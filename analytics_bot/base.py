import os
from dataclasses import dataclass, replace
from typing import Dict, List, Union, Any
import requests
from sqlalchemy import text
import io
from langchain import PromptTemplate
from langchain.sql_database import SQLDatabase
from langchain.chat_models.openai import ChatOpenAI
from langchain.chains import LLMChain
import openai
import inspect


def tables_summary(eng):
    return SQLDatabase(engine=eng).get_table_info(table_names=None).replace("CREATE", "")

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

def query_davinci(prompt, **kwargs) -> str:
    api_key = os.environ['OPENAI_API_KEY']
    params = {
        "prompt": prompt,
        "model": "text-davinci-003",
        "max_tokens": 500,
        "temperature": 0.8,
    }
    params.update(kwargs)
    resp = requests.post(
        "https://api.openai.com/v1/completions",
        json=params,
        headers={"Authorization": f"Bearer {api_key}"},
    )
    if not resp.ok:
        # print(resp.json())
        resp.raise_for_status()
    return resp.json()["choices"][0]["text"]


def completion(prompt, **kwargs):
    return query_davinci(prompt=prompt, **kwargs)


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
    sql = sql.replace('\"', '`')
    # sql = sql.replace("\'", "`")
    # TODO 2023-04-24: move from prints to proper logging.
    # print(f"GET_SQL_RESULT: PERFORM THIS SQL QUERY: \n {sql}")
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
        # TODO 2023-04-24: move from prints to proper logging.
        # print(result)
    except Exception as e:
        import traceback

        # print(traceback.format_exc())
        # print(e)
        try:
            error = str(e.__dict__["orig"])
        except KeyError:
            error = str(e)
    # Return the result as a QueryResult object
    return QueryResult(sql=sql, result=result, error=error)


def double_check_query(sql: str, tables_summary: str) -> Dict[str, str]:
    # TODO 2023-04-17: add further prompt engineering here based on Ben's
    print(f"\nTHIS IS THE SQL INPUT TO DOUBLE CHECK: \n\n{sql}")
    # {tables_summary}
    prompt = f"""
{sql}

Double check the Postgres query above for common mistakes, including:
 - Wrap each column name in back ticks (`) to denote them as delimited identifiers.
 - Remembering to add `NULLS LAST` to an ORDER BY DESC clause
 - Properly quoting identifiers when required (e.g. table.`Sales Amount`)
 - Do not compute median, averages or any other aggregation at this step, simply select the relevant columns. Do not truncate dates. Do not use WHERE clause.
Rewrite the query below if there are any mistakes. If it looks good as it is, just return the original query.
"""
    # ONLY check the query for the above guidelines, do not change its logic whatsoever.
    # - Do not JOIN any table.
    # Rewrite the query below if there are any mistakes. If it looks good as it is, just reproduce the original query.
    # - Handling case sensitivity, e.g. using ILIKE instead of LIKE
    # - Casting values to the appropriate type
    # TODO 2023-04-24: move from prints to proper logging.
    # print(f"\n\nINPUT PROMPT FOR DOUBLE CHECKING SQL QUERY RESULT: \n\n```\n{prompt}\n```\n\nEND OF PROMPT\n\n")
    prompt = inspect.cleandoc(prompt)
    resp = completion(prompt)
    # print(f"\n\nDOUBLED CHECKED SQL QUERY RESULT: \n\n```\n{resp}\n```\n\nEND OF DOUBLE CHECKED SQL QUERY RESULT\n\n")
    # print("CLEANING HACK: REMOVE DOUBLE QUOTES FROM SQL REPLY")
    resp = resp.replace('\"', '`')
    # resp = resp.replace("\'", '`')
    if "SELECT" in resp:
        corrected_sql = resp  # resp.json()["choices"][0]["text"]
    else:
        corrected_sql = sql
    return {"original": sql, "corrected": corrected_sql}


def fix_sql_bug(query: QueryResult, tables_summary: str) -> Dict[str, str]:

    error_prompt = f"""
        {tables_summary}\n\n\n
        {query.sql}\n\n
        The query above produced the following error:\n\n
        {query.error}\n\n
        Rewrite the query with the error fixed:
    """
    error_prompt = inspect.cleandoc(error_prompt)

    no_result_prompt = f"""{query.sql}\n\n\n
    The query above produced no result. Try rewriting the query so it will return results:
    """
    no_result_prompt = inspect.cleandoc(no_result_prompt)
    # TODO 2023-04-24: move from prints to proper logging.
    # print("OPENAI BOT ERROR, RETRYING")
    if query.error:
        prompt = error_prompt
    else:
        prompt = no_result_prompt
    # TODO 2023-04-24: move from prints to proper logging.
    # print(prompt)
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
        # TODO 2023-04-24: move from prints to proper logging.
        # print(corrected)
        # Add the corrected query to the list of query fixes
        corrected["type"] = "sql-double-check"
        query_fixes.append(corrected)
        # Execute the query
        query_result: QueryResult = get_sql_result(eng, corrected["corrected"])

        # If the query failed or did not return any results, attempt to fix it once
        if query_result.error or not query_result.result:
            corrected = fix_sql_bug(query=query_result, tables_summary=tables_summary)
            # TODO 2023-04-24: move from prints to proper logging.
            # print(corrected)
            corrected["type"] = "sql-error"
            query_fixes.append(corrected)
            query_result = get_sql_result(eng, corrected["corrected"])

        # If the query succeeded, break out of the loop and return the result
        if query_result.result:
            break
    else:
        # If none of the queries returned a valid result, construct and return an error message
        if query_result.error:
            query_result = replace(
                query_result,
                result=f"Stumped me. Here's the SQL I came up with but it had the following error: {query_result.error}.",
            )
        else:
            query_result = replace(
                query_result,
                result=f"Stumped me. Here's the SQL I came up with but it didn't return a result.",
            )
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
    # TODO 2023-04-24: move from prints to proper logging.
    # print(f"OPENAI PYTHON ERROR, RETRYING, ATTEMPT NUMBER [{it}]")
    # print(f"THIS IS THE INPUT PROMPT TO OPENAI PYTHON AFTER ERROR \n\n{prompt}\n\nEND OF PROMPT")
    prompt = inspect.cleandoc(prompt)
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


def sql_completion(question, n, tables_summary) -> List:
    # TODO 2023-04-17: add back 'n' functionality support which was passed as params.update(kwargs) to OpenAI api
    #  so likely the top n replies from API agent.
    question = question.strip()
    # print(f"TABLES SUMMARY INPUT TO SQL CHART COMPLETION: \n{tables_summary}\n\nEND OF TABLE SUMMARY")
    prompt = f"""
{tables_summary}\n\n
As a senior analyst, given the above schemas and data, write a detailed and correct Postgres sql query to produce data for the following request. 
Only SELECT columns from a single table, never join tables. Do not use single or double quotes when renaming columns.:\n
"{question}"\n
Do not compute median, averages or any other aggregation at this step, simply select the relevant columns.
"""
    # Be very selective in the columns of interest.
    # Comment the query with your logic.
    prompt = inspect.cleandoc(prompt)
    resp = completion(prompt)
    # TODO 2023-04-24: move from prints to proper logging.
    # print(f"OPENAI SQL CHAT RESPONSE: \n{resp}\n")
    # print("CLEANING HACK: REMOVE DOUBLE QUOTES FROM SQL REPLY")
    resp = resp.replace('\"', '`')
    # resp = resp.replace("\'", '`')
    # return a list of responses to account when we add back the top n choices
    return [resp]
