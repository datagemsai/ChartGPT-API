import sys
import pandas as pd
import os
from chartgpt.tools.python.secure_ast import secure_exec
import openai
import json
import re

from plotly.graph_objs import Figure
from contextlib import redirect_stdout
from io import StringIO
from typing import Any, List, Optional
from dataclasses import dataclass
from google.oauth2 import service_account
from google.cloud import bigquery
from typing import Dict, List, Tuple, Union
from dotenv import load_dotenv
import inspect
import plotly.graph_objs as go
import traceback
import pickle
import base64

from chartgpt.app import client
from app.config import Dataset
from app.config.production import datasets as production_datasets

# Override Streamlit styling
import plotly.io as pio

pio.templates.default = "plotly"

# Load environment variables from .env file
load_dotenv(".env")

openai.api_key = os.environ["OPENAI_API_KEY"]

SQL_GPT_MODEL = "gpt-4"
PYTHON_GPT_MODEL = "gpt-4"
GPT_TEMPERATURE = 0.0

# def get_tables_summary(
#         client: bigquery.Client,
#         datasets: List[Dataset],
#         include_types = False
# ) -> Dict[str, List[Dict[str, List[Union[Tuple[str, str], str]]]]]:
#     # Generate tables_summary for all tables in datasets
#     tables_summary = {}
#     for dataset in datasets:
#         dataset_id = dataset.id
#         tables_summary[dataset_id] = {}
#         for table_id in dataset.tables:
#             table_ref = client.dataset(dataset_id).table(table_id)
#             table = client.get_table(table_ref)
#             tables_summary[dataset_id][table_id] = [
#                 (schema_field.name, schema_field.field_type) if include_types else schema_field.name
#                 for schema_field in table.schema
#             ]
#     return tables_summary


# def get_tables_summary(
#         client: bigquery.Client,
#         datasets: List[bigquery.Dataset],
#         dataset_ids: Optional[List[str]] = None,
#         table_ids: Optional[List[str]] = None,
#         include_types=False
# ) -> Dict[str, List[Dict[str, List[Union[Tuple[str, str], str]]]]]:

#     tables_summary = {}

#     # Filter bigquery.Dataset objects by dataset_ids
#     if dataset_ids:
#         datasets = [dataset for dataset in datasets if dataset.dataset_id in dataset_ids]

#     for dataset in datasets:
#         dataset_id = dataset.dataset_id
#         tables_summary[dataset_id] = {}

#         # Filter bigquery.Table objects by table_ids
#         if table_ids:
#             tables = [table for table in list(client.list_tables(dataset)) if table.table_id in table_ids]
#         else:
#             tables = list(client.list_tables(dataset))

#         for table in tables:
#             table_id = table.table_id
#             table_ref = client.dataset(dataset_id).table(table_id)
#             table = client.get_table(table_ref)

#             # SQL-like CREATE TABLE statement
#             create_table_statement = f'CREATE TABLE {dataset_id}.{table_id} (\n'

#             for field in table.schema:
#                 create_table_statement += f'"{field.name}" {field.field_type}'

#                 if field.mode == "REQUIRED":
#                     create_table_statement += ' NOT NULL'

#                 create_table_statement += ',\n'

#             # Adding primary and foreign keys can be dataset-specific and needs more info.
#             # Here we are not adding them, but they can be added based on the dataset schema.
#             create_table_statement = create_table_statement.rstrip(',\n') + '\n)'

#             # Populate the summary
#             tables_summary[dataset_id][table_id] = {
#                 "fields": [
#                     (schema_field.name, schema_field.field_type) if include_types else schema_field.name
#                     for schema_field in table.schema
#                 ],
#                 "SQL_Schema": create_table_statement
#             }

#     return tables_summary


