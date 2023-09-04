# pylint: disable=C0103
# pylint: disable=C0116

import base64
import io
import json
import os
import pickle
import time
from typing import Optional
from api.chartgpt import QueryResult
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

# ChartGPT
import openapi_client
from openapi_client.exceptions import ApiException

configuration = openapi_client.Configuration(
    # TODO Fetch from environment variable
    host="http://0.0.0.0:8081"
)
configuration.api_key["ApiKeyAuth"] = "abc"


def ask_chartgpt(question) -> Optional[QueryResult]:
    with openapi_client.ApiClient(configuration) as api_client:
        api_instance = openapi_client.DefaultApi(api_client)
        try:
            api_response = api_instance.api_chart_generate_chart(
                {
                    "question": question,
                    "type": "json",
                }
            )
            return QueryResult(**api_response.to_dict())
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
    start_time = time.time()
    query_result = ask_chartgpt(question)
    end_time = time.time()

    if query_result:
        try:
            dataframe: pd.DataFrame = pickle.loads(
                base64.b64decode(query_result.dataframe.encode())
            )
        except Exception as e:
            app.logger.error(f"Exception when converting DataFrame to markdown: {e}")
            dataframe = pd.DataFrame()
        respond(
            inspect.cleandoc(
                f"""
<@{body['user_id']}> Here is the result:

Response time: {end_time - start_time:.2f} seconds

*Question:* {question}

{query_result.description}

```
{sqlparse.format(query_result.query, reindent=True, keyword_case='upper')}
```
            """
            ),
            response_type="in_channel",
        )

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

        respond(
            inspect.cleandoc(
                f"""
```
{query_result.code}
```

{query_result.output}
            """
            ),
            response_type="in_channel",
        )

        with tempfile.TemporaryDirectory() as tmpdirname:
            figure_json_string = query_result.chart
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
                initial_comment=f"ChartGPT chart for question: {question}",
            )
    else:
        respond(
            f"<@{body['user_id']}> Sorry, I couldn't answer your question.",
            response_type="in_channel",
        )


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
