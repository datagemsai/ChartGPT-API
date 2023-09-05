# pylint: disable=C0103
# pylint: disable=C0116

import base64
import json
import os
import pickle
from bots.api import ask_chartgpt
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import dataframe_image as dfi
import inspect
import plotly.graph_objects as go
import sqlparse
import pandas as pd
import tempfile
import chartgpt_client
from chartgpt_client.models import OutputType

# Import environment variables from .env file
from dotenv import load_dotenv

load_dotenv("bots/slack/.env")

# Install the Slack app and get xoxb- token in advance
app = App(token=os.environ["SLACK_BOT_TOKEN"])


@app.command("/ask_chartgpt")
def handle_ask_chartgpt(ack, body, respond):
    ack()
    question = body["text"]
    print(f"Received question: {question}")
    respond(
        f"<@{body['user_id']}> I received your question: {question}",
        response_type="in_channel",
    )
    respond("I'm thinking... :thinking_face:", response_type="in_channel")
    response: chartgpt_client.Response = ask_chartgpt(question)

    channel_id = body["channel_id"]

    if not response:
        respond(
            f"<@{body['user_id']}> Sorry, I couldn't answer your question.",
            response_type="in_channel",
        )
        return

    initial_response = app.client.chat_postMessage(
        text=inspect.cleandoc(
            f"""
<@{body['user_id']}> Here is the result 🧵

Response time: {response.finished_at - response.created_at:.0f} seconds

*Question:* {response.prompt}
"""
        ),
        channel=channel_id,
    )

    thread_ts = initial_response["ts"]
    for output in response.outputs:
        if output.type == OutputType.PLOTLY_CHART.value and output.value:
            # if output.description:
            #     respond(
            #         inspect.cleandoc(output.description), response_type="in_channel"
            #     )
            with tempfile.TemporaryDirectory() as tmpdirname:
                figure_json_string = output.value
                figure_json = json.loads(figure_json_string, strict=False)
                fig = go.Figure(figure_json)
                fig.write_image(f"{tmpdirname}/chart.png")

                # img_byte_arr = io.BytesIO()
                # fig.write_image(img_byte_arr, format="png")
                # chart_png_data = img_byte_arr.getvalue()

                app.client.files_upload_v2(
                    channel=channel_id,
                    file=f"{tmpdirname}/chart.png",
                    filename="chart.png",
                    title="ChartGPT Chart",
                    # initial_comment=f"ChartGPT chart for question: {question}",
                    thread_ts=thread_ts,
                )
        elif output.type == OutputType.SQL_QUERY.value and output.value:
            app.client.chat_postMessage(
                text=(
                    f"{output.description}"
                    f"\n\n```\n{sqlparse.format(output.value, reindent=True, keyword_case='upper')}\n```"
                    if output.value
                    else ""
                ),
                channel=channel_id,
                thread_ts=thread_ts,
            )
        elif output.type == OutputType.PANDAS_DATAFRAME.value and output.value:
            try:
                dataframe: pd.DataFrame = pickle.loads(
                    base64.b64decode(output.value.encode())
                )
            except Exception as e:
                app.logger.error(
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

                        # Upload the image
                        with open(output_path, "rb") as file:
                            app.client.files_upload_v2(
                                channel=channel_id,
                                file=file,
                                filename=filename,
                                title="ChartGPT Table",
                                thread_ts=thread_ts,
                            )
        elif output.type == OutputType.PYTHON_CODE.value and output.value:
            app.client.chat_postMessage(
                text=inspect.cleandoc(f"{output.description}\n\n```\n{output.value}\n```"),
                channel=channel_id,
                thread_ts=thread_ts,
            )
        elif output.type == OutputType.PYTHON_OUTPUT.value and output.value:
            app.client.chat_postMessage(
                text=inspect.cleandoc(output.value),
                channel=channel_id,
                thread_ts=thread_ts,
            )
        else:
            print("Invalid output type:", output.type)


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
