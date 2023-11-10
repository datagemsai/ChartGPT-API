# pylint: disable=C0103
# pylint: disable=C0116

import asyncio
import base64
import contextlib
import enum
import functools
import inspect
import json
import pickle
import re
import time
import traceback
from contextlib import redirect_stdout
from io import StringIO
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple, Union
from fastapi.concurrency import run_in_threadpool
import concurrent.futures

import openai
import pandas as pd
# Imports required for `eval` of `output_type` argument to work
import plotly
import plotly.graph_objs as go
# Override Streamlit styling
import plotly.io as pio
from google.api_core.exceptions import InternalServerError
from google.cloud import bigquery
from IPython.core.interactiveshell import ExecutionResult, InteractiveShell
from IPython.utils import io
from plotly.graph_objs import Figure
import tenacity
from typeguard import TypeCheckError, check_type, typechecked
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
from api import errors  # for exponential backoff

from api.models import Attempt, Error, Output, OutputType, Request
import api.utils
from api import log, utils
from api.config import (
    SQL_INITIAL_GPT_MODEL,
    SQL_CORRECTION_GPT_MODEL,
    CODE_INITIAL_GPT_MODEL,
    CODE_CORRECTION_GPT_MODEL,
    DEFAULT_GPT_TEMPERATURE,   
)
from api.connectors.bigquery import bigquery_client
from api.errors import ContextLengthError, PythonExecutionError, SQLValidationError
from api.log import logger
from api.prompts.templates import (
    CODE_GENERATION_ERROR_PROMPT_TEMPLATE,
    CODE_GENERATION_IMPORTS,
    CODE_GENERATION_PROMPT_TEMPLATE,
    SQL_QUERY_GENERATION_ERROR_PROMPT_TEMPLATE,
    SQL_QUERY_GENERATION_PROMPT_TEMPLATE,
    get_relevant_examples,
    convert_examples_to_llm_messages,
)
from api.security.secure_ast import assert_secure_code
from api.types import (  # Request,; Attempt,; Output,; AnyOutputType,
    CodeGenerationConfig, Message, PythonExecutionResult, QueryResult, Role,
    SQLExecutionResult, SQLQueryGenerationConfig, accepted_output_types,
    assert_matches_accepted_type, map_type_to_output_type)
from api.utils import (apply_lower_to_where, clean_jupyter_shell_output,
                       get_tables_summary)

pio.templates.default = "plotly"


function_respond_to_user = {
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
            },
        },
        "required": ["message", "response"],
    },
}


