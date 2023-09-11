# pylint: disable=C0103
# pylint: disable=C0116

import base64
import inspect
import json
import pickle
import time
import traceback
from contextlib import redirect_stdout
from io import StringIO
from typing import Any, List, Optional, Tuple, Union

import openai
import pandas as pd
# Imports required for `eval` of `output_type` argument to work
import plotly
import plotly.graph_objs as go
# Override Streamlit styling
import plotly.io as pio
from chartgpt_client import ApiRequestAskChartgptRequest as Request
from chartgpt_client import Attempt, Output, OutputType
from google.cloud import bigquery
from IPython.core.interactiveshell import ExecutionResult, InteractiveShell
from IPython.utils import io
from plotly.graph_objs import Figure
from typeguard import TypeCheckError, check_type, typechecked

from api.config import GPT_TEMPERATURE, PYTHON_GPT_MODEL, SQL_GPT_MODEL
from api.errors import ContextLengthError
from api.prompts import (CODE_GENERATION_ERROR_PROMPT_TEMPLATE,
                         CODE_GENERATION_IMPORTS,
                         CODE_GENERATION_PROMPT_TEMPLATE,
                         SQL_QUERY_GENERATION_ERROR_PROMPT_TEMPLATE,
                         SQL_QUERY_GENERATION_PROMPT_TEMPLATE)
from api.types import (  # Request,; Attempt,; Output,; AnyOutputType,
    CodeGenerationConfig, PythonExecutionResult, QueryResult,
    SQLExecutionResult, SQLQueryGenerationConfig, accepted_output_types,
    assert_matches_accepted_type, map_type_to_output_type)
from api.utils import apply_lower_to_where, get_tables_summary
from chartgpt.app import client
from chartgpt.tools.python.secure_ast import assert_secure_code

pio.templates.default = "plotly"


functions = [
    {
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
    },
    {
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
    },
]


def validate_sql_query(query: str) -> List[str]:
    """Takes a BigQuery SQL query, executes it using a dry run, and returns a list of errors, if any"""
    try:
        query_job = client.query(
            query, job_config=bigquery.QueryJobConfig(dry_run=True)
        )
        errors = (
            [str(err["message"]) for err in query_job.errors]
            if query_job.errors
            else []
        )
    except Exception as e:
        errors = [str(e)]
    return errors


def openai_chat_completion(model, messages, function_name):
    return openai.ChatCompletion.create(
        model=model,
        messages=messages,
        functions=functions,
        function_call={"name": function_name},
        temperature=GPT_TEMPERATURE,
    )


def extract_sql_query_generation_response_data(response):
    message = response["choices"][0]["message"]
    finish_reason = response["choices"][0]["finish_reason"]
    function_args = json.loads(str(message["function_call"]["arguments"]), strict=False)

    if finish_reason == "length":
        raise ContextLengthError

    return message, function_args.get("description"), function_args.get("query")


def get_initial_sql_query(messages) -> Tuple[str, str]:
    response = openai_chat_completion(SQL_GPT_MODEL, messages, "validate_sql_query")
    _, description, query = extract_sql_query_generation_response_data(response)
    return description, query


def generate_valid_sql_query(
    query: str,
    description: str,
    messages: List[dict],
    attempts: int = 0,
    config: SQLQueryGenerationConfig = SQLQueryGenerationConfig(),
) -> SQLExecutionResult:
    query = apply_lower_to_where(query)
    errors = validate_sql_query(query=query)

    if not errors:
        try:
            df = execute_sql_query(query=query)
            if config.assert_results_not_empty and df.dropna(how="all").empty:
                errors.append("Query returned no results, please try again.")
        except Exception as e:
            errors.append(str(e))

    if errors and attempts < config.max_attempts:
        print_errors_and_attempts(query, errors, attempts, config.max_attempts)

        messages.append(
            {
                "role": "function",
                "name": "validate_sql_query",
                "content": inspect.cleandoc(
                    SQL_QUERY_GENERATION_ERROR_PROMPT_TEMPLATE.format(errors=errors)
                ),
            }
        )

        corrected_response = openai_chat_completion(
            PYTHON_GPT_MODEL, messages, "validate_sql_query"
        )
        (
            message,
            updated_description,
            updated_query,
        ) = extract_sql_query_generation_response_data(corrected_response)

        messages.append(message)

        return generate_valid_sql_query(
            updated_query, updated_description, messages, attempts + 1, config
        )
    else:
        return SQLExecutionResult(description=description, query=query, dataframe=df)


