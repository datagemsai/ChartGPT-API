from typing import List, Optional
from google.cloud import bigquery
from analytics_bot_langchain.agents.agent_toolkits.bigquery.utils import get_dataset_ids
from langchain.chat_models import ChatOpenAI
from analytics_bot_langchain.agents.agent_toolkits import create_bigquery_agent
from google.oauth2 import service_account
import streamlit as st
from analytics_bot_langchain.callback_handler import CustomCallbackHandler
from langchain.callbacks.base import CallbackManager
import os
import json


callback_manager = CallbackManager([CustomCallbackHandler()])

scopes = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/bigquery",
]

if os.environ.get("gcp_service_account", False):
    credentials = service_account.Credentials.from_service_account_info(json.loads(os.environ["gcp_service_account"], strict=False)).with_scopes(scopes)
    client = bigquery.Client(credentials=credentials)
else:
    # If deployed using App Engine, use default App Engine credentials
    client = bigquery.Client()

@st.cache_resource
def get_agent(dataset_ids: Optional[List] = None):
    if dataset_ids:
        available_dataset_ids = get_dataset_ids(client=client)
        invalid_dataset_ids = set(dataset_ids) - set(available_dataset_ids)
        assert not invalid_dataset_ids, f"Dataset IDs {invalid_dataset_ids} not available"
    return create_bigquery_agent(
        ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5, request_timeout=180),
        bigquery_client=client,
        dataset_ids=dataset_ids,
        verbose=True,
        callback_manager=callback_manager,
        max_iterations=5,
        max_execution_time=120,  # seconds
        early_stopping_method="generate",
    )
