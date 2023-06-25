from typing import Any, Dict, List, Optional
import inspect
import re
import logging

from langchain.agents.agent import AgentExecutor
from chartgpt.agents.mrkl.base import CustomAgent
from langchain.callbacks.base import BaseCallbackManager
from langchain.chains.llm import LLMChain
from langchain.llms.base import BaseLLM
from chartgpt.tools.python.tool import PythonAstREPLTool
from chartgpt.agents.agent_toolkits.bigquery.utils import get_tables_summary, get_example_query
from chartgpt.agents.agent_toolkits.bigquery.prompt import PREFIX, SUFFIX
from chartgpt.agents.mrkl.output_parser import CustomOutputParser


logger = logging.getLogger(__name__)


def create_bigquery_agent(
    llm: BaseLLM,
    bigquery_client: Any,
    dataset_ids: Optional[List] = None,
    callback_manager: Optional[BaseCallbackManager] = None,
    prefix: str = PREFIX,
    suffix: str = SUFFIX,
    input_variables: Optional[List[str]] = None,
    verbose: bool = False,
    return_intermediate_steps: bool = False,
    max_iterations: Optional[int] = 15,
    max_execution_time: Optional[float] = None,
    early_stopping_method: str = "force",
    agent_executor_kwargs: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> AgentExecutor:
    tables_summary = get_tables_summary(client=bigquery_client, dataset_ids=dataset_ids)
    example_query = get_example_query(client=bigquery_client, dataset_ids=dataset_ids)
    python_tool = PythonAstREPLTool(locals={"tables_summary": tables_summary, "bigquery_client": bigquery_client})

    def query_post_processing(query: str) -> str:
        query = query.replace("print(", "display(")
        imports = inspect.cleandoc("""
        # Add custom imports and config here for agent
        import streamlit as st
        import plotly.express as px
        import plotly.graph_objects as go
        import pandas as pd

        def display(*args):
            import streamlit as st
            st.write(*args)
            return args
        """)
        query = imports + "\n" + query
        query = re.sub(".*client =.*\n?", "client = bigquery_client", query)
        query = re.sub(".*bigquery_client =.*\n?", "", query)
        return query

    python_tool.query_post_processing = query_post_processing
    tools = [python_tool]

    if input_variables is None:
        input_variables = ["tables_summary", "example_query", "input", "agent_scratchpad"]

    prompt = CustomAgent.create_prompt(
        tools,
        prefix=prefix,
        suffix=suffix,
        input_variables=input_variables,
    )
    tables_summary_escaped = "{" + str(dict(tables_summary)) + "}"
    partial_prompt = prompt.partial(
        tables_summary=tables_summary_escaped,
        example_query=example_query,
    )
    llm_chain = LLMChain(
        llm=llm,
        prompt=partial_prompt,
        callback_manager=callback_manager,
    )
    tool_names = [tool.name for tool in tools]
    agent = CustomAgent(
        llm_chain=llm_chain,
        allowed_tools=tool_names,
        callback_manager=callback_manager,
        **kwargs,
    )
    return AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=verbose,
        return_intermediate_steps=return_intermediate_steps,
        max_iterations=max_iterations,
        max_execution_time=max_execution_time,
        early_stopping_method=early_stopping_method,
        callback_manager=callback_manager,
        output_parser=CustomOutputParser,
        **(agent_executor_kwargs or {}),
    )
