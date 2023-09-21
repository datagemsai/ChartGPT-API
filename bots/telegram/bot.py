# pylint: disable=C0103
# pylint: disable=C0116

import base64
import inspect
import json
import os
import pickle
import tempfile

import chartgpt_client
import dataframe_image as dfi
import pandas as pd
import plotly.graph_objects as go
import sqlparse
from chartgpt_client.models import OutputType
from dotenv import load_dotenv
from telegram import InputMediaPhoto, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from bots import logger
from bots.api import ask_chartgpt

load_dotenv("bots/.env")

TELEGRAM_ADMIN_USERNAME = os.environ["TELEGRAM_ADMIN_USERNAME"]
# Your token obtained from BotFather
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]


async def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(f"Update {update} caused error {context.error}")

    # Optionally, send a message to an admin or group to notify them of the error.
    await context.bot.send_message(
        chat_id=TELEGRAM_ADMIN_USERNAME, text="An error occurred."
    )
    await update.message.reply_text("Sorry, I couldn't answer your question.")


async def update_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE, message, text
):
    original_text = message.text
    updated_text = original_text + "\n\n" + text
    new_message = await context.bot.edit_message_text(
        text=updated_text,
        chat_id=update.message.chat_id,
        message_id=message.message_id,
        parse_mode="Markdown",
    )
    return new_message


async def handle_ask_chartgpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    question = update.message.text.removeprefix("/ask_chartgpt")
    print(f"Received question from {user.first_name}: {question}")

    message_text = f"{user.first_name}, I received your question: {question}"
    message = await update.message.reply_text(message_text, parse_mode="Markdown")

    message_text = "I'm thinking... 🤔"
    message = await update_message(update, context, message, message_text)

    response: chartgpt_client.Response = ask_chartgpt(question)

    if not response:
        message_text = "Sorry, I couldn't answer your question."
        message = await update_message(update, context, message, message_text)
        return

    message_text = inspect.cleandoc(
        f"""
        *Question:* {response.messages[0].content}

        Response time: {response.finished_at - response.created_at:.0f} seconds

        """
    )
    message = await update_message(update, context, message, message_text)

    for output in response.outputs:
        if not output.value:
            print("Output value is empty for type:", output.type)

        elif output.type == OutputType.PLOTLY_CHART.value:
            # if output.description:
            #     await update.message.reply_text(inspect.cleandoc(output.description))
            with tempfile.TemporaryDirectory() as tmpdirname:
                figure_json_string = output.value
                figure_json = json.loads(figure_json_string, strict=False)
                fig = go.Figure(figure_json)
                fig.write_image(f"{tmpdirname}/chart.png")

                with open(f"{tmpdirname}/chart.png", "rb") as f:
                    await update.message.reply_photo(photo=f)

        elif output.type == OutputType.SQL_QUERY.value:
            await update.message.reply_text(
                f"{output.description}\n\n```\n{sqlparse.format(output.value, reindent=True, keyword_case='upper')}\n```",
                # parse_mode="Markdown"
            )

        elif output.type == OutputType.PANDAS_DATAFRAME.value:
            try:
                dataframe: pd.DataFrame = pd.read_json(output.value)
            except Exception as e:
                logger.error(
                    f"Exception when converting DataFrame to markdown: {e}"
                )
                dataframe = pd.DataFrame()

            if not dataframe.empty:
                with tempfile.TemporaryDirectory() as tmpdirname:
                    # Define the data and filenames
                    data_and_files = [
                        (dataframe, "df_head.png"),
                        (dataframe.describe(), "df_describe.png"),
                    ]

                    media_group = []

                    # Export the dataframes as images
                    for data, filename in data_and_files:
                        output_path = f"{tmpdirname}/{filename}"

                        # Export dataframe as an image
                        dfi.export(
                            data,
                            output_path,
                            max_rows=10,
                            table_conversion="matplotlib",
                        )

                        # Append to the media group
                        media_group.append(InputMediaPhoto(open(output_path, "rb")))

                    # Send the media group
                    await context.bot.send_media_group(
                        chat_id=update.message.chat_id, media=media_group
                    )

        elif output.type == OutputType.PYTHON_CODE.value:
            await update.message.reply_text(
                inspect.cleandoc(f"{output.description}\n\n```\n{output.value}\n```"),
                parse_mode="Markdown",
            )

        elif output.type in [
            OutputType.PYTHON_OUTPUT.value,
            OutputType.STRING.value,
            OutputType.INT.value,
            OutputType.FLOAT.value,
            OutputType.BOOL.value,
        ]:
            await update.message.reply_text(
                inspect.cleandoc("Code output:\n" + output.value)
            )

        else:
            print("Invalid output type:", output.type)


if __name__ == "__main__":
    application = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .read_timeout(300)
        .write_timeout(300)
        .build()
    )

    start_handler = CommandHandler("ask_chartgpt", handle_ask_chartgpt)
    start_handler = CommandHandler("ask_ChartGPT", handle_ask_chartgpt)
    start_handler = CommandHandler("chartgpt", handle_ask_chartgpt)
    start_handler = CommandHandler("ChartGPT", handle_ask_chartgpt)
    application.add_handler(start_handler)
    application.add_error_handler(error_handler)

    application.run_polling()
