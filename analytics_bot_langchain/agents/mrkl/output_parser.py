import inspect
import logging
import re
from typing import Union

from langchain.agents.agent import AgentOutputParser
from analytics_bot_langchain.agents.mrkl.prompt import FORMAT_INSTRUCTIONS
from langchain.schema import AgentAction, AgentFinish, OutputParserException

from app.utils import setup_logger

FINAL_ANSWER_ACTION = "Final Answer:"
FINAL_ANSWER_ACTIONS = [FINAL_ANSWER_ACTION]#FINAL_ANSWER_ACTION] # , 'resulting', 'plotted', 'successfully plot']
FAILURE_ACTION = "Failure:"
logger = setup_logger()
SPACING_BETWEEN_COMMANDS = "\n\n\n\n"

class CustomOutputParser(AgentOutputParser):
    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        regex = (
            r"(```python|```)(.*?)```"
        )
        match = re.search(regex, llm_output, re.MULTILINE | re.DOTALL)

        if match:
            code = match.group(2)
            code = code.strip(" ").strip('"')
            logger.info(f"Agent Python input to python_REPL:{code}{SPACING_BETWEEN_COMMANDS}")
            return AgentAction(tool="python_repl_ast", tool_input=code, log=llm_output)
        elif FAILURE_ACTION in llm_output:
            # logger.error(f"FAILURE_ACTION [{FAILURE_ACTION}] in llm_output: \n{llm_output}{SPACING_BETWEEN_COMMANDS}")
            raise OutputParserException(llm_output)
        elif any(final_action in llm_output for final_action in FINAL_ANSWER_ACTIONS):
            # logger.info(f"FINAL_ANSWER_ACTION [{FINAL_ANSWER_ACTION}] in llm_output: \n{llm_output}{SPACING_BETWEEN_COMMANDS}")
            return AgentFinish(
                return_values={"output": llm_output.split(FINAL_ANSWER_ACTION)[-1].strip()},
                log=llm_output
            )
        else:
            tool_input = inspect.cleandoc("""
            ```python
            ####### Thought: {llm_output}
            print("{llm_output}")
            ```
            """.format(llm_output=llm_output.replace('"', "\'")))
            # llm_output = '```' + llm_output
            # logger.info(f"Python REPL agent action with llm_output \n{llm_output}\n\n and tool input: \n{tool_input}{SPACING_BETWEEN_COMMANDS}")

            return AgentAction(tool="python_repl_ast", tool_input=tool_input, log=llm_output)
            # raise OutputParserException(llm_output)
