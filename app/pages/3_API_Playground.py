import base64
import inspect
import json
import os
import pickle
import time

import chartgpt_client
import pandas as pd
import sqlparse
import streamlit as st
from chartgpt_client.models import OutputType

import app
from api.auth import create_api_key, get_api_keys
from app.auth import requires_auth
from app.components.notices import Notices

# Show notices
Notices()


@requires_auth
def main(user_id, user_email):
    # Clear prior query
    st.session_state.question = ""

    # Display app name
    PAGE_NAME = "API Playground"
    st.markdown("# " + PAGE_NAME + " 🎢")
    st.markdown("### Try out the ChartGPT API")

    # st.info("Coming soon! 🚀")
    # st.stop()

    # Defining the host is optional and defaults to https://api.chartgpt.***REMOVED***
    # See configuration.py for a list of all supported configuration parameters.
    configuration = chartgpt_client.Configuration(host=os.environ["CHARTGPT_API_HOST"])

    # if st.button("Create API key"):
    #     create_api_key(user_id)
    # api_keys = get_api_keys(user_id)

    # TODO Add feature to add/remove API keys and set expiry date
    # for api_key in api_keys:
    #     # Display API key and delete button
    #     cols = st.columns(2)
    #     cols[0].markdown(api_key)
    #     cols[1].button("Delete API key", key=api_key, on_click=(lambda api_key=api_key: delete_api_key(user_id=user_id, api_key=api_key)))

    # api_key = st.text_input("API key", value=(api_keys[0] if api_keys else ""))
    api_key = os.environ["CHARTGPT_API_KEY"]

    with st.form(key="chart_api_request"):
        st.markdown("### API endpoint: `/v1/ask_chartgpt`")
        data_source_url_options = {
            "MetaQuants NFT Finance Aggregator": "bigquery/chartgpt-staging/metaquants_nft_finance_aggregator/p2p_and_p2pool_loan_data_borrow",
            "bitsCrunch Unleash NFTs": "bigquery/chartgpt-staging/bitscrunch_unleash_nfts/nft_market_trends",
        }
        data_source_url_key = st.selectbox(
            "data_source_url",
            options=data_source_url_options.keys(),
        )
        question = st.text_input(
            "prompt",
            value="Plot the average APR for the ***REMOVED*** protocol in the past 6 months.",
        )
        output_type = st.selectbox(
            "output_type",
            options=["any", "plotly_chart", "pandas_dataframe", "int", "float", "bool"],
            index=1,
        )
        submitted = st.form_submit_button("Submit")

        if submitted:
            # TODO Enable API key authentication
            configuration.api_key["ApiKeyAuth"] = api_key
            # Enter a context with an instance of the API client
            with chartgpt_client.ApiClient(configuration) as api_client:
                with st.spinner("Performing query..."):
                    # Create an instance of the API class
                    api_instance = chartgpt_client.DefaultApi(api_client)
                    try:
                        # Generate a Plotly chart from a question
                        api_request_ask_chartgpt_request = chartgpt_client.Request(
                            messages=[
                                {
                                    "content": question,
                                    "role": "user",
                                }
                            ],
                            output_type=output_type,
                            data_source_url=data_source_url_options[
                                data_source_url_key
                            ],
                        )
                        response: chartgpt_client.Response = (
                            api_instance.api_request_ask_chartgpt(
                                api_request_ask_chartgpt_request
                            )
                        )

                        st.markdown(
                            f"**API response time:** {response.finished_at - response.created_at:.0f} seconds"
                        )

                        for output in response.outputs:
                            if not output.value:
                                print("Output value is empty for type:", output.type)

                            elif output.type == OutputType.PLOTLY_CHART.value:
                                figure_json_string = output.value
                                figure_json = json.loads(
                                    figure_json_string, strict=False
                                )
                                st.plotly_chart(figure_json, use_container_width=True)

                            elif output.type == OutputType.SQL_QUERY.value:
                                st.markdown(
                                    inspect.cleandoc(
                                        f"{output.description}\n\n```sql{sqlparse.format(output.value, reindent=True, keyword_case='upper')}\n```"
                                    )
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
                                    st.dataframe(dataframe)

                            elif output.type == OutputType.PYTHON_CODE.value:
                                st.markdown(
                                    inspect.cleandoc(
                                        f"{output.description}\n\n```python\n{output.value}\n```"
                                    )
                                )

                            # elif output.type in [
                            #     OutputType.PYTHON_OUTPUT.value,
                            #     OutputType.STRING.value,
                            #     OutputType.INT.value,
                            #     OutputType.FLOAT.value,
                            #     OutputType.BOOL.value,
                            # ]:
                            #     st.markdown(inspect.cleandoc("Code output:\n" + output.value))

                    except chartgpt_client.ApiException as e:
                        st.warning("API call failed")
    with st.form(key="chart_api_request_stream"):
        st.markdown("### API endpoint: `/v1/ask_chartgpt/stream`")
        st.info(
            f"Demo coming soon! 🚀 In the meantime check out the [ChartGPT OpenAPI spec]({os.environ['CHARTGPT_API_HOST']}/ui)."
        )
        _ = st.form_submit_button("Submit")


if __name__ == "__main__":
    main()
