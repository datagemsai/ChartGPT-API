import re
from typing import Union

from langchain.agents.agent import AgentOutputParser
from analytics_bot_langchain.agents.mrkl.prompt import FORMAT_INSTRUCTIONS
from langchain.schema import AgentAction, AgentFinish, OutputParserException

FINAL_ANSWER_ACTION = "Final Answer:"
FAILURE_ACTION = "Failure:"


class CustomOutputParser(AgentOutputParser):
    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        if FAILURE_ACTION in llm_output:
            # Catch case where Failure and Final Output are returned
            raise OutputParserException(llm_output)
        if FINAL_ANSWER_ACTION in llm_output:
            return AgentFinish(
                return_values={"output": llm_output.split(FINAL_ANSWER_ACTION)[-1].strip()},
                log=llm_output
            )
        # \s matches against tab/newline/whitespace
        regex = (
            r"Action\s*\d*\s*:[\s]*(.*?)[\s]*Action\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        )
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise OutputParserException(llm_output)
        action = match.group(1).strip()
        action_input = match.group(2)
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)
