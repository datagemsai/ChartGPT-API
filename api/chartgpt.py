# pylint: disable=C0103
# pylint: disable=C0116

import base64
import enum
import inspect
import json
import pickle
import re
import time
import traceback
from contextlib import redirect_stdout
from io import StringIO
from typing import Any, Iterator, List, Optional, Tuple, Union

import openai
import pandas as pd
# Imports required for `eval` of `output_type` argument to work
import plotly
import plotly.graph_objs as go
# Override Streamlit styling
import plotly.io as pio
from chartgpt_client import Request, Attempt, Error, Output, OutputType
from google.cloud import bigquery
from IPython.core.interactiveshell import ExecutionResult, InteractiveShell
from IPython.utils import io
from plotly.graph_objs import Figure
from typeguard import TypeCheckError, check_type, typechecked
from google.api_core.exceptions import InternalServerError
from api import utils

from api.config import GPT_TEMPERATURE, PYTHON_GPT_MODEL, SQL_GPT_MODEL
from api.connectors.bigquery import bigquery_client
from api.errors import ContextLengthError
from api.prompts import (CODE_GENERATION_ERROR_PROMPT_TEMPLATE,
                         CODE_GENERATION_IMPORTS,
                         CODE_GENERATION_PROMPT_TEMPLATE,
                         SQL_QUERY_GENERATION_ERROR_PROMPT_TEMPLATE,
                         SQL_QUERY_GENERATION_PROMPT_TEMPLATE)
from api.types import (  # Request,; Attempt,; Output,; AnyOutputType,
    CodeGenerationConfig, PythonExecutionResult, QueryResult,
    SQLExecutionResult, SQLQueryGenerationConfig, accepted_output_types,
    assert_matches_accepted_type, map_type_to_output_type,
    Role, Message
)
from api.utils import apply_lower_to_where, get_tables_summary, clean_jupyter_shell_output
from api.security.secure_ast import assert_secure_code
from api.logging import logger

pio.templates.default = "plotly"


function_respond_to_user =     {
    "name": "respond_to_user",
    "description": """
    Takes a message and responds to the user.
    """,
    "parameters": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "The message to respond to",
            },
            "response": {
                "type": "string",
                "description": "The response to the user's message",
            }
        },
        "required": ["message", "response"],
    },
}

function_validate_sql_query = {
    "name": "validate_sql_query",
    "description": """
    Takes a BigQuery GoogleSQL query, executes it using a dry run, and returns a list of errors, if any.
    """,
    "parameters": {
        "type": "object",
        "properties": {
            "description": {
                "type": "string",
                "description": """
                    The step-by-step description of the GoogleSQL query and Python code you will create
                    and how it will be used to answer the user's analytics question.
                """,
            },
            "query": {
                "type": "string",
                "description": "The GoogleSQL query to validate",
            },
        },
        "required": ["description", "query"],
    },
}

function_execute_python_code = {
    "name": "execute_python_code",
    "description": """
    Takes a Python code string, executes it, and returns an instance of PythonExecutionResult.
    """,
    "parameters": {
        "type": "object",
        "properties": {
            "docstring": {
                "type": "string",
                "description": """
                    The docstring for the Python code describing step-by-step how it will be used to answer the user's analytics question.
                """,
            },
            "code": {
                "type": "string",
                "description": "The Python code to execute",
            },
        },
        "required": ["docstring", "code"],
    },
}


def validate_sql_query(query: str) -> List[str]:
    """Takes a BigQuery SQL query, executes it using a dry run, and returns a list of errors, if any"""
    try:
        query_job = bigquery_client.query(
            query, job_config=bigquery.QueryJobConfig(dry_run=True)
        )
        errors = (
            [str(err["message"]) for err in query_job.errors]
            if query_job.errors
            else []
        )
        logger.debug(f"BigQuery dry-run job errors: {errors}")
        logger.debug(f"BigQuery dry-run job bytes processed: {query_job.total_bytes_processed}")
    except Exception as e:
        errors = [str(e)]
    return errors


