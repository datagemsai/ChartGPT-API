# pylint: disable=C0103
# pylint: disable=C0116

import pandas as pd
from api.config import GPT_TEMPERATURE, PYTHON_GPT_MODEL, SQL_GPT_MODEL
from api.templates import (
    SQL_QUERY_GENERATION_PROMPT_TEMPLATE,
    SQL_QUERY_GENERATION_ERROR_PROMPT_TEMPLATE,
    CODE_GENERATION_PROMPT_TEMPLATE,
    CODE_GENERATION_IMPORTS,
    CODE_GENERATION_ERROR_PROMPT_TEMPLATE,
)
from api.types import PythonExecutionResult, QueryResult, SQLExecutionResult
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


# def get_initial_sql_query(messages) -> Tuple[str, str]:
#     response = openai.ChatCompletion.create(
#         model=SQL_GPT_MODEL,
#         messages=messages,
#         functions=functions,
#         function_call={"name": "validate_sql_query"},
#         temperature=GPT_TEMPERATURE,
#     )
#     response_message = response["choices"][0]["message"]
#     finish_reason = response["choices"][0]["finish_reason"]
#     if finish_reason == "length":
#         raise ContextLengthError
#     messages.append(response_message)
#     function_args = json.loads(
#         str(response_message["function_call"]["arguments"]), strict=False
#     )
#     description = function_args.get("description")
#     query = function_args.get("query")
#     return description, query


# def generate_valid_sql_query(
#     query: str,
#     description: str,
#     messages,
#     attempts=0,
#     max_attempts=10,
#     assert_results_not_empty=True,
# ) -> SQLExecutionResult:
#     query = apply_lower_to_where(query)
#     df = pd.DataFrame()

#     errors = validate_sql_query(
#         query=query,
#     )
#     if not errors:
#         try:
#             df = execute_sql_query(query=query)
#             if assert_results_not_empty and df.dropna(how="all").empty:
#                 print("Query returned no results.")
#                 errors += ["Query returned no results, please try again."]
#         except Exception as e:
#             errors += [str(e)]

#     print(f"Query:\n{query}")
#     print(f"Errors in query: {errors}")

#     if errors and attempts < max_attempts:
#         attempts += 1
#         print(f"Attempt: {attempts} of {max_attempts}")

#         messages.append(
#             {
#                 "role": "function",
#                 "name": "validate_sql_query",
#                 "content": inspect.cleandoc(SQL_QUERY_GENERATION_ERROR_PROMPT_TEMPLATE.format(errors=errors)),
#             }
#         )

#         corrected_response = openai.ChatCompletion.create(
#             model=PYTHON_GPT_MODEL,
#             messages=messages,
#             functions=functions,
#             function_call={"name": "validate_sql_query"},
#             temperature=GPT_TEMPERATURE,
#         )

#         print(f"Corrected response:\n{corrected_response}")
#         corrected_response_message = corrected_response["choices"][0]["message"]
#         finish_reason = corrected_response["choices"][0]["finish_reason"]
#         if finish_reason == "length":
#             raise ContextLengthError

#         messages.append(corrected_response_message)
#         function_args = json.loads(
#             str(corrected_response_message["function_call"]["arguments"]), strict=False
#         )
#         updated_description = function_args.get("description")
#         query = function_args.get("query")

#         return generate_valid_sql_query(
#             query=query,
#             description=updated_description,
#             messages=messages,
#             attempts=attempts,
#         )
#     else:
#         return SQLExecutionResult(
#             description=description,
#             query=query,
#             dataframe=df,
#         )


# def execute_sql_query(query: str) -> pd.DataFrame:
#     """Takes a BigQuery SQL query, executes it, and returns a pandas dataframe of the results"""
#     query_job = client.query(query)
#     results = query_job.result()
#     df = results.to_dataframe()
#     return df


# def get_valid_sql_query(user_query: str) -> SQLExecutionResult:
#     datasets = list(client.list_datasets())
#     tables_summary = get_tables_summary(
#         client=client,
#         datasets=datasets,
#         dataset_ids=[dataset.id for dataset in production_datasets],
#         table_ids=[
#             table_id for dataset in production_datasets for table_id in dataset.tables
#         ],
#     )
#     sql_query_generation_prompt = SQL_QUERY_GENERATION_PROMPT_TEMPLATE.format(
#         sql_query_instruction=(
#             "Develop a step-by-step plan and write a GoogleSQL query compatible with BigQuery",
#             "to fetch the data necessary for your analysis and visualization.",
#         ),
#         python_code_instruction=(
#             "Implement Python code to analyze the data using Pandas and visualize the findings using Plotly."
#         ),
#         database_schema=str(tables_summary),
#     )
#     messages = [
#         {
#             "role": "system",
#             "content": inspect.cleandoc(sql_query_generation_prompt),
#         },
#         {"role": "user", "content": "Analytics question: " + user_query},
#     ]

#     initial_sql_query_description, initial_sql_query = get_initial_sql_query(messages)
#     print(f"Initial SQL query description:\n{initial_sql_query_description}")
#     print(f"Initial SQL query:\n{initial_sql_query}")

#     result: SQLExecutionResult = generate_valid_sql_query(
#         query=initial_sql_query,
#         description=initial_sql_query_description,
#         messages=messages,
#     )
#     print(f"Final SQL query description:\n{result.description}")
#     print(f"Valid SQL query:\n{result.query}")

#     return result


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


