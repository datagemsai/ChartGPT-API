import json
import os
from typing import List, Optional

from google.cloud import bigquery
from google.oauth2 import service_account
from langchain.callbacks.manager import CallbackManager
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

import app
from app.config.datasets import Dataset
from chartgpt.agents.agent_toolkits import create_bigquery_agent
from chartgpt.agents.agent_toolkits.bigquery.utils import get_dataset_ids
from chartgpt.callback_handler import CustomCallbackHandler

OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

callback_manager = CallbackManager([CustomCallbackHandler()])

scopes = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/bigquery",
]

if app.ENV == "LOCAL":
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(os.environ["GCP_SERVICE_ACCOUNT"], strict=False)
    ).with_scopes(scopes)
    client = bigquery.Client(credentials=credentials)
else:
    # If deployed using App Engine, use default App Engine credentials
    client = bigquery.Client()


def get_agent(
    secure_execution: bool = True,
    temperature: float = 0.0,
    datasets: Optional[List[Dataset]] = None,
    callbacks: Optional[List] = None,
):
    if datasets:
        available_dataset_ids = get_dataset_ids(client=client)
        invalid_dataset_ids = set([dataset.id for dataset in datasets]) - set(
            available_dataset_ids
        )
        assert (
            not invalid_dataset_ids
        ), f"Dataset IDs {invalid_dataset_ids} not available"
    return create_bigquery_agent(
        ChatOpenAI(
            model_name=OPENAI_MODEL,
            streaming=True,
            temperature=temperature,
            request_timeout=180,
            callbacks=callbacks,
        ),
        bigquery_client=client,
        datasets=datasets,
        # https://github.com/hwchase17/langchain/issues/6083
        verbose=False,
        callback_manager=callback_manager,
        max_iterations=10,
        max_execution_time=120,  # seconds
        early_stopping_method="generate",
        return_intermediate_steps=True,
        memory=ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            input_key="input",
            output_key="output",
        ),
        secure_execution=secure_execution,
    )