def get_tables_summary(
    client: bigquery.Client,
    datasets: List[bigquery.Dataset],
    dataset_ids: Optional[List[str]] = None,
    table_ids: Optional[List[str]] = None,
    include_types: bool = False,
) -> str:
    markdown_summary = ""

    # Filter bigquery.Dataset objects by dataset_ids
    if dataset_ids:
        datasets = [
            dataset for dataset in datasets if dataset.dataset_id in dataset_ids
        ]

    for dataset in datasets:
        dataset_id = dataset.dataset_id
        markdown_summary += f"## Dataset: {dataset_id}\n"

        # Filter bigquery.Table objects by table_ids
        if table_ids:
            tables = [
                table
                for table in list(client.list_tables(dataset))
                if table.table_id in table_ids
            ]
        else:
            tables = list(client.list_tables(dataset))

        for table in tables:
            table_id = table.table_id
            table_ref = client.dataset(dataset_id).table(table_id)
            table = client.get_table(table_ref)

            # SQL-like CREATE TABLE statement
            create_table_statement = f"CREATE TABLE {dataset_id}.{table_id} (\n"

            for field in table.schema:
                create_table_statement += f'"{field.name}" {field.field_type}'

                if field.mode == "REQUIRED":
                    create_table_statement += " NOT NULL"

                create_table_statement += ","
                if field.description:
                    create_table_statement += f" - {field.description}"
                create_table_statement += "\n"

            # Here we are not adding primary and foreign keys, but they can be added based on the dataset schema.
            create_table_statement = create_table_statement.rstrip(",\n") + "\n)"

            markdown_summary += f"### {dataset_id}.{table_id}\n"
            markdown_summary += f"```\n{create_table_statement}\n```\n"

    return markdown_summary


datasets = list(client.list_datasets())
tables_summary = get_tables_summary(
    client=client,
    datasets=datasets,
    dataset_ids=[dataset.id for dataset in production_datasets],
    table_ids=[
        table_id for dataset in production_datasets for table_id in dataset.tables
    ],
    include_types=True,
)


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


def get_initial_sql_query(messages) -> Tuple[str, str]:
    response = openai.ChatCompletion.create(
        model=SQL_GPT_MODEL,
        messages=messages,
        functions=functions,
        # function_call="auto",  # auto is default, but we'll be explicit
        function_call={"name": "validate_sql_query"},
        temperature=GPT_TEMPERATURE,
    )
    response_message = response["choices"][0]["message"]
    finish_reason = response["choices"][0]["finish_reason"]
    if finish_reason == "length":
        raise ContextLengthError
    messages.append(response_message)  # extend conversation with assistant's reply
    function_args = json.loads(
        str(response_message["function_call"]["arguments"]), strict=False
    )
    description = function_args.get("description")
    query = function_args.get("query")
    return description, query


def apply_lower_to_where(sql):
    # Regular expression to find the WHERE clause
    where_clause = re.search(r"\bWHERE\b(.*)", sql, flags=re.IGNORECASE)

    # If no WHERE clause is found, return the original SQL
    if where_clause is None:
        return sql

    # Extract the WHERE clause
    where_clause = where_clause.group(1)

    # Find all comparisons within the WHERE clause where the value is a string
    comparisons = re.findall(r'(\w+)\s*=\s*([\'"].+?[\'"])', where_clause)

    # Replace each comparison with the LOWER function, only for strings
    for col, value in comparisons:
        old_comparison = f"{col} = {value}"
        new_comparison = f"LOWER({col}) = LOWER({value})"
        where_clause = where_clause.replace(old_comparison, new_comparison, 1)

    # Replace the original WHERE clause with the modified one
    modified_sql = re.sub(
        r"\bWHERE\b.*", f"WHERE{where_clause}", sql, flags=re.IGNORECASE
    )

    return modified_sql


@dataclass
class SQLExecutionResult:
    description: str
    query: str
    dataframe: pd.DataFrame