def openai_chat_completion(model, messages, functions, function_call):
    return openai.ChatCompletion.create(
        model=model,
        messages=messages,
        functions=functions,
        function_call=function_call,
        temperature=GPT_TEMPERATURE,
    )


def extract_sql_query_generation_response_data(response):
    message = response["choices"][0]["message"]
    function_name = message["function_call"]["name"]

    if function_name == "respond_to_user":
        return extract_respond_to_user_data(response)
    else:
        finish_reason = response["choices"][0]["finish_reason"]
        function_args = json.loads(str(message["function_call"]["arguments"]), strict=False)

        if finish_reason == "length":
            raise ContextLengthError

        return message, function_args.get("description"), function_args.get("query")


def get_initial_sql_query(messages) -> Tuple[str, str]:
    response = openai_chat_completion(
        SQL_GPT_MODEL,
        messages,
        functions=[
            # TODO Enable agent to respond to user directly
            # function_respond_to_user,
            function_validate_sql_query,
        ],
        function_call={"name": "validate_sql_query"},
    )
    _, description, query = extract_sql_query_generation_response_data(response)
    return description, query


def generate_valid_sql_query(
    query: str,
    description: str,
    messages: List[dict],
    attempts: List[Attempt] = [],
    config: SQLQueryGenerationConfig = SQLQueryGenerationConfig(),
) -> Iterator[Union[Attempt, SQLExecutionResult]]:
    query = apply_lower_to_where(query)
    errors = validate_sql_query(query=query)
    df = pd.DataFrame()

    if not errors:
        try:
            df = execute_sql_query(query=query)
            if config.assert_results_not_empty and df.dropna(how="all").empty:
                errors.append("Query returned no results, please try again.")
        except Exception as e:
            errors.append(str(e))

    if errors and len(attempts) <= config.max_attempts:
        log_errors_and_attempts(query, errors, attempts, config.max_attempts)

        messages.append(
            {
                "role": Role.FUNCTION.value,
                "name": "validate_sql_query",
                "content": inspect.cleandoc(
                    SQL_QUERY_GENERATION_ERROR_PROMPT_TEMPLATE.format(errors=errors)
                ),
            }
        )

        corrected_response = openai_chat_completion(
            SQL_GPT_MODEL,
            messages,
            functions=[
                # function_respond_to_user,
                function_validate_sql_query
            ],
            function_call={"name": "validate_sql_query"},
        )
        (
            message,
            updated_description,
            updated_query,
        ) = extract_sql_query_generation_response_data(corrected_response)

        messages.append(message)

        created_at = int(time.time())
        attempt = Attempt(
            index=len(attempts),
            created_at=created_at,
            outputs=[
                Output(
                    index=0,
                    created_at=created_at,
                    description=description,
                    type=OutputType.SQL_QUERY.value,
                    value=query,
                )
            ],
            errors=[
                Error(
                    index=index,
                    created_at=created_at,
                    type="SQLValidationError",
                    value=error,
                ) for index, error in enumerate(errors)
            ]
        )
        attempts.append(attempt)
        yield attempt
        yield from generate_valid_sql_query(
            query=updated_query,
            description=updated_description,
            messages=messages,
            attempts=attempts,
            config=config
        )
    else:
        yield SQLExecutionResult(
            description=description,
            query=query,
            dataframe=df,
            messages=messages
        )


def log_errors_and_attempts(query, errors, attempts, max_attempts):
    logger.debug(f"Query: {query}")
    logger.debug(f"Errors in query: {errors}")
    logger.debug(f"Attempt: {len(attempts)} of {max_attempts}")


