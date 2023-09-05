# pylint: disable=C0103
# pylint: disable=C0116

import base64
import io
import json
import os
import pickle
import time
from typing import Optional
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import dataframe_image as dfi
import inspect
import plotly.graph_objects as go
import sqlparse
import pandas as pd
import tempfile

# Import environment variables from .env file
from dotenv import load_dotenv

load_dotenv("bots/slack/.env")

# Install the Slack app and get xoxb- token in advance
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# ChartGPT API
import chartgpt_client
from chartgpt_client.models import OutputType
from chartgpt_client.exceptions import ApiException


configuration = chartgpt_client.Configuration(
    # TODO Fetch from environment variable
    host="http://0.0.0.0:8081"
)
configuration.api_key["ApiKeyAuth"] = "abc"


def ask_chartgpt(question) -> Optional[chartgpt_client.Response]:
    with chartgpt_client.ApiClient(configuration) as api_client:
        api_instance = chartgpt_client.DefaultApi(api_client)
        try:
            api_request_ask_chartgpt_request = chartgpt_client.ApiRequestAskChartgptRequest(
                prompt = question,
                output_type = "plotly_chart",
            )
            api_response  = api_instance.api_request_ask_chartgpt(
                api_request_ask_chartgpt_request
            )
            return api_response
        except ApiException as e:
            app.logger.error(
                f"Exception when calling DefaultApi->api_chart_generate_chart: {e}"
            )
            return None


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

    if not response:
        respond(
            f"<@{body['user_id']}> Sorry, I couldn't answer your question.",
            response_type="in_channel",
        )
        return

    respond(
            inspect.cleandoc(
                        f"""
<@{body['user_id']}> Here is the result:

Response time: {response.finished_at - response.created_at:.2f} seconds

*Question:* {response.prompt}

"""), response_type="in_channel"
    )

    for output in response.outputs:
        if output.type == OutputType.PLOTLY_CHART.value:
            if output.description:
                respond(inspect.cleandoc(output.description), response_type="in_channel")
            with tempfile.TemporaryDirectory() as tmpdirname:
                figure_json_string = output.value
                figure_json = json.loads(figure_json_string, strict=False)
                fig = go.Figure(figure_json)
                fig.write_image(f"{tmpdirname}/chart.png")

                # img_byte_arr = io.BytesIO()
                # fig.write_image(img_byte_arr, format="png")
                # chart_png_data = img_byte_arr.getvalue()

                app.client.files_upload_v2(
                    channel=body["channel_id"],
                    file=f"{tmpdirname}/chart.png",
                    filename="chart.png",
                    title="ChartGPT Chart",
                    # initial_comment=f"ChartGPT chart for question: {question}",
                )
        elif output.type == OutputType.SQL_QUERY.value:
            respond(
                (
                    f"{output.description}"
                    f"\n\n```\n{sqlparse.format(output.value, reindent=True, keyword_case='upper')}\n```" if output.value else ""
                ),
                response_type="in_channel",
            )
        elif output.type == OutputType.PANDAS_DATAFRAME.value:
            try:
                dataframe: pd.DataFrame = pickle.loads(
                    base64.b64decode(output.value.encode())
                )
            except Exception as e:
                app.logger.error(f"Exception when converting DataFrame to markdown: {e}")
                dataframe = pd.DataFrame()
            if not dataframe.empty:
                with tempfile.TemporaryDirectory() as tmpdirname:
                    # Define the data and filenames
                    data_and_files = [
                        (dataframe, "df_head.png"),
                        (dataframe.describe(), "df_describe.png")
                    ]
                    
                    # Export the dataframes as images and upload them
                    for data, filename in data_and_files:
                        output_path = f"{tmpdirname}/{filename}"
                        
                        # Export dataframe as an image
                        dfi.export(
                            data,
                            output_path,
                            max_rows=10,
                            table_conversion="matplotlib"
                        )
                        
                        # Upload the image
                        with open(output_path, "rb") as file:
                            app.client.files_upload_v2(
                                channel=body["channel_id"],
                                file=file,
                                filename=filename,
                                title="ChartGPT Table"
                            )
        elif output.type == OutputType.PYTHON_CODE.value:
            respond(
                inspect.cleandoc(f"{output.description}\n\n```\n{output.value}\n```"),
                response_type="in_channel",
            )
        elif output.type == OutputType.PYTHON_OUTPUT.value:
            respond(
                inspect.cleandoc(output.value),
                response_type="in_channel",
            )
        else:
            print("Invalid output type:", output.type)


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
