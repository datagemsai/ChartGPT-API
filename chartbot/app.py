from typing import Optional
from chartbot.handle_chart_request import process_chart_requests
from chartbot.handle_data_request import process_data_requests
from chartbot.handle_sql_request import process_sql_requests
from chartbot.route_question import process_questions
from chartbot.base import tables_summary
from sqlalchemy.engine import create_engine
import os
import openai
import json


# Load secrets / environment variables from .streamlit directory secrets.toml
openai.api_key = os.environ["OPENAI_API_KEY"]
GCP_SERVICE_ACCOUNT = json.loads(os.environ["GCP_SERVICE_ACCOUNT"], strict=False)


def run(dataset_id, project_id: Optional[str] = None, questions=None, question=None, sql_requests=None, data_requests=None, chart_requests=None) -> bool:
    if chart_requests is None:
        chart_requests = []
    if sql_requests is None:
        sql_requests = []
    if data_requests is None:
        data_requests = []
    if (questions is None) and (question is None):
        questions = []
    elif (questions is None) and not (question is None):
        questions = [{'question': question}]

    project_id = project_id if project_id else GCP_SERVICE_ACCOUNT["project_id"]
    eng = create_engine(f"bigquery://{project_id}/{dataset_id}", credentials_info=GCP_SERVICE_ACCOUNT)

    process_questions(questions=questions, sql_requests=sql_requests, chart_requests=chart_requests, data_requests=data_requests)
    sql_agent_answers = process_sql_requests(eng=eng, sql_requests=sql_requests)
    data_agent_answers = process_data_requests(eng=eng, data_requests=data_requests, tables_summary=tables_summary(eng))
    chart_agent_answers = process_chart_requests(eng=eng, chart_requests=chart_requests, tables_summary=tables_summary(eng))

    for answer, answer_type in zip([sql_agent_answers, chart_agent_answers, data_agent_answers], ["sql", "chart", "data"]):
        if not answer:
            continue
        print(f"{answer_type}: \n")
        for reply in answer:
            print(f"{reply}\n\n")

    return True
