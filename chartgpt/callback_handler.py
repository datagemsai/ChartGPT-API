import inspect
import streamlit as st
from langchain.callbacks.base import BaseCallbackHandler
from typing import Any, Dict, List, Optional, Union
from langchain.schema import AgentAction, AgentFinish, LLMResult
from app import logger


class CustomCallbackHandler(BaseCallbackHandler):
    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Print out the prompts."""
        class_name = serialized["id"]
        logger.info(f"on_llm_start: {class_name}")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Do nothing."""
        logger.info(f"on_llm_end: {response}")

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Do nothing."""
        logger.info(f"on_llm_new_token: {token}")

    def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Do nothing."""
        logger.info(f"on_llm_error: {error}")

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Print out that we are entering a chain."""
        class_name = serialized["id"]
        logger.info(f"on_chain_start: {class_name}")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Print out that we finished a chain."""
        logger.info(f"on_chain_end: {outputs}")

    def on_chain_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Do nothing."""
        logger.info(f"on_chain_error: {error}")

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        **kwargs: Any,
    ) -> None:
        """Do nothing."""
        logger.info(f"on_tool_start: {input_str}")

    def on_agent_action(
        self, action: AgentAction, color: Optional[str] = None, **kwargs: Any
    ) -> Any:
        """Run on agent action."""
        logger.info(f"on_agent_action: {action}")
        new_lines = action.tool_input.count('\n')
        should_display = new_lines > 1 or not "display" in action.tool_input
        if should_display:
            output = inspect.cleandoc(f"""
            ```python
            {action.tool_input}
            ```
            """)
            st.session_state["messages"].append({"role": "assistant", "content": output})

    def on_tool_end(
        self,
        output: str,
        observation_prefix: Optional[str] = None,
        llm_prefix: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """If not the final action, print out observation."""
        logger.info(f"on_tool_end: {output}")

    def on_tool_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Do nothing."""
        logger.info(f"on_tool_error: {error}")

    def on_text(
        self,
        text: str,
        color: Optional[str] = None,
        end: str = "",
        **kwargs: Optional[str],
    ) -> None:
        """Run when agent ends."""
        logger.info(f"on_text: {text}")

    def on_agent_finish(
        self, finish: AgentFinish, color: Optional[str] = None, **kwargs: Any
    ) -> None:
        """Run on agent end."""
        logger.info(f"on_agent_finish: {finish}")
        output = finish.return_values["output"]
        st.session_state["messages"].append({"role": "assistant", "content": output})
