from typing import Any, List, Optional

from langchain.agents.agent import AgentExecutor
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain.callbacks.base import BaseCallbackManager
from langchain.chains.llm import LLMChain
from langchain.llms.base import BaseLLM
from langchain.tools.python.tool import PythonAstREPLTool

from analytics_bot_langchain.agents.agent_toolkits.bigquery.utils import get_tables_summary
from analytics_bot_langchain.agents.agent_toolkits.bigquery.prompt import PREFIX, SUFFIX


python_tool_description = (
    "A Python shell. Use this to execute python commands. "
    "Input should be a valid python command. "
    "When using this tool, sometimes output is abbreviated - "
    "make sure it does not look abbreviated before using it in your answer."
    # Custom
    "Do not try to check the output."
)

def create_bigquery_agent(
    llm: BaseLLM,
    bigquery_client: Any,
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
        input_variables = ["tables_summary", "project_id", "input", "agent_scratchpad"]
    tables_summary = get_tables_summary(client=bigquery_client)
    python_tool = PythonAstREPLTool(locals={"tables_summary": tables_summary, "bigquery_client": bigquery_client})
    python_tool.description = python_tool_description
    tools = [python_tool]
    prompt = ZeroShotAgent.create_prompt(
        tools, prefix=prefix, suffix=suffix, input_variables=input_variables
    )
    tables_summary_escaped = "{" + str(tables_summary) + "}"
    partial_prompt = prompt.partial(
        tables_summary=tables_summary_escaped,
        project_id=bigquery_client.project,
    )
    llm_chain = LLMChain(
        llm=llm,
        prompt=partial_prompt,
        callback_manager=callback_manager,
    )
    tool_names = [tool.name for tool in tools]
    agent = ZeroShotAgent(llm_chain=llm_chain, allowed_tools=tool_names, **kwargs)
    return AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=verbose,
        return_intermediate_steps=return_intermediate_steps,
        max_iterations=max_iterations,
        max_execution_time=max_execution_time,
        early_stopping_method=early_stopping_method,
    )