def print_errors_and_attempts(query, errors, attempts, max_attempts):
    print(f"Query:\n{query}")
    print(f"Errors in query: {errors}")
    print(f"Attempt: {attempts} of {max_attempts}")


def execute_sql_query(query: str) -> pd.DataFrame:
    query_job = client.query(query)
    results = query_job.result()
    return results.to_dataframe()


def get_valid_sql_query(
    user_query: str, config: SQLQueryGenerationConfig
) -> SQLExecutionResult:
    tables_summary = get_tables_summary(
        client=client,
        data_source_url=config.data_source_url,
    )
    print("Tables summary:", tables_summary)

    sql_query_generation_prompt = SQL_QUERY_GENERATION_PROMPT_TEMPLATE.format(
        sql_query_instruction=(
            "Develop a step-by-step plan and write a GoogleSQL query compatible with BigQuery",
            "to fetch the data necessary for your analysis and visualization.",
            # "Use Python Pandas functions rather than GoogleSQL queries wherever possible.",
        ),
        python_code_instruction=(
            "Implement Python code to analyze the data using Pandas and visualize the findings using Plotly."
        ),
        database_schema=str(tables_summary),
    )

    messages = [
        {"role": "system", "content": inspect.cleandoc(sql_query_generation_prompt)},
        {"role": "user", "content": "Analytics question: " + user_query},
    ]

    initial_description, initial_query = get_initial_sql_query(messages)
    print_initial_queries(initial_description, initial_query)

    if not config.assert_results_not_empty and not initial_query:
        return SQLExecutionResult(
            description=initial_description,
            query=initial_query,
            dataframe=pd.DataFrame(),
        )
    else:
        return generate_valid_sql_query(
            initial_query,
            initial_description,
            messages,
            config=config,
        )


def print_initial_queries(description, query):
    print(f"Initial SQL query description:\n{description}")
    print(f"Initial SQL query:\n{query}")


def print_final_queries(description, query):
    print(f"Final SQL query description:\n{description}")
    print(f"Valid SQL query:\n{query}")


def extract_code_generation_response_data(response):
    message = response["choices"][0]["message"]
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
        print(e)
        return {}


def execute_python_code(
    code: str,
    docstring: str,
    imports=None,
    local_variables=None,
    config: CodeGenerationConfig = CodeGenerationConfig(),
) -> PythonExecutionResult:
    if not code:
        raise ValueError("No code provided")

    local_variables = local_variables.copy() if local_variables else {}
    result = None
    output = ""

    if imports:
        local_variables.update(execute_python_imports(imports))

    try:
        # Assert that the code is secure
        assert_secure_code(code)

        shell = InteractiveShell.instance()
        shell.push(local_variables)

        with io.capture_output() as captured:
            r: ExecutionResult = shell.run_cell(code, store_history=True)
            r.raise_error()

        answer_fn = shell.user_ns.get("answer_question")

        if callable(answer_fn):
            with io.capture_output() as captured:
                r: ExecutionResult = shell.run_cell(
                    "answer_question(df.copy())", store_history=True
                )
                r.raise_error()

        output = captured.stdout
        result = r.result

        if result:
            try:
                # check_type(result, config.output_type)
                assert_matches_accepted_type(result, config.output_type)
            except TypeCheckError as exc:
                raise TypeError(
                    f"The `answer_question` function must return a variable of type `{config.output_type}`."
                ) from exc
        else:
            raise ValueError(
                f"The variable `{config.output_variable}` or function `answer_question` was not found."
            )
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
    response = openai_chat_completion(PYTHON_GPT_MODEL, messages, "execute_python_code")
    _, docstring, code = extract_code_generation_response_data(response)
    return docstring, code


