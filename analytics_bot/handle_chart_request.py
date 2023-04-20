from dataclasses import dataclass, asdict, replace
from typing import Dict, List

from analytics_bot.base import table_info, completion, double_check_query, fix_sql_bug, get_sql_result, sql_completion_pipeline, plot_completion_pipeline, pyplot_preamble
from langchain.sql_database import SQLDatabase

from analytics_bot.make_plot import plot_charts


def sql_chart_completion(eng, question, n, tables_summary) -> List:
    # TODO 2023-04-17: add back 'n' functionality support which was passed as params.update(kwargs) to OpenAI api
    #  so likely the top n replies from API agent.
    question = question.strip()
    # print(f"TABLES SUMMARY INPUT TO SQL CHART COMPLETION: \n{tables_summary}\n\nEND OF TABLE SUMMARY")
    prompt = f"""
{tables_summary}\n\n
As a senior analyst, given the above schemas and data, write a detailed and correct Postgres sql query to produce data for the following requested chart:\n
"{question}"\n
Do not perform any JOIN of tables. Be very selective in the columns of interest.
"""
    # Comment the query with your logic.

    resp = completion(prompt, n=n)
    print(f"OPENAI SQL CHAT RESPONSE: [{resp}]")
    return resp


def handle_chart_request(eng, request: Dict, tables_summary: str, query_fixes=None) -> Dict:
    question = request["question"]
    resp = sql_chart_completion(eng=eng, question=question, n=5, tables_summary=tables_summary)  # returns top n choices of agent replies
    qr = sql_completion_pipeline(eng=eng, completions=resp, tables_summary=tables_summary, query_fixes=query_fixes)
    # qr = sql_completion_pipeline(eng=eng, completions=resp.json()["choices"], tables_summary=tables_summary, query_fixes=query_fixes)
    request["sql_result"] = asdict(qr)
    return request


def process_chart_requests(eng, chart_requests: List[Dict], tables_summary: str, query_fixes=None) -> list:
    sql_results = []
    for request in chart_requests:
        sql_results.append(handle_chart_request(eng, request, tables_summary, query_fixes))

    results = []
    # TODO 2023-04-17: now add the make_plot logic
    plot_charts(sql_results=sql_results, tables_summary=tables_summary)


    return results
