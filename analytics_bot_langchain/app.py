import json
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
import dotenv
dotenv.load_dotenv()

callback_manager = CallbackManager([CustomCallbackHandler()])
credentials = service_account.Credentials.from_service_account_info(json.loads(os.environ["gcp_service_account"], strict=False)).with_scopes([
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/bigquery",
])
client = bigquery.Client(credentials=credentials)


@st.cache_resource
def get_agent(dataset_ids: Optional[List] = None):
    if dataset_ids:
        available_dataset_ids = get_dataset_ids(client=client)
        invalid_dataset_ids = set(dataset_ids) - set(available_dataset_ids)
        assert not invalid_dataset_ids, f"Dataset IDs {invalid_dataset_ids} not available"
    return create_bigquery_agent(
        ChatOpenAI(model="gpt-3.5-turbo", temperature=0),
        bigquery_client=client,
        dataset_ids=dataset_ids,
        verbose=True,
        callback_manager=callback_manager,
        max_iterations=5,
        max_execution_time=120,  # seconds
        early_stopping_method="generate",
    )
