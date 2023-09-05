# pylint: disable=C0103
# pylint: disable=C0116

import time
import pandas as pd
from api.config import GPT_TEMPERATURE, PYTHON_GPT_MODEL, SQL_GPT_MODEL
from api.templates import (
    SQL_QUERY_GENERATION_PROMPT_TEMPLATE,
    SQL_QUERY_GENERATION_ERROR_PROMPT_TEMPLATE,
    CODE_GENERATION_PROMPT_TEMPLATE,
    CODE_GENERATION_IMPORTS,
    CODE_GENERATION_ERROR_PROMPT_TEMPLATE,
)
from chartgpt_client import ApiRequestAskChartgptRequest as Request
from chartgpt_client import Attempt, Output, OutputType
from api.types import (
    # Request,
    # Attempt,
    CodeGenerationConfig,
    # Output,
    PythonExecutionResult,
    QueryResult,
    SQLExecutionResult,
    SQLQueryGenerationConfig,
)
from api.errors import ContextLengthError
from api.utils import apply_lower_to_where, get_tables_summary
from chartgpt.tools.python.secure_ast import secure_exec
import openai
import json

from plotly.graph_objs import Figure
from contextlib import redirect_stdout
from io import StringIO
from typing import List
from google.cloud import bigquery
from typing import List, Tuple
import inspect
import plotly.graph_objs as go
import traceback
import pickle
import base64

from chartgpt.app import client
from app import datasets as production_datasets

# Imports required for `eval` of `output_type` argument to work
import plotly
from typing import Optional

# Override Streamlit styling
import plotly.io as pio

pio.templates.default = "plotly"


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
    user_query: str, config: SQLQueryGenerationConfig = SQLQueryGenerationConfig()
) -> SQLExecutionResult:
    tables_summary = get_tables_summary(
        client=client,
        datasets=list(client.list_datasets()),
        dataset_ids=[dataset.id for dataset in production_datasets],
        table_ids=[
            table_id for dataset in production_datasets for table_id in dataset.tables
        ],
    )

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
    local_variables[config.output_variable] = None

    if imports:
        local_variables.update(execute_python_imports(imports))

    with StringIO() as io_buffer, redirect_stdout(io_buffer):
        try:
            secure_exec(code, local_variables, local_variables)
            answer_fn = local_variables.get("answer_question")
            if callable(answer_fn):
                result = local_variables[config.output_variable] = answer_fn(
                    local_variables["df"]
                )
            elif local_variables[config.output_variable]:
                result = local_variables[config.output_variable]
            else:
                raise ValueError("The `answer_question` function was not found.")
            if not isinstance(result, eval(config.output_type)):
                raise ValueError(
                    f"The `answer_question` function must return a variable of type {config.output_type}."
                )
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            _, line_number, function_name, line_data = tb[-1]
            error_msg = f"{type(e).__name__}: {str(e)}\nOn line {line_number}, function `{function_name}`, with code `{line_data}`"
            return PythonExecutionResult(
                description=docstring,
                code=code,
                output=None,
                local_variables=local_variables,
                io=io_buffer.getvalue(),
                error=error_msg,
            )
        else:
            return PythonExecutionResult(
                description=docstring,
                code=code,
                output=result,
                local_variables=local_variables,
                io=io_buffer.getvalue(),
                error=None,
            )


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

    # TODO Handle all output types:
    # - any
    # - plotly_chart
    # - sql_query
    # - python_code
    # - python_output
    # - pandas_dataframe

    if request.output_type == OutputType.ANY.value:
        function_parameters = "df: pd.DataFrame"
        function_description = "Function to analyze the data and optionally return a list of results `result_list` or `None`."
        output_type = "Optional[List[Any]]"
        output_description = "A list of any type of object."
        output_variable = "result_list"
    elif request.output_type == OutputType.PLOTLY_CHART.value:
        function_parameters = "df: pd.DataFrame"
        function_description = (
            # "Function to analyze the data and return a list of Plotly charts."
            "Function to analyze the data and return a Plotly chart."
        )
        output_type = "plotly.graph_objs.Figure"
        output_description = "A Plotly figure object."
        output_variable = "fig"
    elif request.output_type == "optional_chart":
        function_parameters = "df: pd.DataFrame"
        function_description = (
            "Function to analyze the data and optionally return a Plotly chart."
        )
        output_type = "Optional[plotly.graph_objs.Figure]"
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

    # TODO Handle all output types:
    output_value = code_generation_result.output
    created_at = int(time.time())

    outputs = [
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
            value=str(base64.b64encode(pickle.dumps(df)).decode("utf-8")),
        ),
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
        Output(
            index=4,
            created_at=created_at,
            description=output_description,
            type=OutputType.PLOTLY_CHART.value,
            value=str(output_value.to_json() if output_value else None),
        )
    ]

    return QueryResult(
        output_type=request.output_type,
        attempts=[],
        errors=[],
        outputs=outputs,
    )