function_validate_sql_query = {
    "name": "validate_sql_query",
    "description": """
    Takes a BigQuery GoogleSQL query, validates and executes it using a dry run, and returns a list of errors, if any.
    """,
    "parameters": {
        "type": "object",
        "properties": {
            "description": {
                "type": "string",
                "description": """
                    The step-by-step description of the GoogleSQL query and Python code you will create
                    and how it will be used to answer the user's analytics question.

                    Use simple language intended for a non-technical user, abstracting the details of the query and code.
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

function_validate_sql_query_without_description = {
    "name": function_validate_sql_query["name"],
    "description": function_validate_sql_query["description"],
    "parameters": {
        "type": "object",
        "properties": {
            "query": function_validate_sql_query["parameters"]["properties"]["query"],
        },
        "required": ["query"],
    },
}

function_execute_python_code = {
    "name": "execute_python_code",
    "description": """
    Takes a Python code string, validates and executes it, and returns a list of errors, if any.
    """,
    "parameters": {
        "type": "object",
        "properties": {
            "docstring": {
                "type": "string",
                "description": """
                    The description for the Python code describing step-by-step how it will be used to answer the user's analytics question.
                
                    Use simple language intended for a non-technical user, abstracting the details of the query and code.                
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

function_execute_python_code_without_docstring = {
    "name": function_execute_python_code["name"],
    "description": function_execute_python_code["description"],
    "parameters": {
        "type": "object",
        "properties": {
            "code": function_execute_python_code["parameters"]["properties"]["code"],
        },
        "required": ["code"],
    },
}


async def execute_in_process(func, *args, **kwargs) -> Any:
    partial_func = functools.partial(func, *args, **kwargs)

    # asyncio.set_event_loop(asyncio.new_event_loop())
    with concurrent.futures.ProcessPoolExecutor() as executor:
        return await asyncio.get_running_loop().run_in_executor(executor, partial_func)


@log.wrap(log.entering, log.exiting)
async def validate_sql_query(query: str) -> List[str]:
    """Takes a BigQuery SQL query, executes it using a dry run, and returns a list of errors, if any"""
    try:
        query_job = await run_in_threadpool(
            bigquery_client.query,
            query,
            job_config=bigquery.QueryJobConfig(dry_run=True)
        )
        errors = (
            [str(err["message"]) for err in query_job.errors]
            if query_job.errors
            else []
        )
        logger.debug(f"BigQuery dry-run job errors: {errors}")
        logger.debug(
            f"BigQuery dry-run job bytes processed: {query_job.total_bytes_processed}"
        )
    except Exception as e:
        errors = [str(e)]
    return errors


@log.wrap(log.entering, log.exiting)
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
def openai_chat_completion_sync(
    model,
    messages,
    max_tokens: Optional[int] = None,
    functions: Optional[List] = None,
    function_call: Optional[Dict] = None,
    temperature: float = DEFAULT_GPT_TEMPERATURE,
):
    try:
        args = []
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        if functions:
            kwargs["functions"] = functions
        if function_call:
            kwargs["function_call"] = function_call
        response = openai.ChatCompletion.create(*args, **kwargs)
        logger.debug("OpenAI ChatCompletion temperature: %s", temperature)
        logger.debug("OpenAI ChatCompletion response usage: %s", response.get('usage'))
        return response
    except openai.InvalidRequestError as exc:
        logger.exception(f"{exc}.\nMessages with length {len(messages)}: {messages}")
        raise exc


@log.wrap(log.entering, log.exiting)
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
async def openai_chat_completion(
    model,
    messages,
    max_tokens: Optional[int] = None,
    functions: Optional[List] = None,
    function_call: Optional[Dict] = None,
    temperature: float = DEFAULT_GPT_TEMPERATURE,
):
    try:
        args = []
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        if functions:
            kwargs["functions"] = functions
        if function_call:
            kwargs["function_call"] = function_call
        response = await openai.ChatCompletion.acreate(*args, **kwargs)
        logger.debug("OpenAI ChatCompletion temperature: %s", temperature)
        logger.debug("OpenAI ChatCompletion response usage: %s", response.get('usage'))
        return response
    except openai.InvalidRequestError as exc:
        logger.exception(f"{exc}.\nMessages with length {len(messages)}: {messages}")
        raise exc


def extract_sql_query_generation_response_data(response):
    choice = response["choices"][0]
    finish_reason = choice["finish_reason"]

    if finish_reason == "length":
        raise ContextLengthError("The LLM context is too long.")

    message = choice["message"]
    function_call = message["function_call"]
    function_name = function_call["name"]

    try:
        if function_name == "respond_to_user":
            return extract_respond_to_user_data(response)
        else:
            raw_function_args = function_call["arguments"]
            function_args = json.loads(
                str(raw_function_args), strict=False
            )
            return message, function_args.get("description"), function_args.get("query")
    except Exception as exc:
        logger.exception("Failed to extract SQL query generation response data from response: %s", response)
        raise SQLValidationError("Failed to extract SQL query generation response data") from exc


@log.wrap(log.entering, log.exiting)
async def get_initial_sql_query(messages) -> Tuple[str, str]:
    response = await openai_chat_completion(
        SQL_INITIAL_GPT_MODEL,
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


@log.wrap(log.entering, log.exiting)
async def generate_valid_sql_query(
    query: str,
    description: str,
    messages: List[dict],
    attempts: List[Attempt] = [],
    config: SQLQueryGenerationConfig = SQLQueryGenerationConfig(),
) -> AsyncGenerator[Union[Attempt, SQLExecutionResult], None]:
    query = apply_lower_to_where(query)
    errors = await validate_sql_query(query=query)
    df = pd.DataFrame()

    if not errors:
        try:
            df = await execute_sql_query(query=query)
            if config.assert_results_not_empty and df.dropna(how="all").empty:
                errors.append("Query returned no results, please try again.")
        except Exception as e:
            errors.append(str(e))

    # TODO If attempts > max_attempts, return an error to the user
    if errors and len(attempts) <= config.max_attempts:
        log_errors_and_attempts(query, errors, attempts, config.max_attempts)

        error_prompt = SQL_QUERY_GENERATION_ERROR_PROMPT_TEMPLATE.format(
            description=description,
            sql_query=query,
            error_messages=errors
        )
        error_correction_messages = [
            # Include system message,
            # exclude extensive examples to improve performance
            messages[0],
            {"role": Role.USER.value, "content": inspect.cleandoc(error_prompt)}
        ]

        corrected_response = await openai_chat_completion(
            SQL_CORRECTION_GPT_MODEL,
            error_correction_messages,
            functions=[
                # function_respond_to_user,
                # function_validate_sql_query,
                function_validate_sql_query_without_description,
            ],
            function_call={"name": "validate_sql_query"},
            # Increase temperature from 0.1 to 0.5 with each attempt
            temperature=0.1 + (len(attempts) / config.max_attempts) * 0.4,
        )
        (
            _,
            _,
            updated_query,
        ) = extract_sql_query_generation_response_data(corrected_response)

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
                    type=SQLValidationError.__name__,
                    value=error,
                )
                for index, error in enumerate(errors)
            ],
        )
        attempts.append(attempt)
        yield attempt
        async for result in generate_valid_sql_query(
            query=updated_query,
            description=description,
            messages=messages,
            attempts=attempts,
            config=config,
        ):
            yield result
    else:
        yield SQLExecutionResult(
            description=description, query=query, dataframe=df, messages=messages
        )


def log_errors_and_attempts(query, errors, attempts, max_attempts):
    logger.debug(f"Query: {query}")
    logger.debug(f"Errors in query: {errors}")
    logger.debug(f"Attempt: {len(attempts)} of {max_attempts}")


@log.wrap(log.entering, log.exiting)
async def execute_sql_query(query: str) -> pd.DataFrame:
    try:
        query_job = await run_in_threadpool(bigquery_client.query, query)
        results = await run_in_threadpool(query_job.result)
        logger.debug(f"BigQuery job bytes billed: {query_job.total_bytes_billed}")
    except InternalServerError as exc:
        # Typically raised when maximum bytes processed limit is exceeded
        logger.error(f"BigQuery InternalServerError for query {query}")
        raise exc
    return results.to_dataframe()


@log.wrap(log.entering, log.exiting)
async def get_valid_sql_query(
    messages: List[Message], config: SQLQueryGenerationConfig
) -> AsyncGenerator[Union[Attempt, SQLExecutionResult], None]:
    initial_description, initial_query = await get_initial_sql_query(messages)
    log_initial_queries(initial_description, initial_query)

    if not config.assert_results_not_empty and not initial_query:
        yield SQLExecutionResult(
            description=initial_description,
            query=initial_query,
            dataframe=pd.DataFrame(),
            messages=messages,
        )
    else:
        async for result in generate_valid_sql_query(
            query=initial_query,
            description=initial_description,
            messages=messages,
            config=config,
        ):
            yield result


def log_initial_queries(description, query):
    logger.debug("Initial SQL query description: %s", description)
    logger.debug("Initial SQL query: %s", query)


def log_final_queries(description, query):
    logger.debug("Final SQL query description: %s", description)
    logger.debug("Valid SQL query: %s", query)


def extract_respond_to_user_data(response):
    message = response["choices"][0]["message"]

    finish_reason = response["choices"][0]["finish_reason"]
    function_args = json.loads(str(message["function_call"]["arguments"]), strict=False)

    if finish_reason == "length":
        raise ContextLengthError

    return message, function_args.get("message"), function_args.get("response")


def extract_code_generation_response_data(response):
    choice = response["choices"][0]
    finish_reason = choice["finish_reason"]

    if finish_reason == "length":
        raise ContextLengthError("The LLM context is too long.")

    message = choice["message"]
    function_call = message["function_call"]
    function_name = function_call["name"]

    try:
        if function_name == "respond_to_user":
            return extract_respond_to_user_data(response)
        else:
            raw_function_args = function_call["arguments"]
            # Replace """ with "
            raw_function_args = raw_function_args.replace('"""', '"')
            function_args = json.loads(
                str(raw_function_args), strict=False
            )
            return message, function_args.get("docstring"), function_args.get("code")
    except Exception as exc:
        logger.exception("Failed to extract code generation response data from response: %s", response)
        raise PythonExecutionError("Failed to extract code generation response data") from exc


def execute_python_imports(imports: str) -> dict:
    try:
        global_variables = {}
        exec(imports, global_variables)
        return global_variables
    except Exception as e:
        logger.error(e)
        return {}


@log.wrap(log.entering, log.exiting)
async def execute_python_code(
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

    df = local_variables.get("df", pd.DataFrame())
    local_variables = local_variables or {}
    result = None
    output = ""

    if imports:
        local_variables.update(execute_python_imports(imports))

    shell = InteractiveShell.instance()
    try:
        try:
            # TODO For now we just log the error to Sentry,
            # but once the app is deployed publicly, we should lock this down
            assert_secure_code(code)
        except Exception:
            pass

        # with io.capture_output() as captured:
        with contextlib.redirect_stdout(StringIO()) as captured_stdout:
            logger.debug("Executing code")
            # Make a copy of the DataFrame to ensure the original is not modified
            shell.push({**local_variables, "df": df.copy()})
            execution_result: ExecutionResult = await shell.run_cell_async(code, store_history=True)
            execution_result.raise_error()

        answer_fn = shell.user_ns.get("answer_question")
        function_result = None
        if callable(answer_fn):
            logger.debug("Found function `answer_question`")
            # with io.capture_output() as captured:
            with contextlib.redirect_stdout(StringIO()) as captured_stdout:
                logger.debug("Calling function `answer_question`")
                # Make a copy of the DataFrame to ensure the original is not modified
                shell.push({**local_variables, "df": df.copy()})
                function_result: ExecutionResult = await shell.run_cell_async("answer_question(df)", store_history=True)
                function_result.raise_error()

        output = clean_jupyter_shell_output(
            captured_stdout.getvalue(), remove_final_result=True
        )

        if function_result and function_result.result is not None:
            result = function_result.result
        elif execution_result.result is not None:
            result = execution_result.result
        elif (
            config.output_variable in shell.user_ns
            and shell.user_ns[config.output_variable] is not None
        ):
            result = shell.user_ns[config.output_variable]
        else:
            result = None

        if result is not None:
            logger.debug("Result: %s", str(result)[:100])
            try:
                # check_type(result, config.output_type)
                assert_matches_accepted_type(result, config.output_types)
            except TypeCheckError as exc:
                message = (
                    f"The code must return a variable of type `{config.output_types}`."
                )
                logger.warning(message)
                raise TypeError(message) from exc
        else:
            message = f"The variable `{config.output_variable}` was not defined, or the function `answer_question` does not exist or does not return a value."
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
        error_msg = f"{type(e).__name__}: {str(e)}" #, in code `{line_data}`"
        error_msg_trace = f"{type(e).__name__}: {str(e)}\nOn line {line_number}, function `{function_name}`, with code `{line_data}`"
        logger.warning(error_msg_trace)
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


@log.wrap(log.entering, log.exiting)
async def get_initial_python_code(messages) -> Tuple[str, str]:
    response = await openai_chat_completion(
        CODE_INITIAL_GPT_MODEL,
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


@log.wrap(log.entering, log.exiting)
async def generate_valid_python_code(
    messages: List[Message],
    local_variables=None,
    config: CodeGenerationConfig = CodeGenerationConfig(),
) -> AsyncGenerator[Union[Attempt, PythonExecutionResult], None]:
    docstring, code = await get_initial_python_code(messages)
    logger.debug("Initial Python code docstring:\n%s", docstring)
    logger.debug("Initial Python code:\n%s", code)

    result: PythonExecutionResult = PythonExecutionResult()
    for attempt_index in range(config.max_attempts):
        local_variables["df"] = local_variables["df"].copy()

        result: PythonExecutionResult = await execute_python_code(
            code=code,
            docstring=docstring,
            imports=CODE_GENERATION_IMPORTS,
            local_variables=local_variables,
            config=config,
        )

        if result.error:
            logger.warning(f"Attempt: {attempt_index + 1} of {config.max_attempts}")
            logger.warning(f"Error in code: {result.error}")
            logger.warning(f"Code:\n{result.code}")

            yield Attempt(
                index=attempt_index,
                created_at=int(time.time()),
                outputs=[
                    Output(
                        index=0,
                        created_at=int(time.time()),
                        description=docstring,
                        type=OutputType.PYTHON_CODE.value,
                        value=result.code,
                    )
                ],
                errors=[
                    Error(
                        index=0,
                        created_at=int(time.time()),
                        type=PythonExecutionError.__name__,
                        value=result.error,
                    )
                ],
            )

            error_prompt = CODE_GENERATION_ERROR_PROMPT_TEMPLATE.format(
                description=docstring,
                code=result.code,
                error_message=result.error
            )

            error_correction_messages = messages + [
                {"role": Role.USER.value, "content": inspect.cleandoc(error_prompt)}
            ]

            response = await openai_chat_completion(
                CODE_CORRECTION_GPT_MODEL,
                error_correction_messages,
                # max_tokens=8000,
                functions=[
                    # TODO Enable agent to respond to user directly
                    # function_respond_to_user,
                    # function_execute_python_code,
                    function_execute_python_code_without_docstring,
                ],
                function_call={"name": "execute_python_code"},
                # Increase temperature from 0.1 to 0.5 with each attempt
                temperature=0.1 + (attempt_index / config.max_attempts) * 0.4,
            )
            _, _, updated_code = extract_code_generation_response_data(
                response
            )

            code_diff = log.get_unified_diff_changes(result.code, updated_code)
            logger.debug("Corrected code diff:\n%s", code_diff)

            # Update code with corrected code
            code = updated_code
        else:
            result.messages = messages
            yield result
            break
    result.messages = messages
    yield result


@log.wrap(log.entering, log.exiting)
async def answer_user_query(
    request: Request,
    stream=False,
) -> AsyncGenerator[Union[Attempt, Output, QueryResult], None]:
    tables_summary = await run_in_threadpool(
        get_tables_summary,
        client=bigquery_client,
        data_source_url=request.data_source_url
    )
    if not tables_summary:
        logger.error(
            "Could not find any tables for data source: %s", request.data_source_url
        )
    else:
        logger.debug("Tables summary: %s", tables_summary.replace("\n", " "))

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

    # user_query = request.messages[-1].content
    # Get all user messages and convert to dict for OpenAI API
    _user_messages = [message.to_dict() for message in request.messages if message.role == Role.USER.value]
    user_messages = [
        {
            **message,
            # Truncate message content to 100 characters
            "content": message["content"][:100] + "..."
            if len(message["content"]) > 100
            else message["content"],
        }
        # Limit to last 3 user messages
        for message in _user_messages[-3:]
    ]
    
    examples = get_relevant_examples(
        query=user_messages[-1]["content"],
        data_source_url=request.data_source_url,
    )
    example_messages_without_sql = convert_examples_to_llm_messages(
        examples,
        include_sql_query=False
    )
    example_messages_without_code = convert_examples_to_llm_messages(
        examples,
        include_code=False
    )

    messages = (
        [{"role": Role.SYSTEM.value, "content": inspect.cleandoc(sql_query_generation_prompt)}]
        + example_messages_without_code
        + user_messages
    )

    sql_query_attempts = []
    async for result in get_valid_sql_query(
        messages=messages,
        config=SQLQueryGenerationConfig(
            data_source_url=request.data_source_url,
            assert_results_not_empty=True,
        ),
    ):
        if isinstance(result, Attempt):
            sql_query_attempts.append(result)
            if stream:
                yield result
        elif isinstance(result, SQLExecutionResult):
            sql_generation_result: SQLExecutionResult = result
        else:
            raise ValueError("Invalid SQL execution result type")

    df = sql_generation_result.dataframe
    log_final_queries(sql_generation_result.description, sql_generation_result.query)

    # Convert Period dtype to timestamp to ensure DataFrame is JSON serializable
    # NOTE: This is now handled by the `to_json` method's `default_handler` argument
    # df = utils.convert_period_dtype_to_timestamp(df)
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
        value=pd.concat([df.head(5), df.tail(5)]).to_json(
            orient="records", default_handler=str
        ),
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
        output_types = accepted_output_types
        output_description = "A list of any type of object or `None`."
        output_variable = "result_list"
    elif request.output_type == OutputType.PLOTLY_CHART.value:
        function_parameters = "df: pd.DataFrame"
        function_description = (
            "Function to analyze the data and return a Plotly chart."
        )
        output_types = [plotly.graph_objs.Figure]
        output_description = "A Plotly figure object."
        output_variable = "fig"
    elif request.output_type == "optional_chart":
        function_parameters = "df: pd.DataFrame"
        function_description = (
            "Function to analyze the data and optionally return a Plotly chart."
        )
        output_types = [Optional[plotly.graph_objs.Figure]]
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
        dataframe_columns=json.dumps(list(df.columns), indent=4, sort_keys=True),
        dataframe_schema=json.dumps(df_summary, indent=4, sort_keys=True),
        imports=CODE_GENERATION_IMPORTS,
        function_parameters=function_parameters,
        function_description=function_description,
        output_type=utils.create_type_string(output_types),
        output_description=output_description,
        output_variable=output_variable,
    )

    code_generation_messages = (
        [{"role": Role.SYSTEM.value, "content": inspect.cleandoc(code_generation_prompt)}]
        + example_messages_without_sql
        + user_messages
    )

    python_execution_attempts = []
    async for result in generate_valid_python_code(
        messages=code_generation_messages,
        local_variables={"df": df},
        config=CodeGenerationConfig(
            output_types=output_types,
            output_variable=output_variable,
        ),
    ):
        if isinstance(result, Attempt):
            python_execution_attempts.append(result)
            if stream:
                yield result
        elif isinstance(result, PythonExecutionResult):
            code_generation_result: PythonExecutionResult = result
            if code_generation_result.error:
                logger.error("Failed to generate valid Python code: %s", code_generation_result.error)
                raise PythonExecutionError(code_generation_result.error)
        else:
            raise ValueError("Invalid Python execution result type")

    logger.debug("Valid Python code:\n%s", code_generation_result.code)

    Figure.show = original_show_method

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

    if code_generation_result.result is None:
        code_generation_results = []
    elif not isinstance(code_generation_result.result, list):
        code_generation_results = [code_generation_result.result]
    else:
        code_generation_results = code_generation_result.result

    def process_result(item, index, created_at, output_description):
        _type: OutputType = map_type_to_output_type(item)

        if _type == OutputType.PLOTLY_CHART:
            _output = json.dumps(item, cls=utils.CustomPlotlyJSONEncoder)
        elif _type == OutputType.PANDAS_DATAFRAME:
            # If the dataframe is larger than X rows, only return the first X rows
            n = 20
            if len(item) > n:
                item = item.iloc[:n]
            item = item.reset_index()
            _output = item.to_json(orient="records", default_handler=str)
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
        final_errors = (
            [
                Error(
                    index=0,
                    created_at=created_at,
                    type=PythonExecutionError.__name__,
                    value=code_generation_result.error,
                )
            ]
            if code_generation_result.error
            else []
        )
        yield QueryResult(
            data_source="",
            output_type=request.output_type,
            attempts=sql_query_attempts + python_execution_attempts,
            errors=final_errors,
            outputs=outputs,
        )
