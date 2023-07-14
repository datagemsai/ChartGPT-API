import asyncio
import os
import discord
from discord import app_commands
from concurrent.futures import ThreadPoolExecutor
import requests
from langchain.callbacks.base import BaseCallbackHandler
from typing import Any, Dict, List, Optional, Union
from langchain.schema import AgentAction, AgentFinish, LLMResult
import logging
from langchain.schema import OutputParserException
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    HumanMessage,
)
import streamlit as st
from discord.ext import tasks
from discord.utils import get
from typing import Dict, Union, Any, List
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction
import chartgpt
import app


DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


class DiscordCallbackHandler(BaseCallbackHandler):
    def __init__(
        self,
        client,
        embed: Optional[discord.Embed] = None,
        embed_message: Optional[discord.Message] = None,
    ) -> None:
        super().__init__()
        self.client: discord.Client = client
        self.embed: Optional[discord.Embed] = embed
        self.embed_message: Optional[discord.Message] = embed_message

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Print out the prompts."""
        # class_name = serialized["name"]
        # app.logger.info(f"on_llm_start: {class_name}")
        pass

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Do nothing."""
        # app.logger.info(f"on_llm_end: {response}")
        pass

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Do nothing."""
        # app.logger.info(f"on_llm_new_token: {token}")
        pass

    def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Do nothing."""
        # app.logger.info(f"on_llm_error: {error}")
        pass

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Print out that we are entering a chain."""
        # class_name = serialized["name"]
        # app.logger.info(f"on_chain_start: {class_name}")
        pass

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Print out that we finished a chain."""
        # app.logger.info(f"on_chain_end: {outputs}")
        pass

    def on_chain_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Do nothing."""
        # app.logger.info(f"on_chain_error: {error}")
        pass

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        **kwargs: Any,
    ) -> None:
        """Do nothing."""
        # app.logger.info(f"on_tool_start: {input_str}")
        pass

    def on_agent_action(
        self, action: AgentAction, color: Optional[str] = None, **kwargs: Any
    ) -> Any:
        """Run on agent action."""
        # app.logger.info(f"on_agent_action: {action}")
        # new_lines = action.tool_input.count('\n')
        # should_display = new_lines > 1 or not "display" in action.tool_input
        # if should_display:
        #     st.markdown(inspect.cleandoc(f"""
        #     ```python
        #     {action.tool_input}
        #     """))
        pass

    def on_tool_end(
        self,
        output: str,
        observation_prefix: Optional[str] = None,
        llm_prefix: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """If not the final action, print out observation."""
        # app.logger.info(f"on_tool_end: {output}")
        pass

    def on_tool_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Do nothing."""
        # app.logger.info(f"on_tool_error: {error}")
        pass

    def on_text(
        self,
        text: str,
        color: Optional[str] = None,
        end: str = "",
        **kwargs: Optional[str],
    ) -> None:
        """Run when agent ends."""
        # app.logger.info(f"on_text: {text}")
        pass

    def on_agent_finish(
        self, finish: AgentFinish, color: Optional[str] = None, **kwargs: Any
    ) -> None:
        """Run on agent end."""
        # app.logger.info(f"on_agent_finish: {finish}")
        # st.markdown(finish.return_values["output"])
        pass

# Override Streamlit session state and initialize chat history
st.session_state = {"messages": [], "container": st.empty()}

@client.event
async def on_ready():
    await tree.sync()
    print(f"We have logged in as {client.user}")


def _ask_chartgpt_api(question):
    """
    NOTE Work in progress
    """
    url = f"http://localhost:8000/query?question={question}&format=png"
    payload = {}
    headers = {}
    _ = requests.request("GET", url, headers=headers, data=payload)
    with open("app/outputs/result.png", "rb") as result:
        return discord.File(result, spoiler=False, description="Here's your chart!")


def clear_output_directory():
    if not os.path.exists("app/outputs"):
        os.makedirs("app/outputs", exist_ok=True)
    app.logger.info("Clearing outputs directory")
    for filename in os.listdir("app/outputs"):
        app.logger.info(f"Removing {filename}")
        os.remove(f"app/outputs/{filename}")


def _ask_chartgpt(
    question="Perform EDA",
    dataset: Optional[str] = None,
    # embed: Optional[discord.Embed] = None,
    # embed_message: Optional[discord.Message] = None,
):
    clear_output_directory()
    # Ask ChartGPT
    response = {"input": "", "output": "", "chat_history": "", "intermediate_steps": []}
    try:
        # get_agent() is cached by Streamlit, where the cache is invalidated if datasets changes
        question += " Answer as quickly as possible with one chart."
        agent = chartgpt.get_agent(
            datasets=app.datasets
        )
        response = agent(
            question, # callbacks=[DiscordCallbackHandler(client, embed, embed_message)]
        )
        # response[
        #     "output"
        # ] += f"""
        #
        #     Analysis complete!
        #
        #     Enjoying ChartGPT and eager for more? Join our waitlist to stay ahead with the latest updates.
        #     You'll also be among the first to gain access when we roll out new features! Sign up [here](https://ne6tibkgvu7.typeform.com/to/ZqbYQVE6).
        #     """
    except OutputParserException as e:
        response[
            "output"
        ] += f"""

            Analysis failed.

            {str(e)}

            [We welcome any feedback or bug reports.](https://ne6tibkgvu7.typeform.com/to/jZnnMGjh)
            """
    except Exception as e:
        app.logger.error(e)
        response[
            "output"
        ] += f"""

            Analysis failed for unknown reason, please try again.

            [We welcome any feedback or bug reports.](https://ne6tibkgvu7.typeform.com/to/jZnnMGjh)
            """
    return response


@tasks.loop(seconds=1)
async def embed_progress_bar(embed: discord.Embed, embed_message: discord.Message):
    load_char = "✨"
    max_chars = 5
    if embed.description:
        chars = embed.description.count(load_char)
        embed.description = "Thinking" + (load_char * int((chars + 1) % max_chars + 1))
    else:
        embed.description = "Thinking" + load_char * max_chars
    await embed_message.edit(embed=embed)


@tree.command(name="ask_chartgpt", description="Ask ChartGPT an analytics question")
@app_commands.describe(question="The question to ask ChartGPT")
async def ask_chartgpt(
    interaction: discord.Interaction,
    question: str,
):
    await interaction.response.send_message("Coming right up 🪄")

    embed = discord.Embed()
    logo_image = discord.File(
        "media/logo_chartgpt.png",
        filename="logo.png",
        spoiler=False,
        description="ChartGPT logo",
    )
    embed.set_thumbnail(url="attachment://logo.png")
    embed.set_author(name="ChartGPT")
    embed.title = f"Question: {question}"
    embed.description = "Thinking..."
    msg: discord.Message = await interaction.channel.send(embed=embed, file=logo_image)

    embed_progress_bar.start(embed, msg)

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        ThreadPoolExecutor(), _ask_chartgpt, question, # embed, msg
    )

    # Get the path to the outputs directory
    outputs_dir = f"app/outputs/"
    # Get a list of all files in the outputs directory
    output_files = os.listdir(outputs_dir)
    # Create a list of discord.File objects for each file in the directory
    attachments = [
        discord.File(
            os.path.join(outputs_dir, f),
            spoiler=False,
            description=f"Output file {i+1}",
        )
        for i, f in enumerate(output_files)
    ]

    embed_progress_bar.cancel()
    embed.description = response["output"]
    # embed.set_footer(text="Made with ❤️ by CADLabs")

    # await msg.edit(embed=embed, attachments=attachments)
    await msg.edit(embed=embed)
    if attachments:
        await interaction.channel.send("Here are the results!", files=attachments)
        clear_output_directory()


if __name__ == "__main__":
    client.run(
        DISCORD_TOKEN
    )
