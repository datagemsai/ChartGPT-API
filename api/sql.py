from api.chartgpt import SQLExecutionResult, get_valid_sql_query


def generate_sql(body):
    question = body["question"]

    # Logic to generate SQL query based on question
    query_result: SQLExecutionResult = get_valid_sql_query(question)

    return {"query": query_result.query}, 200
