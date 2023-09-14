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
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from bots.api import ask_chartgpt

load_dotenv("bots/.env")

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
*Question:* {response.messages[0].content}

<@{body['user_id']}> Here is the result 🧵

Response time: {response.finished_at - response.created_at:.0f} seconds
"""
        ),
        channel=channel_id,
    )

    thread_ts = initial_response["ts"]
    for output in response.outputs:
        if not output.value:
            print("Output value is empty for type:", output.type)

        elif output.type == OutputType.PLOTLY_CHART.value:
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

        elif output.type == OutputType.SQL_QUERY.value:
            app.client.chat_postMessage(
                text=(
                    f"{output.description}"
                    f"\n\n```\n{sqlparse.format(output.value, reindent=True, keyword_case='upper')}\n```"
                ),
                channel=channel_id,
                thread_ts=thread_ts,
            )

        elif output.type == OutputType.PANDAS_DATAFRAME.value:
            try:
                dataframe: pd.DataFrame = pd.read_json(output.value)
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

        elif output.type == OutputType.PYTHON_CODE.value:
            app.client.chat_postMessage(
                text=inspect.cleandoc(
                    f"{output.description}\n\n```\n{output.value}\n```"
                ),
                channel=channel_id,
                thread_ts=thread_ts,
            )

        elif output.type in [
            OutputType.PYTHON_OUTPUT.value,
            OutputType.STRING.value,
            OutputType.INT.value,
            OutputType.FLOAT.value,
            OutputType.BOOL.value,
        ]:
            app.client.chat_postMessage(
                text=inspect.cleandoc("Code output:\n" + output.value),
                channel=channel_id,
                thread_ts=thread_ts,
            )

        else:
            print("Invalid output type:", output.type)


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
