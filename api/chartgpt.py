import pandas as pd
import os
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

from app.config import Dataset
from app.config.production import datasets


# Load environment variables from .env file
load_dotenv(".env")

openai.api_key = os.environ["OPENAI_API_KEY"]

# GPT_MODEL = "gpt-3.5-turbo"
GPT_MODEL = "gpt-4"
GPT_TEMPERATURE = 0.7

credentials = service_account.Credentials.from_service_account_info(
    json.loads(os.environ["GCP_SERVICE_ACCOUNT"], strict=False)
)
client = bigquery.Client(credentials=credentials)

def get_tables_summary(
        client: bigquery.Client,
        datasets: List[Dataset],
        include_types = False
) -> Dict[str, List[Dict[str, List[Union[Tuple[str, str], str]]]]]:
    # Generate tables_summary for all tables in datasets
    tables_summary = {}
    for dataset in datasets:
        dataset_id = dataset.id
        tables_summary[dataset_id] = {}
        for table_id in dataset.tables:
            table_ref = client.dataset(dataset_id).table(table_id)
            table = client.get_table(table_ref)
            tables_summary[dataset_id][table_id] = [
                (schema_field.name, schema_field.field_type) if include_types else schema_field.name
                for schema_field in table.schema
            ]
    return tables_summary


tables_summary = get_tables_summary(client=client, datasets=datasets)


def validate_sql_query(query: str) -> List[str]:
    """Takes a BigQuery SQL query, executes it using a dry run, and returns a list of errors, if any"""
    try:
        query_job = client.query(query, job_config=bigquery.QueryJobConfig(dry_run=True))
        errors = [str(err['message']) for err in query_job.errors] if query_job.errors else []
    except Exception as e:
        errors = [str(e)]
    return errors


functions = [
    {
        "name": "validate_sql_query",
        "description": f"""
        Takes a BigQuery SQL query, executes it using a dry run, and returns a list of errors, if any.
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The GoogleSQL query to validate",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "execute_python_code",
        "description": f"""
        Takes a Python code string, executes it, and returns an instance of PythonExecutionResult.
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The Python code to execute",
                },
            },
            "required": ["code"],
        },
    },
]


def get_initial_sql_query(messages) -> str:
    response = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=messages,
            functions=functions,
            # function_call="auto",  # auto is default, but we'll be explicit
            function_call={"name": "validate_sql_query"},
            temperature=GPT_TEMPERATURE,
    )
    response_message = response["choices"][0]["message"]
    messages.append(response_message)  # extend conversation with assistant's reply
    function_args = json.loads(
        str(response_message["function_call"]["arguments"]),
        strict=False
    )
    query = function_args.get("query")
    return query



def apply_lower_to_where(sql):
    # Regular expression to find the WHERE clause
    where_clause = re.search(r'\bWHERE\b(.*)', sql, flags=re.IGNORECASE)

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
    modified_sql = re.sub(r'\bWHERE\b.*', f"WHERE{where_clause}", sql, flags=re.IGNORECASE)

    return modified_sql


def generate_valid_sql_query(query: str, messages, attempts=0, max_attempts=10) -> str:
    query = apply_lower_to_where(query)

    errors = validate_sql_query(
        query=query,
    )
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
            model=GPT_MODEL,
            messages=messages,
            functions=functions,
            # function_call="auto",  # auto is default, but we'll be explicit
            function_call={"name": "validate_sql_query"},
            temperature=GPT_TEMPERATURE,
        )  # get a new response from GPT where it can see the function response

        print(f"Corrected response:\n{corrected_response}")
        corrected_response_message = corrected_response["choices"][0]["message"]

        messages.append(corrected_response_message)  # extend conversation with assistant's reply
        function_args = json.loads(
            str(corrected_response_message["function_call"]["arguments"]),
            strict=False
        )
        query = function_args.get("query")
        
        return generate_valid_sql_query(query=query, messages=messages, attempts=attempts)
    else:
        return query


def execute_sql_query(query: str) -> pd.DataFrame:
    """Takes a BigQuery SQL query, executes it, and returns a pandas dataframe of the results"""
    query_job = client.query(query)
    results = query_job.result()
    df = results.to_dataframe()
    return df


def get_valid_sql_query(user_query: str) -> str:
    messages = [
        {"role": "system", "content": f"""
            You are a data analyst and GoogleSQL expert.
            When given an analytics question you must construct a GoogleSQL query to get the data to answer the question.
            You will in a subsequent step write Python code to analyze the data and plot the results.

            # SQL Instructions
            - Always drop NULL values from the results: e.g. `WHERE column_name IS NOT NULL`
            - Do NOT make DML statements (INSERT, UPDATE, DELETE, DROP, etc.).
            - Always use `LOWER` when comparing strings to ensure case insensitivity: e.g. `LOWER(column_name) = LOWER('value')`
            - SQL should be written using the following database schema (ensure the column names are correct):
            {str(tables_summary)}
        """},
        {"role": "user", "content": "Analytics question: " + user_query},
    ]
    
    initial_sql_query = get_initial_sql_query(messages)
    print(f"Initial SQL query:\n{initial_sql_query}")
    
    valid_sql_query = generate_valid_sql_query(query=initial_sql_query, messages=messages)
    print(f"Valid SQL query:\n{valid_sql_query}")

    return valid_sql_query


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


