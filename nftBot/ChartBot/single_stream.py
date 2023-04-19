
from typing import List
from dotenv import load_dotenv
from google.cloud import bigquery
import google.auth
from .handle_chart_request import process_chart_requests
from .handle_data_request import process_data_requests
from .handle_sql_request import process_sql_requests
from .route_question import question, process_questions
from sqlalchemy.engine import create_engine
from langchain.sql_database import SQLDatabase

# Load environment variables from the .env file
load_dotenv()


def tables_summary(eng):
    # Set the environment variable GOOGLE_APPLICATION_CREDENTIALS to the path of the JSON file that contains your service account key
    credentials, _ = google.auth.default(
        scopes=[
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/bigquery",
        ]
    )

    return SQLDatabase(engine=eng).get_table_info(table_names=None).replace("CREATE", "")


def run(dataset_id="nft_lending_aggregated_borrow", project_id="psychic-medley-383515", questions=None, sql_requests=None, data_requests=None, chart_requests=None) -> bool:
    if chart_requests is None:
        chart_requests = []
    if sql_requests is None:
        sql_requests = []
    if data_requests is None:
        data_requests = []
    if questions is None:
        questions = []
    eng = create_engine(f"bigquery://{project_id}/{dataset_id}")
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