def execute_sql_query(query: str) -> pd.DataFrame:
    try:
        query_job = bigquery_client.query(query)
        results = query_job.result()
        logger.debug(f"BigQuery job bytes billed: {query_job.total_bytes_billed}")
    except InternalServerError as exc:
        # Typically raised when maximum bytes processed limit is exceeded
        logger.error(f"BigQuery InternalServerError for query {query}")
        raise exc
    return results.to_dataframe()


def get_valid_sql_query(
    messages: List[Message],
    config: SQLQueryGenerationConfig
) -> Iterator[Union[Attempt, SQLExecutionResult]]:
    initial_description, initial_query = get_initial_sql_query(messages)
    log_initial_queries(initial_description, initial_query)

    if not config.assert_results_not_empty and not initial_query:
        yield SQLExecutionResult(
            description=initial_description,
            query=initial_query,
            dataframe=pd.DataFrame(),
            messages=messages,
        )
    else:
        yield from generate_valid_sql_query(
            query=initial_query,
            description=initial_description,
            messages=messages,
            config=config,
        )


def log_initial_queries(description, query):
    logger.debug(f"Initial SQL query description: {description}")
    logger.debug(f"Initial SQL query: {query}")


def log_final_queries(description, query):
    logger.debug(f"Final SQL query description: {description}")
    logger.debug(f"Valid SQL query: {query}")


def extract_respond_to_user_data(response):
    message = response["choices"][0]["message"]

    finish_reason = response["choices"][0]["finish_reason"]
    function_args = json.loads(str(message["function_call"]["arguments"]), strict=False)

    if finish_reason == "length":
        raise ContextLengthError

    return message, function_args.get("message"), function_args.get("response")


def extract_code_generation_response_data(response):
    message = response["choices"][0]["message"]
    function_name = message["function_call"]["name"]

    if function_name == "respond_to_user":
        return extract_respond_to_user_data(response)
    else:
        finish_reason = response["choices"][0]["finish_reason"]
        function_args = json.loads(str(message["function_call"]["arguments"]), strict=False)

        if finish_reason == "length":
            raise ContextLengthError

        return message, function_args.get("docstring"), function_args.get("code")


def execute_python_imports(imports: str) -> dict:
    try:
        global_variables = {}
        exec(imports, global_variables)
        return global_variables
    except Exception as e:
        logger.error(e)
        return {}


def execute_python_code(
    code: str,
    docstring: str,
    imports=None,
    local_variables=None,
    config: CodeGenerationConfig = CodeGenerationConfig(),
) -> PythonExecutionResult:
    if not code:
        error_msg = "No code provided"
        logger.warning(error_msg)
        return PythonExecutionResult(
            description=docstring,
            code=code,
            result=None,
            local_variables=local_variables,
            error=error_msg,
        )

    local_variables = local_variables.copy() if local_variables else {}
    result = None
    output = ""

    if imports:
        local_variables.update(execute_python_imports(imports))

    shell = InteractiveShell.instance()
    try:
        # Assert that the code is secure
        assert_secure_code(code)

        shell.push(local_variables)

        with io.capture_output() as captured:
            logger.debug("Executing code")
            execution_result: ExecutionResult = shell.run_cell(code, store_history=True)
            execution_result.raise_error()

        answer_fn = shell.user_ns.get("answer_question")
        function_result = None
        if callable(answer_fn):
            logger.debug("Found function `answer_question`")
            with io.capture_output() as captured:
                logger.debug("Calling function `answer_question`")
                function_result: ExecutionResult = shell.run_cell(
                    "answer_question(df.copy())", store_history=True
                )
                function_result.raise_error()

        output = clean_jupyter_shell_output(captured.stdout, remove_final_result=True)

        if function_result and function_result.result is not None:
            result = function_result.result
        elif execution_result.result is not None:
            result = execution_result.result
        elif config.output_variable in shell.user_ns and shell.user_ns[config.output_variable] is not None:
            result = shell.user_ns[config.output_variable]
        else:
            result = None

        if result is not None:
            logger.debug(f"Result: {str(result)[:100]}")
            try:
                # check_type(result, config.output_type)
                assert_matches_accepted_type(result, config.output_type)
            except TypeCheckError as exc:
                message = f"The code must return a variable of type `{config.output_type}`."
                logger.warning(message)
                raise TypeError(message) from exc
        else:
            message = f"The variable `{config.output_variable}` or function `answer_question` was not found."
            logger.warning(message)
            raise ValueError(message)
        return PythonExecutionResult(
            description=docstring,
            code=code,
            result=result,
            local_variables=local_variables,
            io=output,
            error=None,
        )
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        _, line_number, function_name, line_data = tb[-1]
        error_msg = f"{type(e).__name__}: {str(e)}\nOn line {line_number}, function `{function_name}`, with code `{line_data}`"
        logger.warning(error_msg)
        return PythonExecutionResult(
            description=docstring,
            code=code,
            result=None,
            local_variables=local_variables,
            io=output,
            error=error_msg,
        )
    finally:
        shell.clear_instance()