def execute_python_code(code: str, imports=None, local_variables=None) -> PythonExecutionResult:
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

    local_variables["result"] = None

    if imports:
        imported_modules = execute_python_imports(imports=imports)
        local_variables.update(imported_modules)
    
    global_variables = local_variables

    # for lib in libraries:
    #     local_variables[lib] = importlib.import_module(lib)

    io_buffer = StringIO()
    try:
        with redirect_stdout(io_buffer):
            exec(f"{code}\nresult = {code.splitlines()[-1]}", global_variables, local_variables)
            result = local_variables["result"]
            io = io_buffer.getvalue()
            return PythonExecutionResult(result=result, local_variables=local_variables, io=io, error=error)
    except Exception as e:
        print(e)
        error = "{}: {}".format(type(e).__name__, str(e))
        return PythonExecutionResult(result=result, local_variables=local_variables, io=io, error=error)


def get_initial_python_code(messages) -> str:
    response = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=messages,
            functions=functions,
            # function_call="auto",  # auto is default, but we'll be explicit
            function_call={"name": "execute_python_code"},
            temperature=GPT_TEMPERATURE,
    )
    response_message = response["choices"][0]["message"]
    messages.append(response_message)  # extend conversation with assistant's reply
    function_args = json.loads(
        str(response_message["function_call"]["arguments"]),
        strict=False
    )
    code = function_args.get("code")
    return code


def generate_valid_python_code(code: str, messages, imports=None, local_variables=None, attempts=0, max_attempts=10) -> str:
    result: PythonExecutionResult = execute_python_code(code=code, imports=imports, local_variables=local_variables)
    print(f"Code:\n{code}")
    print(f"Error in code: {result.error}")

    figure_created = result.local_variables.get("fig", None)

    if (result.error or not figure_created) and attempts < max_attempts:
        attempts += 1
        print(f"Attempt: {attempts} of {max_attempts}")

        if result.error:
            messages.append(
                {
                    "role": "user",
                    "content": f"""
                    There was an error in the Python code. Please correct the following errors and try again:
                    {result.error}
                    """,
                }
            )  # extend conversation with function response
        
        if not figure_created:
            messages.append(
                {
                    "role": "user",
                    "content": f"""
                    Expected a Plotly figure named `fig` to exist. Please create and display a Plotly figure using `fig.show()`.
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

        messages.append(corrected_response_message)  # extend conversation with assistant's reply
        function_args = json.loads(
            str(corrected_response_message["function_call"]["arguments"]),
            strict=False
        )
        code = function_args.get("code")
        
        return generate_valid_python_code(code=code, messages=messages, imports=imports, local_variables=local_variables, attempts=attempts)
    else:
        return code


imports = """
import pandas as pd
import plotly.express as px
import numpy as np
"""


def answer_user_query(user_query: str) -> tuple[Optional[str], Optional[str], Optional[str]]:
    # Returns
    valid_sql_query = get_valid_sql_query(user_query=user_query)
    figure_json_string = ""

    df = execute_sql_query(query=valid_sql_query)
    messages = [
        {"role": "system", "content": f"""
            You are an expert data analyst.
            When given an analytics question you must write Python code using Pandas to answer the question and plot the results using Plotly.
         
            You have access to a Pandas DataFrame named `df` with the following data structure:
         
            {df}

            Do not attempt to create your own sample data or Pandas DataFrame!

            # Python Instructions
            - Unless displaying Plotly charts and Pandas DataFrames, use `print()` to display output, for example on the last line of code.
            - Always create a Plotly figure, assign it to a variable named `fig` and use `fig.show()` to display it.
            - You have access to the following libraries:\n {str(imports)}
        """},
        {"role": "user", "content": "Analytics question: " + user_query},
    ]
    initial_python_code = get_initial_python_code(messages)
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
        messages=messages,
        imports=imports,
        local_variables={"df": df.copy()}
    )
    print(f"Valid Python code:\n{valid_python_code}")

    # Restore the original rendering backend
    # pio.renderers.default = original_renderer
    Figure.show = original_show_method

    result: PythonExecutionResult = execute_python_code(
        code=valid_python_code,
        imports=imports,
        local_variables={"df": df}
    )

    print("\n")
    # print(f"Final result: {result.result}")
    # print(f"Final io: {result.io}")
    print(f"Final error: {result.error}")

    figure = result.local_variables.get("fig", None)
    if figure:
        figure_json_string = figure.to_json()
        # figure_json = json.loads(figure_json_string, strict=False)
        return valid_sql_query, valid_python_code, figure_json_string
    else:
        return valid_sql_query, valid_python_code, None

# answer_user_query("Give me a description of each of the columns in the dataset")
# answer_user_query("Which protocol provided the lowest APRs in the past month?")
# answer_user_query("Plot the average APR for the NFTfi protocol in the past 6 months")
# answer_user_query("Plot a bar chart of the USD lending volume for all protocols")
# answer_user_query("Plot a stacked area chart of the USD lending volume for all protocols over time")
