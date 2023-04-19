

from typing import List
from .base import completion


question = {
    'question': None,
    'route': None,
    'slack_channel': None,
    'email_sender': None,
    'message_id': None
}


def process_questions(questions: List, sql_requests=List, chart_requests=List, data_requests=List):
    prompt = """Classify the following message according to whether it is a SQL query, a data request, or a chart request. Examples:

    message: how many new customers were added last year?
    class: data request
    
    message: show me the trend in house prices over the last 5 years
    class: chart request
    
    message: plot a graph of miles vs heartrate, grouped by age group
    class: chart request
    
    message: SELECT * FROM customers ORDER BY date
    class: sql query
    
    message: {question}
    class: 
    """
    for q in questions:
        prompt = prompt.format(question=q["question"])
        resp = completion(prompt)
        # q["route"] = resp  # resp.json()["choices"][0]["text"]
        # route = resp  # resp.json()["choices"][0]["text"]
        q['route'] = resp
        # print(q)  # TODO improve logging of request
        print(f"INPUT QUESTION: [{q['question']}]")  # TODO improve logging of request
        if "sql" in q["route"].lower():
            sql_requests.append(q)
        elif "chart" in q["route"].lower():
            chart_requests.append(q)
        elif "data" in q["route"].lower():
            data_requests.append(q)
        else:
            print(f"Unknown route!")
            data_requests.append(q)

