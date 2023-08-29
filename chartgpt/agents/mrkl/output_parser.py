import re
from typing import Union
import streamlit as st
from langchain.agents.agent import AgentOutputParser
from chartgpt.agents.mrkl.prompt import FORMAT_INSTRUCTIONS
from langchain.schema import AgentAction, AgentFinish, OutputParserException

import logging
logger = logging.getLogger(__name__)


FINAL_ANSWER_ACTION = "Analysis complete:"
FAILURE_ACTION = "Analysis failed:"
THOUGHT = "Thought:"

class CustomOutputParser(AgentOutputParser):
    """Output parser for the BigQuery agent.
    This parser is used to parse the output of the BigQuery agent.
    """
    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        if "messages" not in st.session_state:
            return AgentFinish(return_values={"output": llm_output}, log=llm_output)
        regex = (
            r"(.*?)\s*\d*\s*(```python|```)\s*\d*\s*(.*?)\s*\d*\s*```"
        )
        match = re.search(regex, llm_output, re.MULTILINE | re.DOTALL)

        if match:
            code = match.group(3)
            # Clean up the code
            code = (
                code
                .strip()
                .removeprefix("```python")
                .strip()
                .removesuffix("```")
                .strip()
            )
            thought = (
                match
                .group(1)
                .removesuffix("Action Input:")
                .strip()
            )
            st.session_state["messages"].append({"role": "assistant", "content": thought})
            return AgentAction(tool="python_repl_ast", tool_input=code, log=llm_output)
        elif FAILURE_ACTION in llm_output:
            raise OutputParserException(llm_output)
        elif FINAL_ANSWER_ACTION in llm_output:
            return AgentFinish(
                return_values={"output": llm_output.split(FINAL_ANSWER_ACTION)[-1].strip()},
                log=llm_output
            )
        elif THOUGHT in llm_output:
            st.session_state["messages"].append({"role": "assistant", "content": llm_output})
            return AgentAction(tool="python_repl_ast", tool_input="", log=llm_output)
        else:
            st.session_state["messages"].append({"role": "assistant", "content": llm_output})
            return AgentAction(tool="python_repl_ast", tool_input="", log=llm_output)
