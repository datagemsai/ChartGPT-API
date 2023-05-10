import inspect
import re
from typing import Union

from langchain.agents.agent import AgentOutputParser
from analytics_bot_langchain.agents.mrkl.prompt import FORMAT_INSTRUCTIONS
from langchain.schema import AgentAction, AgentFinish, OutputParserException

import logging
logger = logging.getLogger(__name__)


FINAL_ANSWER_ACTION = "Final Answer:"
FAILURE_ACTION = "Failure:"

class CustomOutputParser(AgentOutputParser):
    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
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
                .strip('"')
                .removeprefix("```python")
                .strip()
                .removesuffix("```")
                .strip()
            )
            logger.debug(f"CustomOutputParser group 1: {match.group(1)}")
            logger.debug(f"CustomOutputParser group 2: {match.group(2)}")
            logger.debug(f"CustomOutputParser group 3: {match.group(3)}")
            return AgentAction(tool="python_repl_ast", tool_input=code, log=llm_output)
        elif FAILURE_ACTION in llm_output:
            raise OutputParserException(llm_output)
        elif FINAL_ANSWER_ACTION in llm_output:
            return AgentFinish(
                return_values={"output": llm_output.split(FINAL_ANSWER_ACTION)[-1].strip()},
                log=llm_output
            )
        else:
            return AgentAction(tool="python_repl_ast", tool_input=inspect.cleandoc('''
            display("""{llm_output}""")
            '''.format(llm_output=llm_output.replace('"', "\'"))), log=llm_output)
            # raise OutputParserException(llm_output)
