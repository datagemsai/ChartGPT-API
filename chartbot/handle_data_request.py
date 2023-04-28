

from dataclasses import asdict

from . import base
from chartbot.base import sql_completion_pipeline



def process_data_requests(eng, data_requests, query_fixes=None, tables_summary=str):
    """
    Processes a list of data requests by generating a SQL query for each request using GPT-3's SQL completion API,
    executing the query using the `sql_completion_pipeline()` function, and appending the resulting SQL query
    result to the original data request.

    Args:
        data_requests: A list of data requests, each containing a question for which an SQL query should be generated.
        query_fixes: A list of corrected queries.

    Returns:
        A list of data requests, each with an appended "sql_result" key containing the SQL query result or an error message.
        :param eng:
    """
    if query_fixes is None:
        query_fixes = []

    # Initialize empty list to hold processed data requests
    results = []

    # Loop through each data request
    for request in data_requests:
        # Get the question from the data request
        q = request["question"]

        # Get a suggested SQL query for the question using GPT-3's SQL completion API
        resp = base.sql_completion(question=q, n=1, tables_summary=tables_summary)

        # Execute the SQL query using the `sql_completion_pipeline()` function
        # qr = sql_completion_pipeline(eng=eng, completions=resp.json()["choices"], tables_summary=tables_summary, query_fixes=query_fixes)
        qr = sql_completion_pipeline(eng=eng, completions=resp, tables_summary=tables_summary, query_fixes=query_fixes)

        # Append the resulting SQL query to the original data request
        request["sql_result"] = asdict(qr)

        # Append the processed data request to the `results` list
        results.append(request)

    # Return the list of processed data requests
    return results



