import os
from typing import Optional

import chartgpt_client
from chartgpt_client.exceptions import ApiException

from bots import logger

from dotenv import load_dotenv

load_dotenv('bots/.env')

configuration = chartgpt_client.Configuration(
    host=os.environ["CHARTGPT_API_HOST"]
)
configuration.api_key["ApiKeyAuth"] = os.environ["CHARTGPT_API_KEY"]

def ask_chartgpt(question) -> Optional[chartgpt_client.Response]:
    with chartgpt_client.ApiClient(configuration) as api_client:
        api_instance = chartgpt_client.DefaultApi(api_client)
        try:
            api_request_ask_chartgpt_request = chartgpt_client.Request(
                messages=[
                    {
                        "content": question,
                        "role": "user",
                    }
                ],
                output_type="any",
                data_source_url=os.environ["CHARTGPT_DATA_SOURCE_URL"],
            )
            api_response = api_instance.api_request_ask_chartgpt(
                api_request_ask_chartgpt_request
            )
            return api_response
        except ApiException as e:
            logger.error(
                f"Exception when calling DefaultApi->api_chart_generate_chart: {e}"
            )
            return None
        except Exception as e:
            logger.error(f"Exception: {e}")
            return None
