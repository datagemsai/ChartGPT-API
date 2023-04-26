from google.cloud import bigquery
from langchain.chat_models import ChatOpenAI
from analytics_bot_langchain.agents.agent_toolkits import create_bigquery_agent
from google.oauth2 import service_account
import streamlit as st


credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"]).with_scopes([
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/bigquery",
])
client = bigquery.Client(credentials=credentials)
agent = create_bigquery_agent(ChatOpenAI(temperature=0), bigquery_client=client, verbose=True)


def run(question) -> bool:
    agent.run(question)
    return True