def generate_valid_sql_query(
    query: str, description: str, messages, attempts=0, max_attempts=10
) -> SQLExecutionResult:
    query = apply_lower_to_where(query)
    df = pd.DataFrame()

    errors = validate_sql_query(
        query=query,
    )
    if not errors:
        # If there are no errors, try executing the query
        try:
            df = execute_sql_query(query=query)
            if df.dropna(how="all").empty:
                print("Query returned no results.")
                errors += ["Query returned no results, please try again."]
        except Exception as e:
            errors += [str(e)]

    print(f"Query:\n{query}")
    print(f"Errors in query: {errors}")

    if errors and attempts < max_attempts:
        attempts += 1
        print(f"Attempt: {attempts} of {max_attempts}")

        messages.append(
            {
                "role": "function",
                "name": "validate_sql_query",
                "content": f"""
                There was an error in the GoogleSQL query. Please correct the following errors and try again:
                {errors}
                """,
            }
        )  # extend conversation with function response

        corrected_response = openai.ChatCompletion.create(
            model=PYTHON_GPT_MODEL,
            messages=messages,
            functions=functions,
            # function_call="auto",  # auto is default, but we'll be explicit
            function_call={"name": "validate_sql_query"},
            temperature=GPT_TEMPERATURE,
        )  # get a new response from GPT where it can see the function response

        print(f"Corrected response:\n{corrected_response}")
        corrected_response_message = corrected_response["choices"][0]["message"]
        finish_reason = corrected_response["choices"][0]["finish_reason"]
        if finish_reason == "length":
            raise ContextLengthError

        messages.append(
            corrected_response_message
        )  # extend conversation with assistant's reply
        function_args = json.loads(
            str(corrected_response_message["function_call"]["arguments"]), strict=False
        )
        updated_description = function_args.get("description")
        query = function_args.get("query")

        return generate_valid_sql_query(
            query=query,
            description=updated_description,
            messages=messages,
            attempts=attempts,
        )
    else:
        return SQLExecutionResult(
            description=description,
            query=query,
            dataframe=df,
        )


def execute_sql_query(query: str) -> pd.DataFrame:
    """Takes a BigQuery SQL query, executes it, and returns a pandas dataframe of the results"""
    query_job = client.query(query)
    results = query_job.result()
    df = results.to_dataframe()
    return df


def get_valid_sql_query(user_query: str) -> SQLExecutionResult:
    messages = [
        {
            "role": "system",
            "content": inspect.cleandoc(
                f"""
            You are a Data Analyst specialized in GoogleSQL (BigQuery syntax), Pandas, and Plotly. Your mission is to address a specific analytics question and visualize the findings. Follow these steps:

            1. **Understand the Data:** Analyze the BigQuery database schema to understand what data is available.
            2. **GoogleSQL Query:** Develop a step-by-step plan and write a GoogleSQL query compatible with BigQuery to fetch the data necessary for your analysis and visualization.
            3. **Python Code:** Implement Python code to analyze the data using Pandas and visualize the findings using Plotly.

            # GoogleSQL Guidelines
            - Avoid DML operations (INSERT, UPDATE, DELETE, DROP, etc.)
            - Use `LOWER` for case-insensitive string comparisons: `LOWER(column_name) = LOWER('value')`
            - Use `LIKE` for case-insensitive substring matches: `LOWER(column_name) LIKE '%value%'`
            - If the result is empty, try `LIKE` with other variations of the value.
            
            # BigQuery Database Schema
            The GoogleSQL query should be constructed based on the following database schema:

            {str(tables_summary)}

            # Begin
            Complete Steps (1) and (2).
        """
            ),
        },
        {"role": "user", "content": "Analytics question: " + user_query},
    ]
    #             - Always exclude NULL values: `WHERE column_name IS NOT NULL`

    initial_sql_query_description, initial_sql_query = get_initial_sql_query(messages)
    print(f"Initial SQL query description:\n{initial_sql_query_description}")
    print(f"Initial SQL query:\n{initial_sql_query}")

    result: SQLExecutionResult = generate_valid_sql_query(
        query=initial_sql_query,
        description=initial_sql_query_description,
        messages=messages,
    )
    print(f"Final SQL query description:\n{result.description}")
    print(f"Valid SQL query:\n{result.query}")

    return result