class SQLQueryGenerationConfig:
    def __init__(self, max_attempts=10, assert_results_not_empty=True):
        self.max_attempts = max_attempts
        self.assert_results_not_empty = assert_results_not_empty


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
        user_query: str,
        config: SQLQueryGenerationConfig = SQLQueryGenerationConfig()
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
    code: str, docstring: str, imports=None, local_variables=None
) -> PythonExecutionResult:
    if not code:
        raise ValueError("No code provided")

    local_variables = local_variables.copy() if local_variables else {}
    local_variables["fig"] = None

    if imports:
        local_variables.update(execute_python_imports(imports))

    with StringIO() as io_buffer, redirect_stdout(io_buffer):
        try:
            secure_exec(code, local_variables, local_variables)
            answer_fn = local_variables.get("answer_question")
            if not callable(answer_fn):
                raise ValueError("The `answer_question` function was not found.")
            result = local_variables["fig"] = answer_fn(local_variables["df"])
            if not isinstance(result, go.Figure):
                raise ValueError(
                    "The `answer_question` function must return a Plotly figure."
                )
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            _, line_number, function_name, line_data = tb[-1]
            error_msg = f"{type(e).__name__}: {str(e)}\nOn line {line_number}, function `{function_name}`, with code `{line_data}`"
            return PythonExecutionResult(
                None, local_variables, io_buffer.getvalue(), error_msg
            )
        else:
            return PythonExecutionResult(
                result, local_variables, io_buffer.getvalue(), None
            )


def get_initial_python_code(messages) -> Tuple[str, str]:
    response = openai_chat_completion(PYTHON_GPT_MODEL, messages, "execute_python_code")
    _, docstring, code = extract_code_generation_response_data(response)
    return docstring, code


def generate_valid_python_code(
    code: str,
    docstring="",
    messages=None,
    imports=None,
    local_variables=None,
    max_attempts=10,
) -> str:
    messages = messages or []
    for attempt in range(max_attempts):
        result = execute_python_code(code, docstring, imports, local_variables)
        print(f"Code:\n{code}")
        print(f"Error in code: {result.error}")

        if result.error:
            print(f"Attempt: {attempt + 1} of {max_attempts}")
            error_prompt = CODE_GENERATION_ERROR_PROMPT_TEMPLATE.format(
                attempt=attempt + 1, code=code, error_message=result.error
            )
            messages.append({"role": "user", "content": inspect.cleandoc(error_prompt)})
            response = openai_chat_completion(
                PYTHON_GPT_MODEL, messages, "execute_python_code"
            )
            _, docstring, code = extract_code_generation_response_data(response)
        else:
            return code
    return code


def answer_user_query(user_query: str) -> QueryResult:
    # Returns
    sql_result: SQLExecutionResult = get_valid_sql_query(
        user_query=user_query,
        config=SQLQueryGenerationConfig(
            assert_results_not_empty=False,
        )
    )
    df = sql_result.dataframe
    print_final_queries(sql_result.description, sql_result.query)

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

    # TODO Temporarily hardcoding the request
    request = {
        "output_type": "chart",
    }
    request_output_type = request["output_type"]
    if request_output_type == "any":
        function_parameters = "df: pd.DataFrame"
        function_description = "Function to analyze the data and optionally return a list of results `result_list` or `None`."
        output_type = "Optional[List[Any]]"
        output_description = "A list of any type of object."
        output_variable = "result_list"
    elif request_output_type == "chart":
        function_parameters = "df: pd.DataFrame"
        function_description = (
            # "Function to analyze the data and return a list of Plotly charts."
            "Function to analyze the data and return a Plotly chart."
        )
        output_type = "plotly.graph_objs.Figure"
        output_description = "A Plotly figure object."
        output_variable = "fig"
    else:
        raise ValueError("Invalid output type requested")

    code_generation_prompt = CODE_GENERATION_PROMPT_TEMPLATE.format(
        sql_description=sql_result.description,
        sql_query=sql_result.query,
        dataframe_schema=json.dumps(df_summary, indent=4, sort_keys=True),
        imports=CODE_GENERATION_IMPORTS,
        function_parameters=function_parameters,
        function_description=function_description,
        output_type=output_type,
        output_description=output_description,
        output_variable=output_variable,
    )
    print(f"Code generation prompt:\n{code_generation_prompt}")

    messages = [
        {
            "role": "system",
            "content": inspect.cleandoc(code_generation_prompt),
        },
        {"role": "user", "content": user_query},
    ]

    docstring, initial_python_code = get_initial_python_code(messages)
    print(f"Initial Python code docstring:\n{docstring}")
    print(f"Initial Python code:\n{initial_python_code}")

    def no_show(*args, **kwargs):
        pass

    original_show_method = Figure.show
    Figure.show = no_show

    valid_python_code = generate_valid_python_code(
        code=initial_python_code,
        docstring=docstring,
        messages=messages,
        imports=CODE_GENERATION_IMPORTS,
        local_variables={"df": df.copy()},
    )
    print(f"Valid Python code:\n{valid_python_code}")

    Figure.show = original_show_method

    result: PythonExecutionResult = execute_python_code(
        code=valid_python_code,
        docstring=docstring,
        imports=CODE_GENERATION_IMPORTS,
        local_variables={"df": df},
    )

    print("\n")
    print(f"Final error: {result.error}")

    figure = result.local_variables.get("fig", None)
    return QueryResult(
        description=sql_result.description,
        query=sql_result.query,
        code=valid_python_code,
        chart=figure.to_json() if figure else None,
        output=result.io,
        dataframe=base64.b64encode(pickle.dumps(df)).decode("utf-8"),
    )
