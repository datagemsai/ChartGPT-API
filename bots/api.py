import os
from typing import Optional

import chartgpt_client
from chartgpt_client.exceptions import ApiException

import app

configuration = chartgpt_client.Configuration(
    # TODO Fetch from environment variable
    host="http://0.0.0.0:8081"
)
configuration.api_key["ApiKeyAuth"] = os.environ["CHARTGPT_API_KEY"]


def ask_chartgpt(question) -> Optional[chartgpt_client.Response]:
    with chartgpt_client.ApiClient(configuration) as api_client:
        api_instance = chartgpt_client.DefaultApi(api_client)
        try:
            api_request_ask_chartgpt_request = chartgpt_client.ApiRequestAskChartgptRequest(
                messages=[
                    {
                        "content": question,
                        "role": "user",
                    }
                ],
                output_type="any",
                data_source_url="bigquery/chartgpt-staging/metaquants_nft_finance_aggregator/p2p_and_p2pool_loan_data_borrow",
            )
            api_response = api_instance.api_request_ask_chartgpt(
                api_request_ask_chartgpt_request
            )
            return api_response
        except ApiException as e:
            app.logger.error(
                f"Exception when calling DefaultApi->api_chart_generate_chart: {e}"
            )
            return None
        except Exception as e:
            app.logger.error(f"Exception: {e}")
            return None
