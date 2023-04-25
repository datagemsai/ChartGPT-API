

from dataclasses import asdict
from typing import Dict, List

from analytics_bot.base import sql_completion_pipeline, sql_completion
from analytics_bot.make_plot import plot_charts


def handle_chart_request(eng, request: Dict, tables_summary: str, query_fixes=None) -> Dict:
    question = request["question"]
    resp = sql_completion(question=question, n=5, tables_summary=tables_summary)  # returns top n choices of agent replies
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


