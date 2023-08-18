from api.chartgpt import get_valid_sql_query


def generate_sql(body):
    question = body['question']
    
    # Logic to generate SQL query based on question
    query = get_valid_sql_query(question)

    return {"query": query}, 200
