# pylint: disable=C0103
# pylint: disable=C0116

import asyncio
import base64
import json
import os
import pickle
import tempfile

import chartgpt_client
import dataframe_image as dfi
import discord
import pandas as pd
import plotly.graph_objects as go
import sqlparse
from chartgpt_client import OutputType
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv

from bots.api import ask_chartgpt

load_dotenv("bots/.env")


DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    await tree.sync()
    print(f"We have logged in as {client.user}")


ongoing_tasks = {}

async def embed_progress_bar(embed: discord.Embed, embed_message: discord.Message):
    load_char = "✨"
    max_chars = 5
    chars = (embed.description.count(load_char) if embed.description else 0) + 1
    
    while True:  # Keep this running until you manually break out of it
        embed.description = "Thinking" + (load_char * min(chars, max_chars))
        await embed_message.edit(embed=embed)
        await asyncio.sleep(1)  # This replaces your loop's seconds=1
        chars += 1
        if chars > max_chars:
            chars = 1


@tree.command(name="ask_chartgpt", description="Ask ChartGPT an analytics question")
@app_commands.describe(question="The question to ask ChartGPT")
async def handle_ask_chartgpt(interaction: discord.Interaction, question: str):
    await interaction.response.send_message("Coming right up 🪄")

    embed = create_embed(question)
    msg = await interaction.channel.send(
        embed=embed, file=discord.File("media/logo_chartgpt.png", filename="logo.png")
    )

    task = asyncio.create_task(embed_progress_bar(embed, msg))
    ongoing_tasks[msg.id] = task

    response: chartgpt_client.Response = await asyncio.to_thread(ask_chartgpt, question)

    if not response:
        await handle_no_response(embed, msg)
        return

    await handle_response(embed, msg, interaction, response)


def create_embed(question: str) -> discord.Embed:
    embed = discord.Embed()
    embed.set_thumbnail(url="attachment://logo.png")
    embed.set_author(name="ChartGPT")
    embed.title = f"Question: {question}"
    embed.description = "Thinking..."
    return embed


async def handle_no_response(embed: discord.Embed, msg: discord.Message):
    task_to_cancel = ongoing_tasks.pop(msg.id, None)
    if task_to_cancel:
        task_to_cancel.cancel()
    embed.description = "Sorry, I couldn't answer your question."
    await msg.edit(embed=embed)


async def handle_response(
    embed: discord.Embed,
    msg: discord.Message,
    interaction: discord.Interaction,
    response: dict,
):
    task_to_cancel = ongoing_tasks.pop(msg.id, None)
    if task_to_cancel:
        task_to_cancel.cancel()

    description = (
        f"Response time: {response.finished_at - response.created_at:.0f} seconds\n\n"
    )
    files = []

    for output in response.outputs:
        if not output.value:
            print("Output value is empty for type:", output.type)

        elif output.type == OutputType.PLOTLY_CHART.value:
            # if output.description:
            #     description += f"{output.description}\n"
            with tempfile.TemporaryDirectory() as tmpdirname:
                figure_json_string = output.value
                figure_json = json.loads(figure_json_string, strict=False)
                fig = go.Figure(figure_json)
                fig.write_image(f"{tmpdirname}/chart.png")

                files += [discord.File(f"{tmpdirname}/chart.png", filename="chart.png")]

        elif output.type == OutputType.SQL_QUERY.value:
            description += (
                f"{output.description}"
                f"\n\n```sql\n{sqlparse.format(output.value, reindent=True, keyword_case='upper')}\n```"
            )

        elif output.type == OutputType.PANDAS_DATAFRAME.value:
            try:
                dataframe: pd.DataFrame = pd.read_json(output.value)
            except Exception as e:
                print(
                    f"Exception when converting DataFrame to markdown: {e}"
                )  # Adjusted the error logging to a simple print, you can adapt this to your preferred logging method.
                dataframe = pd.DataFrame()

            if not dataframe.empty:
                with tempfile.TemporaryDirectory() as tmpdirname:
                    # Define the data and filenames
                    data_and_files = [
                        (dataframe, "df_head.png"),
                        (dataframe.describe(), "df_describe.png"),
                    ]

                    # Export the dataframes as images and upload them
                    for data, filename in data_and_files:
                        output_path = f"{tmpdirname}/{filename}"

                        # Export dataframe as an image
                        dfi.export(
                            data,
                            output_path,
                            max_rows=10,
                            table_conversion="matplotlib",
                        )

                        files += [discord.File(output_path, filename=filename)]

        elif output.type == OutputType.PYTHON_CODE.value:
            description += f"\n\n{output.description}\n\n```python\n{output.value}\n```"

        elif output.type in [
            OutputType.PYTHON_OUTPUT.value,
            OutputType.STRING.value,
            OutputType.INT.value,
            OutputType.FLOAT.value,
            OutputType.BOOL.value,
        ]:
            description += f"\n\nCode output:\n{output.value}"

        else:
            print("Invalid output type:", output.type)

    # Limit description to "Must be 4096 or fewer in length."
    embed.description = description[:4000] + "..." if len(description) > 4000 else description
    await msg.edit(embed=embed)
    if files:
        await interaction.channel.send("Here are the results!", files=files)


if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
