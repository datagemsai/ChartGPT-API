

import os
from dataclasses import dataclass, asdict, replace
from typing import Dict, List, Union, Any
import requests
from sqlalchemy import text
import io
import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv


# from nftBot.ChartBot.single_stream import get_eng_project_dataset_id

# Load environment variables from the .env file
load_dotenv()


def table_info(table):
    # TODO 2023-04-17:  upgrade with BQ info
    field_summary = "\n\t".join(
        f.name + " " + f.field_type.name for f in table.schema.fields
    )
    schema_summary = f"""Schema for table: {table.port_name}
    \t{field_summary}
    """

    df = table.read_sql(f"select * from {table} limit 5", as_format="dataframe")

    s = f"""{schema_summary}
Data for table: {table.port_name}:
{df}
    """
    return s


def completion_local_agent(prompt, n=0):
    # create a completion
    resp = agent.run(prompt)
    return resp


def completion(prompt, **kwargs):
    api_key = os.environ['OPENAI_API_KEY']

    params = {
        "prompt": prompt,
        "model": "text-davinci-003",
        "max_tokens": 500,
        "temperature": 0.8,
    }
    params.update(kwargs)
    # create a completion
    # TODO 2023-04-19: try with other apis?
    resp = requests.post(
        "https://api.openai.com/v1/completions",
        json=params,
        headers={"Authorization": f"Bearer {api_key}"},
    )
    # resp = handle_rate_limiting(resp)
    if not resp.ok:
        print(resp.json())
        resp.raise_for_status()
    return resp.json()["choices"][0]["text"]


@dataclass(frozen=True)
class QueryResult:
    sql: str
    result: list[dict] = None
    error: str = None


def get_sql_result(eng, sql: str, limit=50000000000000) -> QueryResult:
    """
    Executes a SQL query using the provided database engine, and returns the query result as a QueryResult object.
    If the query fails, returns an error message instead.

    Args:
        eng: A SQLAlchemy engine instance connected to a database.
        sql: The SQL query to be executed.
        limit: The maximum number of rows to be returned in the result.

    Returns:
        A QueryResult object containing either the query result or an error message.
    """
    print(sql)
    error = None
    result = []
    try:
        # Execute the query using the provided database engine
        # TODO 2023-04-17: replace with BQ call
        curs = eng.connect().execute(text(sql))
        # curs = eng.query(text(sql))

        # Fetch the results and add them to the result list
        for r in curs:
            result.append({k: v for k, v in zip(curs.keys(), r)})
            if len(result) >= limit:
                break
        # print(result)
    except Exception as e:
        import traceback

        print(traceback.format_exc())
        print(e)
        try:
            error = str(e.__dict__["orig"])
        except KeyError:
            error = str(e)
    # Return the result as a QueryResult object
    return QueryResult(sql=sql, result=result, error=error)


def double_check_query(sql: str, tables_summary: str) -> Dict[str, str]:
    # TODO 2023-04-17: add further prompt engineering here based on Ben's
    prompt = f"""
{tables_summary}



{sql}


Double check the Postgres query above for common mistakes, including:
 - Wrap each column name in back ticks (`) to denote them as delimited identifiers.
 - Remembering to add `NULLS LAST` to an ORDER BY DESC clause
 - Handling case sensitivity, e.g. using ILIKE instead of LIKE
 - Ensuring the join columns are correct
 - Casting values to the appropriate type
 - Properly quoting identifiers when required (e.g. table.`Sales Amount`)
 
 Rewrite the query below if there are any mistakes. If it looks good as it is, just reproduce the original query."""

    resp = completion(prompt)
    corrected_sql = resp  # resp.json()["choices"][0]["text"]
    return {"original": sql, "corrected": corrected_sql}


def fix_sql_bug(query: QueryResult, tables_summary: str) -> Dict[str, str]:

    error_prompt = f"""
        {tables_summary}\n\n\n
        {query.sql}\n\n
        The query above produced the following error:\n\n
        {query.error}\n\n
        Rewrite the query with the error fixed:
    """

    no_result_prompt = f"""{query.sql}\n\n\n
    The query above produced no result. Try rewriting the query so it will return results:
    """

    print("OPENAI BOT ERROR, RETRYING")
    if query.error:
        prompt = error_prompt
    else:
        prompt = no_result_prompt
    print(prompt)
    resp = completion(prompt)
    corrected_sql: str = resp  # resp.json()["choices"][0]["text"]
    return {"original": query.sql, "corrected": corrected_sql}


