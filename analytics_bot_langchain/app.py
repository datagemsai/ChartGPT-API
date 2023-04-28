from google.cloud import bigquery
from langchain.chat_models import ChatOpenAI
from analytics_bot_langchain.agents.agent_toolkits import create_bigquery_agent
from google.oauth2 import service_account
import streamlit as st
from analytics_bot_langchain.callback_handler import CustomCallbackHandler
from langchain.callbacks.base import CallbackManager


callback_manager = CallbackManager([CustomCallbackHandler()])
credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"]).with_scopes([
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/bigquery",
])
client = bigquery.Client(credentials=credentials)
agent = create_bigquery_agent(
    ChatOpenAI(model="gpt-3.5-turbo", temperature=0),
    bigquery_client=client,
    verbose=True,
    callback_manager=callback_manager,
    max_iterations=5,
    max_execution_time=120,  # seconds
    early_stopping_method="generate",
)


def run(question) -> bool:
    agent.run(question)
    return True