def generate_valid_python_code(
    user_query: str,
    code_generation_prompt: str,
    local_variables=None,
    config: CodeGenerationConfig = CodeGenerationConfig(),
) -> PythonExecutionResult:
    messages = [
        {
            "role": "system",
            "content": inspect.cleandoc(code_generation_prompt),
        },
        {"role": "user", "content": user_query},
    ]

    docstring, code = get_initial_python_code(messages)
    print(f"Initial Python code docstring:\n{docstring}")
    print(f"Initial Python code:\n{code}")

    result: PythonExecutionResult = PythonExecutionResult()
    for attempt in range(config.max_attempts):
        local_variables["df"] = local_variables["df"].copy()

        result: PythonExecutionResult = execute_python_code(
            code,
            docstring,
            CODE_GENERATION_IMPORTS,
            local_variables,
            config=config,
        )

        if result.error:
            print(f"Attempt: {attempt + 1} of {config.max_attempts}")
            print(f"Error in code: {result.error}")
            print(f"Code:\n{code}")
            print("\n")
            error_prompt = CODE_GENERATION_ERROR_PROMPT_TEMPLATE.format(
                attempt=attempt + 1, code=code, error_message=result.error
            )
            messages.append({"role": "user", "content": inspect.cleandoc(error_prompt)})
            response = openai_chat_completion(
                PYTHON_GPT_MODEL, messages, "execute_python_code"
            )
            _, docstring, code = extract_code_generation_response_data(response)
        else:
            return result
    return result


def answer_user_query(
    request: Request,
) -> QueryResult:
    print(request)
    sql_generation_result: SQLExecutionResult = get_valid_sql_query(
        user_query=request.prompt,
        config=SQLQueryGenerationConfig(
            data_source_url=request.data_source_url,
            assert_results_not_empty=False,
        ),
    )
    df = sql_generation_result.dataframe
    print_final_queries(sql_generation_result.description, sql_generation_result.query)

    # Convert Period dtype to timestamp to ensure DataFrame is JSON serializable
    df = df.astype(
        {
            col: "datetime64[ns]"
            for col in df.columns
            if pd.api.types.is_period_dtype(df[col])
        }
    )

    try:
        df_summary = {
            column_name: f"{sample}: {dtype}"
            for column_name, sample, dtype in zip(df.columns, df.iloc[0], df.dtypes)
        }
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

    def no_show(*args, **kwargs):
        pass

    original_show_method = Figure.show
    Figure.show = no_show

    code_generation_result: PythonExecutionResult = generate_valid_python_code(
        user_query=request.prompt,
        code_generation_prompt=code_generation_prompt,
        local_variables={"df": df.copy()},
        config=CodeGenerationConfig(
            output_type=output_type,
            output_variable=output_variable,
        ),
    )
    print(f"Valid Python code:\n{code_generation_result.code}")

    Figure.show = original_show_method

    print("\n")
    print(f"Final error: {code_generation_result.error}")

    created_at = int(time.time())

    sql_generation_outputs = [
        Output(
            index=0,
            created_at=created_at,
            description=sql_generation_result.description,
            type=OutputType.SQL_QUERY.value,
            value=str(sql_generation_result.query),
        ),
        Output(
            index=1,
            created_at=created_at,
            description="",
            type=OutputType.PANDAS_DATAFRAME.value,
            value=base64.b64encode(pickle.dumps(df)).decode("utf-8"),
        ),
    ]

    code_generation_outputs = [
        Output(
            index=2,
            created_at=created_at,
            description=code_generation_result.description,
            type=OutputType.PYTHON_CODE.value,
            value=str(code_generation_result.code),
        ),
        Output(
            index=3,
            created_at=created_at,
            description="",
            type=OutputType.PYTHON_OUTPUT.value,
            value=str(code_generation_result.io),
        ),
    ]

    if not code_generation_result.result:
        code_generation_results = []
    elif not isinstance(code_generation_result.result, list):
        code_generation_results = [code_generation_result.result]
    else:
        code_generation_results = code_generation_result.result

    for index, output in enumerate(code_generation_results):
        _type: OutputType = map_type_to_output_type(output)
        # Convert output to JSON if it is a Plotly chart
        if _type == OutputType.PLOTLY_CHART:
            _output = output.to_json()
        elif _type == OutputType.PANDAS_DATAFRAME:
            _output = base64.b64encode(pickle.dumps(output)).decode("utf-8")
        else:
            _output = str(output)
        code_generation_outputs += [
            Output(
                index=4 + index,
                created_at=created_at,
                description=output_description,
                type=_type.value,
                value=_output,
            )
        ]

    outputs = sql_generation_outputs + code_generation_outputs

    return QueryResult(
        data_source="",
        output_type=request.output_type,
        attempts=[],
        errors=[],
        outputs=outputs,
    )