def execute_python_imports(imports: str) -> dict:
    """Takes a Python imports string, executes it, and returns a dict of the imported modules"""
    try:
        global_variables = {}
        exec(imports, global_variables)
        return global_variables
    except Exception as e:
        print(e)
        return {}


@dataclass
class PythonExecutionResult:
    result: Any
    local_variables: dict
    io: str
    error: str


@dataclass
class QueryResult:
    description: str
    query: str
    code: str
    chart: str
    output: str
    dataframe: str


def execute_python_code(
    code: str, docstring: str, imports=None, local_variables=None
) -> PythonExecutionResult:
    """Takes a Python code string, executes it, and returns an instance of PythonExecutionResult"""
    result = ""
    io = ""
    error = None

    if not code:
        raise ValueError("No code provided")

    if local_variables is None:
        local_variables = {}
    else:
        local_variables = local_variables.copy()

    local_variables["fig"] = None

    if imports:
        imported_modules = execute_python_imports(imports=imports)
        local_variables.update(imported_modules)

    global_variables = local_variables

    io_buffer = StringIO()
    try:
        with redirect_stdout(io_buffer):
            secure_exec(f"{code}", global_variables, local_variables)
            answer_question = local_variables.get("answer_question", None)
            if not callable(answer_question):
                error = "The `answer_question` function was not found. Please ensure that the function is named `answer_question` and is defined in the Python code."
            else:
                result = local_variables["fig"] = answer_question(local_variables["df"])
                if not isinstance(result, go.Figure):
                    error = f"The `answer_question` function returned `{type(result)}`. Please ensure that the function returns a single Plotly figure."
            return PythonExecutionResult(
                result=result,
                local_variables=local_variables,
                io=io_buffer.getvalue(),
                error=error,
            )
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        file_name, line_number, function_name, line_data = tb[-1]
        error = inspect.cleandoc(
            f"""
        {type(e).__name__}: {str(e)}
        On line {line_number}, function `{function_name}`, with code `{line_data}`
        """
        )
        return PythonExecutionResult(
            result=result, local_variables=local_variables, io=io, error=error
        )


class ContextLengthError(Exception):
    pass


def get_initial_python_code(messages) -> str:
    response = openai.ChatCompletion.create(
        model=PYTHON_GPT_MODEL,
        messages=messages,
        functions=functions,
        # function_call="auto",  # auto is default, but we'll be explicit
        function_call={"name": "execute_python_code"},
        temperature=GPT_TEMPERATURE,
    )
    response_message = response["choices"][0]["message"]
    finish_reason = response["choices"][0]["finish_reason"]
    if finish_reason == "length":
        raise ContextLengthError
    messages.append(response_message)  # extend conversation with assistant's reply
    function_args = json.loads(
        str(response_message["function_call"]["arguments"]), strict=False
    )
    docstring = function_args.get("docstring")
    code = function_args.get("code")
    return docstring, code


def generate_valid_python_code(
    code: str,
    docstring="",
    messages=[],
    imports=None,
    local_variables=None,
    attempts=0,
    max_attempts=10,
) -> str:
    result: PythonExecutionResult = execute_python_code(
        code=code, docstring=docstring, imports=imports, local_variables=local_variables
    )
    print(f"Code:\n{code}")
    print(f"Error in code: {result.error}")

    if result.error and attempts < max_attempts:
        attempts += 1
        print(f"Attempt: {attempts} of {max_attempts}")

        if result.error:
            messages.append(
                {
                    "role": "user",
                    "content": f"""
                    # Error Detected in Python Code
                    Please correct the errors and try again.
                    
                    Attempt #{attempts}:
                    ```python
                    {code}
                    ```

                    Error Message:
                    {result.error}
                    """,
                }
            )  # extend conversation with function response

        corrected_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            functions=functions,
            # function_call="auto",  # auto is default, but we'll be explicit
            function_call={"name": "execute_python_code"},
            temperature=GPT_TEMPERATURE,
        )  # get a new response from GPT where it can see the function response

        print(f"Corrected response: {corrected_response}")
        corrected_response_message = corrected_response["choices"][0]["message"]
        finish_reason = corrected_response["choices"][0]["finish_reason"]
        if finish_reason == "length":
            raise ContextLengthError

        messages.append(
            corrected_response_message
        )  # extend conversation with assistant's reply
        function_args = json.loads(
            str(corrected_response_message["function_call"]["arguments"]), strict=False
        )
        docstring = function_args.get("docstring")
        code = function_args.get("code")

        return generate_valid_python_code(
            code=code,
            docstring=docstring,
            messages=messages,
            imports=imports,
            local_variables=local_variables,
            attempts=attempts,
        )
    else:
        return code


