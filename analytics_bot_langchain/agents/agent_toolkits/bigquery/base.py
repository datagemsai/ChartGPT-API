from typing import Any, Dict, List, Optional, Tuple, Union
import inspect
import re
import logging
from pydantic import Field

from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from langchain.agents.agent import AgentExecutor, AgentOutputParser
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain.callbacks.base import BaseCallbackManager
from langchain.chains.llm import LLMChain
from langchain.llms.base import BaseLLM
from analytics_bot_langchain.tools.python.tool import PythonAstREPLTool
from pydantic import root_validator
from analytics_bot_langchain.agents.agent_toolkits.bigquery.utils import get_tables_summary
from analytics_bot_langchain.agents.agent_toolkits.bigquery.prompt import PREFIX, SUFFIX
from langchain.schema import (
    AgentAction,
    BaseMessage
)
from analytics_bot_langchain.agents.mrkl.output_parser import CustomOutputParser
from analytics_bot_langchain.agents.mrkl.prompt import FORMAT_INSTRUCTIONS


logger = logging.getLogger(__name__)

python_tool_description = (
    "A Python shell. Use this to execute python commands. "
    "Input should be a valid python command. "
    "When using this tool, sometimes output is abbreviated - "
    "make sure it does not look abbreviated before using it in your answer."
    # Custom
    "Do not try to check the output."
)

class CustomAgent(ZeroShotAgent):
    output_parser: AgentOutputParser = Field(default_factory=CustomOutputParser)

    @property
    def observation_prefix(self) -> str:
        """Prefix to append the observation with."""
        return "Observation: "

    @property
    def llm_prefix(self) -> str:
        """Prefix to append the llm call with."""
        return "Thought: "

    @root_validator(allow_reuse=True)
    def validate_prompt(cls, values: Dict) -> Dict:
        """Validate that prompt matches format."""
        prompt = values["llm_chain"].prompt
        if "agent_scratchpad" not in prompt.input_variables:
            logger.warning(
                "`agent_scratchpad` should be a variable in prompt.input_variables."
                " Did not find it, so adding it at the end."
            )
            prompt.input_variables.append("agent_scratchpad")
            if isinstance(prompt, PromptTemplate):
                prompt.template += "\n{agent_scratchpad}"
            elif isinstance(prompt, FewShotPromptTemplate):
                prompt.suffix += "\n{agent_scratchpad}"
            else:
                raise ValueError(f"Got unexpected prompt type {type(prompt)}")
        return values
    
    def _construct_scratchpad(
        self, intermediate_steps: List[Tuple[AgentAction, str]]
    ) -> Union[str, List[BaseMessage]]:
        """Construct the scratchpad that lets the agent continue its thought process."""
        thoughts = ""
        for action, observation in intermediate_steps:
            character_limit = 1000
            if len(str(observation)) > character_limit:
                observation = str(observation)[:character_limit]
            thoughts += action.log
            thoughts += f"\n{self.observation_prefix}{observation}\n{self.llm_prefix}"
        return thoughts


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
    **kwargs: Any,
) -> AgentExecutor:
    if input_variables is None:
        input_variables = ["tables_summary", "input", "agent_scratchpad"]
    tables_summary = get_tables_summary(client=bigquery_client, dataset_ids=dataset_ids)
    python_tool = PythonAstREPLTool(locals={"tables_summary": tables_summary, "bigquery_client": bigquery_client})
    python_tool.description = python_tool_description

    def query_post_processing(query: str) -> str:
        prefix = inspect.cleandoc("""
        # Add custom imports and config here for agent
        import streamlit as st
        """)
        query = prefix + "\n" + query
        query = re.sub(".*client =.*\n?", "client = bigquery_client", query)
        query = re.sub(".*bigquery_client =.*\n?", "", query)
        query = query.replace("print", "st.write")
        return query

    python_tool.query_post_processing = query_post_processing

    tools = [python_tool]
    prompt = ZeroShotAgent.create_prompt(
        tools, prefix=prefix, suffix=suffix, format_instructions=FORMAT_INSTRUCTIONS, input_variables=input_variables
    )
    tables_summary_escaped = "{" + str(tables_summary) + "}"
    partial_prompt = prompt.partial(
        tables_summary=tables_summary_escaped,
    )
    llm_chain = LLMChain(
        llm=llm,
        prompt=partial_prompt,
        callback_manager=callback_manager,
    )
    tool_names = [tool.name for tool in tools]
    agent = CustomAgent(llm_chain=llm_chain, allowed_tools=tool_names, **kwargs)
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
    )