def sql_completion_pipeline(eng, completions: List, tables_summary: str, query_fixes: List[Dict]=None) -> QueryResult:
    """
    Executes SQL queries and returns the result. If the query fails or does not return any results, attempts to fix it
    up to one time before giving up and returning an error message.

    Args:
        eng: A database engine instance.
        completions: A list of suggested SQL queries.
        tables_summary: A summary of the available database tables.
        query_fixes: A list of corrected queries.

    Returns:
        A QueryResult instance with the query result or an error message.
    """
    if query_fixes is None:
        query_fixes = []
    # Loop through suggested SQL queries
    for completion in completions:
        sql: str = completion  # ["text"]
        # Check the query for any potential errors
        corrected = double_check_query(sql, tables_summary)
        print(corrected)
        # Add the corrected query to the list of query fixes
        corrected["type"] = "sql-double-check"
        query_fixes.append(corrected)
        # Execute the query
        query_result: QueryResult = get_sql_result(eng, corrected["corrected"])

        # If the query failed or did not return any results, attempt to fix it once
        if query_result.error or not query_result.result:
            corrected = fix_sql_bug(query=query_result, tables_summary=tables_summary)
            print(corrected)
            corrected["type"] = "sql-error"
            query_fixes.append(corrected)
            query_result = get_sql_result(eng, corrected["corrected"])

        # If the query succeeded, break out of the loop and return the result
        if query_result.result:
            break
    else:
        # If none of the queries returned a valid result, construct and return an error message
        if query_result['error']:
            query_result['result'] = f"Stumped me. Here's the SQL I came up with but it had the following error: {query_result.error}."
        else:
            query_result['result'] = f"Stumped me. Here's the SQL I came up with but it didn't return a result."
    return query_result


def format_result_as_table(res):
    if res and isinstance(res, list):
        return tabulate(res, headers="keys")
    return res


@dataclass(frozen=True)
class PlotResult:
    python: str
    result: str = None
    error: str = None


def get_plot_result(py: str, data):
    print(py)
    error = None
    buf = io.BytesIO()
    result = None

    def get_data():
        return pd.DataFrame.from_records(data)

    try:
        exec(py, {"get_data": get_data})
        # print(f"[DEBUG]: INPUT DATA TO BOT: \n{get_data()}")

        plt.savefig(buf, format="png")
        buf.seek(0)
    except Exception as e:
        import traceback

        error = traceback.format_exc()
        print(error)
    # if buf:
    #    result = base64.b64encode(buf.getvalue()).decode("utf-8").replace("\n", "")
    return PlotResult(python=py, result=buf, error=error)


def fix_python_bug(result: PlotResult, it) -> dict[str, Union[str, Any]]:
    prompt = f"""
    ```
    {result.python}
    ```
    
    
    ```
    {result.error}
    ```
    
    Above is the code and the error it produced. Here is the corrected code:
    
    ```
    """

    print(f"OPENAI PYTHON ERROR, RETRYING, ATTEMPT NUMBER [{it}]")
    resp = completion(prompt)
    corrected = resp  # resp.json()["choices"][0]["text"]
    corrected = corrected.split("```")[0]
    return {"original": result.python, "corrected": corrected}


pyplot_preamble = """# Import the necessary libraries
import matplotlib.pyplot as plt
import pandas as pd


# Load the data into a pandas dataframe
records_df = get_data()

"""

plotly_preamble = """
import plotly.express as px
import pandas as pd
import streamlit as st
records_df = get_data()
"""


pyplot_exec_prefix = "plt.style.use(plt.style.library['ggplot'])\n"


def plot_completion_pipeline(completions: List, data: List, query_fixes=None, plot_lib='matplotlib') -> PlotResult:
    # TODO 2023-04-18: add docstring
    if query_fixes is None:
        query_fixes = []
    for completion in completions:
        py = completion
        py = py.split("```")[0]
        if plot_lib == 'matplotlib':
            py = pyplot_preamble + pyplot_exec_prefix + py
        elif plot_lib == 'plotly':
            py = plotly_preamble + py
        else:
            py = pyplot_preamble + pyplot_exec_prefix + py
        pr = get_plot_result(py, data)
        it = 0
        max_retries = 5  # TODO 2023-04-18: parametrise this value
        while pr.error or not pr.result:
            if it == max_retries:
                raise Exception(f"Error: tried recovering {max_retries} times from Python fixing loop, now erroring")
            # Try to fix error
            corrected = fix_python_bug(pr, it)
            print(corrected)
            corrected["type"] = "python-error"
            query_fixes.append(corrected)
            pr = get_plot_result(corrected["corrected"], data)
            it += 1
        if pr.result:
            break
    else:
        if pr.error:
            pr['result'] = f"Stumped me. Here's the SQL I came up with but it had the following error: {pr.error}."
        else:
            pr['result'] = f"Stumped me. Here's the SQL I came up with but it didn't return a result."
    return pr