imports = """
import pandas as pd
import plotly
import plotly.express as px
import numpy as np
"""


def answer_user_query(user_query: str) -> QueryResult:
    # Returns
    sql_result: SQLExecutionResult = get_valid_sql_query(user_query=user_query)
    df = sql_result.dataframe

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

    messages = [
        {
            "role": "system",
            "content": inspect.cleandoc(
                f"""
            You're a Data Analyst proficient in the use of GoogleSQL, Pandas, and Plotly.
            You have been provided with a Pandas DataFrame `df` containing the results of a GoogleSQL query.
            Your task is to use the data provided to answer a user's Analytics Question and visualise the results.
         
            # GoogleSQL Query
            {sql_result.description}

            ```sql
            {sql_result.query}
            ```

            # DataFrame Schema
            {json.dumps(df_summary, indent=4, sort_keys=True)}

            # Instructions
            - Display text outputs using `print()`.
            - For visual outputs, use Plotly within the `answer_question()` function.
            - Complete the following code, replacing <YOUR CODE HERE> with your own code.
            - Do not try to recreate the Pandas DataFrame `df` or generate sample data.

            ```python
            # Required Imports
            {imports}

            # Analysis and Visualization Function
            def answer_question(df: pd.DataFrame) -> plotly.graph_objs.Figure:
                '''
                Function to analyze the data and generate a Plotly chart.
                
                Parameters:
                    df (pd.DataFrame): DataFrame containing the data.
                
                Returns:
                    plotly.graph_objs.Figure: The Plotly figure object.
                '''
                <YOUR CODE HERE>
                return fig
            ```

            # Analytics Question
        """
            ),
        },
        {"role": "user", "content": user_query},
    ]
    # Follow these steps:

    # 1. **Understand Data:** Start by examining the GoogleSQL query to understand what data is available in the Pandas DataFrame `df`.
    # 2. **Code Analysis:** Implement the function `answer_question(df: pd.DataFrame)` to analyze `df`.
    # 3. **Data Visualization:** Within `answer_question(df: pd.DataFrame)`, use Plotly to create a chart that visualizes your analysis.
    docstring, initial_python_code = get_initial_python_code(messages)
    print(f"Initial Python code docstring:\n{docstring}")
    print(f"Initial Python code:\n{initial_python_code}")

    # Set the rendering backend to a non-displaying format
    # original_renderer = pio.renderers.default
    # pio.renderers.default = "png"

    def no_show(*args, **kwargs):
        pass

    # Override the 'show' method with the 'no_show' function
    original_show_method = Figure.show
    Figure.show = no_show

    valid_python_code = generate_valid_python_code(
        code=initial_python_code,
        docstring=docstring,
        messages=messages,
        imports=imports,
        local_variables={"df": df.copy()},
    )
    print(f"Valid Python code:\n{valid_python_code}")

    # Restore the original rendering backend
    # pio.renderers.default = original_renderer
    Figure.show = original_show_method

    result: PythonExecutionResult = execute_python_code(
        code=valid_python_code,
        docstring=docstring,
        imports=imports,
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
