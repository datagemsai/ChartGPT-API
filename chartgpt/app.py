import json
import os
from typing import List, Optional

from langchain.callbacks.manager import CallbackManager
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

import app
from api.connectors.bigquery import bigquery_client
from app.config.datasets import Dataset
from chartgpt.agents.agent_toolkits import create_bigquery_agent
from chartgpt.agents.agent_toolkits.bigquery.utils import get_dataset_ids
from chartgpt.callback_handler import CustomCallbackHandler

OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

callback_manager = CallbackManager([CustomCallbackHandler()])


def get_agent(
    secure_execution: bool = True,
    temperature: float = 0.0,
    datasets: Optional[List[Dataset]] = None,
    callbacks: Optional[List] = None,
):
    return create_bigquery_agent(
        ChatOpenAI(
            model_name=OPENAI_MODEL,
            streaming=True,
            temperature=temperature,
            request_timeout=180,
            callbacks=callbacks,
        ),
        bigquery_client=bigquery_client,
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
