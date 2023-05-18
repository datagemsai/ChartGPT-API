from typing import Dict, List, Optional, Tuple, Union, Sequence
from pydantic import Field

from langchain.tools.base import BaseTool
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from langchain.agents.agent import AgentOutputParser
from pydantic import root_validator
from analytics_bot_langchain.agents.agent_toolkits.bigquery.prompt import PREFIX, SUFFIX
from langchain.schema import (
    AgentAction,
    BaseMessage
)
from analytics_bot_langchain.agents.mrkl.output_parser import CustomOutputParser
from analytics_bot_langchain.agents.mrkl.prompt import FORMAT_INSTRUCTIONS
import logging
from langchain.agents.mrkl.base import ZeroShotAgent


logger = logging.getLogger(__name__)

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

    @classmethod
    def create_prompt(
        cls,
        tools: Sequence[BaseTool],
        prefix: str = PREFIX,
        suffix: str = SUFFIX,
        format_instructions: str = FORMAT_INSTRUCTIONS,
        input_variables: Optional[List[str]] = None,
    ) -> PromptTemplate:
        """Create prompt in the style of the zero shot agent.

        Args:
            tools: List of tools the agent will have access to, used to format the
                prompt.
            prefix: String to put before the list of tools.
            suffix: String to put after the list of tools.
            input_variables: List of input variables the final prompt will expect.

        Returns:
            A PromptTemplate with the template assembled from the pieces here.
        """
        tool_strings = "\n\n".join([f"## {tool.name}:\n\n{tool.description}" for tool in tools])
        # tool_names = ", ".join([tool.name for tool in tools])
        # format_instructions = format_instructions.format(tool_names=tool_names)
        template = "\n\n".join([prefix, tool_strings, format_instructions, suffix])
        if input_variables is None:
            input_variables = ["input", "agent_scratchpad"]
        return PromptTemplate(template=template, input_variables=input_variables)

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
        logger.info(f"===================== scratchpad start =====================\n{thoughts}")
        logger.info("===================== scratchpad end =====================")
        return thoughts