def get_initial_python_code(messages) -> Tuple[str, str]:
    response = openai_chat_completion(
        PYTHON_GPT_MODEL,
        messages,
        functions=[
            # TODO Enable agent to respond to user directly
            # function_respond_to_user,
            function_execute_python_code
        ],
        function_call={"name": "execute_python_code"},
    )
    _, docstring, code = extract_code_generation_response_data(response)
    return docstring, code


def generate_valid_python_code(
    messages: List[Message],
    local_variables=None,
    config: CodeGenerationConfig = CodeGenerationConfig(),
) -> Iterator[Union[Attempt, PythonExecutionResult]]:
    docstring, code = get_initial_python_code(messages)
    logger.debug(f"Initial Python code docstring:\n{docstring}")
    logger.debug(f"Initial Python code:\n{code}")

    result: PythonExecutionResult = PythonExecutionResult()
    for attempt_index in range(config.max_attempts):
        local_variables["df"] = local_variables["df"].copy()

        result: PythonExecutionResult = execute_python_code(
            code=code,
            docstring=docstring,
            imports=CODE_GENERATION_IMPORTS,
            local_variables=local_variables,
            config=config,
        )

        if result.error:
            logger.warning(f"Attempt: {attempt_index + 1} of {config.max_attempts}")
            logger.warning(f"Error in code: {result.error}")
            logger.warning(f"Code:\n{code}")
            
            yield Attempt(
                index=attempt_index,
                created_at=int(time.time()),
                outputs=[
                    Output(
                        index=0,
                        created_at=int(time.time()),
                        description=docstring,
                        type=OutputType.PYTHON_CODE.value,
                        value=code,
                    )
                ],
                errors=[
                    Error(
                        index=0,
                        created_at=int(time.time()),
                        type="PythonExecutionError",
                        value=result.error,
                    )
                ],
            )

            error_prompt = CODE_GENERATION_ERROR_PROMPT_TEMPLATE.format(
                attempt=attempt_index + 1, code=code, error_message=result.error
            )
            messages.append({"role": "user", "content": inspect.cleandoc(error_prompt)})
            response = openai_chat_completion(
                PYTHON_GPT_MODEL,
                messages,
                functions=[
                    # TODO Enable agent to respond to user directly
                    # function_respond_to_user,
                    function_execute_python_code
                ],
                function_call={"name": "execute_python_code"},
            )
            _, docstring, code = extract_code_generation_response_data(response)
        else:
            result.messages = messages
            yield result
            break
    result.messages = messages
    yield result


