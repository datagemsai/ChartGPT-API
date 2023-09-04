# pylint: disable=C0103
# pylint: disable=C0116

import asyncio
import os
from openapi_client.exceptions import ApiException
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
import io
import plotly.graph_objects as go
import json

import openapi_client
from openapi_client.apis.tags import default_api


DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

configuration = openapi_client.Configuration(
    # TODO Fetch from environment variable
    host="http://0.0.0.0:8081"
)
configuration.api_key["ApiKeyAuth"] = "abc"


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
        pass

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        pass

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        pass

    def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        pass

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        pass

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        pass

    def on_chain_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        pass

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        **kwargs: Any,
    ) -> None:
        pass

    def on_agent_action(
        self, action: AgentAction, color: Optional[str] = None, **kwargs: Any
    ) -> Any:
        pass

    def on_tool_end(
        self,
        output: str,
        observation_prefix: Optional[str] = None,
        llm_prefix: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        pass

    def on_tool_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        pass

    def on_text(
        self,
        text: str,
        color: Optional[str] = None,
        end: str = "",
        **kwargs: Optional[str],
    ) -> None:
        pass

    def on_agent_finish(
        self, finish: AgentFinish, color: Optional[str] = None, **kwargs: Any
    ) -> None:
        pass


# Override Streamlit session state and initialize chat history
st.session_state = {"messages": [], "container": st.empty()}


@client.event
async def on_ready():
    await tree.sync()
    print(f"We have logged in as {client.user}")


def _ask_chartgpt_api(question) -> Optional[str]:
    with openapi_client.ApiClient(configuration) as api_client:
        api_instance = default_api.DefaultApi(api_client)
        try:
            api_response = api_instance.api_chart_generate_chart(
                {
                    "question": question,
                    "type": "json",
                }
            )
        except ApiException as e:
            app.logger.error(
                f"Exception when calling DefaultApi->api_chart_generate_chart: {e}"
            )
            return None
        figure_json_string = api_response.body["chart"]
        figure_json = json.loads(figure_json_string, strict=False)
        fig = go.Figure(figure_json)
        img_byte_arr = io.BytesIO()
        fig.write_image(img_byte_arr, format="png")
        png_data = img_byte_arr.getvalue()
        return {
            "description": api_response.body["description"],
            "chart": discord.File(
                io.BytesIO(png_data),
                filename=f"chart.png",
                spoiler=False,
                description="Here's your chart!",
            ),
            "query": api_response.body["query"],
            "code": api_response.body["code"],
            "output": api_response.body["output"],
        }


def clear_output_directory():
    if not os.path.exists("app/outputs"):
        os.makedirs("app/outputs", exist_ok=True)
    app.logger.info("Clearing outputs directory")
    for filename in os.listdir("app/outputs"):
        app.logger.info(f"Removing {filename}")
        os.remove(f"app/outputs/{filename}")


def _ask_chartgpt(
    question="Perform EDA",
):
    clear_output_directory()
    # Ask ChartGPT
    response = {"input": "", "output": "", "chat_history": "", "intermediate_steps": []}
    try:
        question += " Answer as quickly as possible with one chart."
        agent = chartgpt.get_agent(datasets=app.datasets)
        response = agent(
            question,  # callbacks=[DiscordCallbackHandler(client, embed, embed_message)]
        )
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
        ThreadPoolExecutor(),
        _ask_chartgpt_api,
        question,  # embed, msg
    )
    if not response:
        embed_progress_bar.cancel()
        embed.description = (
            "I wasn't able to generate a chart for this question. Please try again."
        )
        await msg.edit(embed=embed)
        return

    attachments = [response["chart"]]

    embed_progress_bar.cancel()
    embed.description = f"""
    {response["description"]}
    
    ```sql
    {response["query"]}
    ```

    ```python
    {response["code"]}
    ```

    ```
    {response["output"]}
    ```
    """

    await msg.edit(embed=embed)
    if attachments:
        await interaction.channel.send("Here are the results!", files=attachments)
        clear_output_directory()


if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
