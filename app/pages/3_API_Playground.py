import inspect
import json
import time
import sqlparse
import streamlit as st
import openapi_client
from app.auth import requires_auth
from chartgpt.app import client
from api.auth import create_api_key, get_api_keys
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
    st.markdown("### Try out the ChartGPT API with the MetaQuants dataset")

    # st.info("Coming soon! 🚀")
    # st.stop()

    # Defining the host is optional and defaults to https://api.chartgpt.***REMOVED***
    # See configuration.py for a list of all supported configuration parameters.
    configuration = openapi_client.Configuration(
        # TODO Fetch from environment variable
        host = "http://0.0.0.0:8081"
    )

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

    with st.form(key="chart_api_request"):
        st.markdown("### API endpoint: `/chart`")
        question = st.text_input("question", value="Plot the average APR for the ***REMOVED*** protocol in the past 6 months.")
        submitted = st.form_submit_button("Submit")

        if submitted:
            # TODO Enable API key authentication
            # configuration.api_key['ApiKeyAuth'] = api_key
            configuration.api_key['ApiKeyAuth'] = "abc"
            # Enter a context with an instance of the API client
            with openapi_client.ApiClient(configuration) as api_client:
                with st.spinner("Generating chart..."):
                    # Create an instance of the API class
                    api_instance = openapi_client.DefaultApi(api_client)
                    try:
                        start_time = time.time()
                        # Generate a Plotly chart from a question
                        api_response = api_instance.api_chart_generate_chart({
                            "question": question,
                            "type": "json",
                        })
                        end_time = time.time()
                        sql_query = api_response.query
                        python_code = api_response.code
                        formatted_sql_query = sqlparse.format(sql_query, reindent=True, keyword_case='upper')
                        figure_json_string = api_response.chart
                        figure_json = json.loads(figure_json_string, strict=False)
                        
                        st.markdown("**API response:**")
                        st.json({
                            "query": sql_query,
                            "code": python_code,
                            "chart": "<Plotly chart JSON string>"
                        }, expanded=False)
                        st.markdown(f"**API response time:** {end_time - start_time:.2f} seconds")

                        st.markdown("**Validated SQL query:**")
                        st.markdown(inspect.cleandoc(f"""```sql
                        {formatted_sql_query}
                        """))
                        st.markdown("\n")

                        query_job = client.query(sql_query)
                        results = query_job.result()
                        df = results.to_dataframe()
                        st.dataframe(df)

                        st.markdown("**Validated Python code:**")
                        st.markdown(inspect.cleandoc(f"""```python
                        {python_code}
                        """))
                        
                        st.markdown("**Generated chart:**")
                        st.plotly_chart(figure_json)
                    except openapi_client.ApiException as e:
                        st.warning("API call failed")


    with st.form(key="sql_api_request"):
        st.markdown("### API endpoint: `/sql`")
        question = st.text_input("question", value="Get the average APR for the ***REMOVED*** protocol in the past 6 months.")
        submitted = st.form_submit_button("Submit")

        if submitted:
            # TODO Enable API key authentication
            # configuration.api_key['ApiKeyAuth'] = api_key
            configuration.api_key['ApiKeyAuth'] = "abc"

            # Enter a context with an instance of the API client
            with openapi_client.ApiClient(configuration) as api_client:
                with st.spinner("Generating SQL query..."):
                    # Create an instance of the API class
                    api_instance = openapi_client.DefaultApi(api_client)
                    try:
                        # Generate an SQL query from a question
                        api_response = api_instance.api_sql_generate_sql({
                            "question": question,
                        })
                        sql_query = api_response.query
                        formatted_sql_query = sqlparse.format(sql_query, reindent=True, keyword_case='upper')
                        st.markdown("**API response:**")
                        st.json({"query": sql_query}, expanded=False)
                        st.markdown("**Validated SQL query:**")
                        st.markdown(inspect.cleandoc(f"""```sql
                        {formatted_sql_query}
                        """))
                    except openapi_client.ApiException as e:
                        st.warning("API call failed")

if __name__ == "__main__":
    main()