def answer_user_query(
    request: Request,
    stream=False,
) -> Iterator[Union[Attempt, Output, QueryResult]]:  # When streaming, returns partial Output
    logger.debug(request)

    tables_summary = get_tables_summary(
        client=bigquery_client,
        data_source_url=request.data_source_url,
    )
    if not tables_summary:
        logger.error("Could not find any tables for data source: %s", request.data_source_url)
    else:
        logger.debug(f"Tables summary: {tables_summary}")

    sql_query_generation_prompt = SQL_QUERY_GENERATION_PROMPT_TEMPLATE.format(
        sql_query_instruction=(
            "Develop a step-by-step plan and write a GoogleSQL query compatible with BigQuery",
            "to fetch the data necessary for your analysis and visualization.",
        ),
        python_code_instruction=(
            "Implement Python code to analyze the data using Pandas and visualize the findings using Plotly."
        ),
        database_schema=str(tables_summary),
    )

    user_query = request.messages[-1].content
    input_messages_raw = [message.to_dict() for message in request.messages[:-1]]
    input_messages = [
        {
            **message, "content": message["content"][:100] + "..."
            if len(message["content"]) > 100
            else message["content"]
        }
        for message in input_messages_raw[:-1]
    ]
    messages = input_messages + [
        {
            "role": Role.SYSTEM.value,
            "content": inspect.cleandoc(sql_query_generation_prompt)
        },
        {
            "role": Role.USER.value,
            "content": "Analytics question: " + user_query
        },
    ]

    sql_query_attempts = []
    for result in get_valid_sql_query(
        messages=messages,
        config=SQLQueryGenerationConfig(
            data_source_url=request.data_source_url,
            assert_results_not_empty=False,
        ),
    ):
        if isinstance(result, Attempt):
            sql_query_attempts.append(result)
            print("Attempt:", result)
            if stream:
                yield result
        elif isinstance(result, SQLExecutionResult):
            sql_generation_result: SQLExecutionResult = result
        else:
            raise ValueError("Invalid SQL execution result type")

    df = sql_generation_result.dataframe
    log_final_queries(sql_generation_result.description, sql_generation_result.query)

    # Convert Period dtype to timestamp to ensure DataFrame is JSON serializable
    df = df.astype(
        {
            col: "datetime64[ns]"
            for col in df.columns
            if pd.api.types.is_period_dtype(df[col])
        }
    )
    # Sort DataFrame by date column if it exists
    df = utils.sort_dataframe(df)

    outputs = []
    output_0 = Output(
        index=0,
        created_at=int(time.time()),
        description=sql_generation_result.description,
        type=OutputType.SQL_QUERY.value,
        value=str(sql_generation_result.query),
    )
    output_1 = Output(
        index=1,
        created_at=int(time.time()),
        description="Table sample rows",
        type=OutputType.PANDAS_DATAFRAME.value,
        # value=base64.b64encode(pickle.dumps(df)).decode("utf-8"),
        value=pd.concat([df.head(5), df.tail(5)]).to_json(orient='records'),
    )

    if stream:
        yield QueryResult(
            data_source=request.data_source_url,
            output_type=request.output_type,
            attempts=sql_query_attempts,
            errors=[],
            outputs=[output_0],
        )
        yield output_1
    else:
        outputs += [output_0, output_1]

    try:
        df_summary = utils.get_dataframe_summary(df)
    except IndexError:
        df_summary = "DataFrame is empty"

    if request.output_type == OutputType.ANY.value:
        function_parameters = "df: pd.DataFrame"
        function_description = "Function to analyze the data and optionally return a list of results `result_list` or `None`."
        output_type = accepted_output_types
        # output_type = Any
        output_description = "A list of any type of object or `None`."
        output_variable = "result_list"
    elif request.output_type == OutputType.PLOTLY_CHART.value:
        function_parameters = "df: pd.DataFrame"
        function_description = (
            # "Function to analyze the data and return a list of Plotly charts."
            "Function to analyze the data and return a Plotly chart."
        )
        output_type = [plotly.graph_objs.Figure]
        output_description = "A Plotly figure object."
        output_variable = "fig"
    elif request.output_type == "optional_chart":
        function_parameters = "df: pd.DataFrame"
        function_description = (
            "Function to analyze the data and optionally return a Plotly chart."
        )
        output_type = [Optional[plotly.graph_objs.Figure]]
        output_description = "A Plotly figure object or None."
        output_variable = "fig"
    else:
        raise ValueError("Invalid output type requested")

    def no_show(*args, **kwargs):
        pass

    original_show_method = Figure.show
    Figure.show = no_show

    code_generation_prompt = CODE_GENERATION_PROMPT_TEMPLATE.format(
        sql_description=sql_generation_result.description,
        sql_query=sql_generation_result.query,
        dataframe_schema=json.dumps(df_summary, indent=4, sort_keys=True),
        imports=CODE_GENERATION_IMPORTS,
        function_parameters=function_parameters,
        function_description=function_description,
        output_type=output_type,
        output_description=output_description,
        output_variable=output_variable,
    )

    sql_generation_result.messages += [
        {
            "role": Role.SYSTEM.value,
            "content": inspect.cleandoc(code_generation_prompt),
        },
        {
            "role": Role.USER.value,
            "content": user_query
        },
    ]

    python_execution_attempts = []
    for result in generate_valid_python_code(
        messages=sql_generation_result.messages,
        local_variables={"df": df.copy()},
        config=CodeGenerationConfig(
            output_type=output_type,
            output_variable=output_variable,
        ),
    ):
        if isinstance(result, Attempt):
            python_execution_attempts.append(result)
            if stream:
                yield result
        elif isinstance(result, PythonExecutionResult):
            code_generation_result: PythonExecutionResult = result
        else:
            raise ValueError("Invalid Python execution result type")

    logger.debug(f"Valid Python code:\n{code_generation_result.code}")

    Figure.show = original_show_method

    logger.debug(f"Final error: {code_generation_result.error}")

    created_at = int(time.time())

    output_2 = Output(
        index=2,
        created_at=created_at,
        description=code_generation_result.description,
        type=OutputType.PYTHON_CODE.value,
        value=str(code_generation_result.code),
    )
    output_3 = Output(
        index=3,
        created_at=created_at,
        description="",
        type=OutputType.PYTHON_OUTPUT.value,
        value=code_generation_result.io,
    )

    if stream:
        yield QueryResult(
            data_source=request.data_source_url,
            output_type=request.output_type,
            attempts=python_execution_attempts,
            errors=[],
            outputs=[output_2],
        )
        yield output_3
    else:
        outputs += [output_2, output_3]

    if not code_generation_result.result:
        code_generation_results = []
    elif not isinstance(code_generation_result.result, list):
        code_generation_results = [code_generation_result.result]
    else:
        code_generation_results = code_generation_result.result

    def process_result(item, index, created_at, output_description):
        _type: OutputType = map_type_to_output_type(item)

        if _type == OutputType.PLOTLY_CHART:
            _output = item.to_json()
        elif _type == OutputType.PANDAS_DATAFRAME:
            n = 5
            # Determine the start index for the tail slice
            tail_start = max(n, len(df) - n)
            result = pd.concat([df.iloc[:n], df.iloc[tail_start:]])
            _output = result.to_json(orient='records')
        else:
            _output = str(item)

        output = Output(
            index=index,
            created_at=created_at,
            description=output_description,
            type=_type.value,
            value=_output,
        )

        return output

    for index, result in enumerate(code_generation_results):
        items_to_process = []

        # Depending on the type of result, prepare a list of items to be processed
        if isinstance(result, (list, tuple)):
            items_to_process.extend(result)
        elif isinstance(result, dict):
            items_to_process.extend(result.values())
        else:
            items_to_process.append(result)

        for item in items_to_process:
            output = process_result(item, index + 4, created_at, output_description)
            
            if stream:
                yield output
            else:
                outputs.append(output)

    if not stream:
        yield QueryResult(
            data_source="",
            output_type=request.output_type,
            attempts=sql_query_attempts + python_execution_attempts,
            errors=[],
            outputs=outputs,
        )
