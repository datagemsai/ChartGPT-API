# pylint: disable=C0103
# pylint: disable=C0116

import datetime
import re
from dataclasses import dataclass
from enum import Enum

import plotly.io as pio
import streamlit as st
from google.cloud.bigquery import Client
from langchain.callbacks import get_openai_callback
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import OutputParserException

import app
import app.patches
import app.settings
import chartgpt
from api.guards import is_nda_broken
from app import datasets, db_charts, db_queries
from app.auth import check_user_credits, requires_auth
from app.components.notices import Notices
from app.components.sidebar import Sidebar
from app.config.datasets import Dataset
from app.utils import copy_url_to_clipboard
from chartgpt.agents.agent_toolkits.bigquery.utils import get_sample_dataframes
from chartgpt.app import client

# from st_pages import Page, show_pages, hide_pages


# # add_page_title()
# show_pages(
#     [
#         Page("app/Home.py", "ChartGPT"),
#         Page("app/pages/1_My_Charts.py", "My Charts"),
#     ]
# )

# hide_pages(
#     [
#         # Page("app/pages/1_My_Charts.py", "My Charts"),
#         Page("app/pages/2_Chart_Gallery.py", "Chart Gallery"),
#         Page("app/pages/3_API_Playground.py", "API Playground"),
#         Page("app/pages/4_Admin_Dashboard.py", "Admin Dashboard"),
#     ]
# )

# Show notices
Notices()

query_params = st.experimental_get_query_params()
if "chart_id" in query_params:
    st.button("← Back to ChartGPT", on_click=st.experimental_set_query_params)
    # Get chart from Firestore
    chart_ref = db_charts.document(query_params["chart_id"][0])
    chart = chart_ref.get()
    if chart.exists:
        chart_json = chart.to_dict()["json"]
        chart = pio.from_json(chart_json)
        st.plotly_chart(chart, use_container_width=True)
        st.stop()
    else:
        st.error("Chart not found")
        st.stop()


@requires_auth
def main(user_id, _user_email):
    # Initialise Streamlit components
    sidebar = Sidebar()
    sidebar.display_settings()

    padding_top = 2
    padding_left = padding_right = 1
    padding_bottom = 10

    styl = f"""
    <style>
        .appview-container .main .block-container{{
            padding-top: {padding_top}rem;
            padding-right: {padding_right}rem;
            padding-left: {padding_left}rem;
            padding-bottom: {padding_bottom}rem;
        }}
    </style>
    """
    st.markdown(styl, unsafe_allow_html=True)

    # Check user credits
    check_user_credits()

    st.markdown("### 1. Select a dataset 📊")

    dataset: Dataset = st.selectbox(
        "Select a dataset:", datasets, index=0, label_visibility="collapsed"
    ) or Dataset(name="", project="", id="", description="", sample_questions=[])
    st.markdown(dataset.description)

    # Monkey patching of BigQuery list_datasets()
    @dataclass
    class MockBQDataset:
        dataset_id: str

    Client.list_datasets = lambda *kwargs: [MockBQDataset(dataset.id)]  # type: ignore

    # tables = list(client.list_tables(dataset.id))
    # Client.list_tables = lambda *kwargs: tables

    print(datasets)
    print(dataset)

    @st.cache_data
    def display_sample_dataframes(dataset: Dataset) -> None:
        sample_dataframes = get_sample_dataframes(client, dataset)
        for table_id, df in sample_dataframes.items():
            with st.expander(f"**\`{table_id}\` table sample data**"):
                st.dataframe(df.head())

    display_sample_dataframes(dataset)

    st.info(
        """
    Datasets are updated daily at 12AM CET.

    If you have a request for a specific dataset or use case, [please reach out!](https://ne6tibkgvu7.typeform.com/to/jZnnMGjh)
    """
    )

    st.markdown("### 2. Ask a question 🤔")

    sample_questions_for_dataset = [""]  # Create unselected option
    if dataset:
        # Get a list of all sample questions for the selected dataset
        sample_questions_for_dataset.extend(dataset.sample_questions)
    else:
        # Get a list of all sample questions from the dataclass using list comprehension
        sample_questions_for_dataset.extend(
            [
                item
                for sublist in [dataset.sample_questions for dataset in datasets]
                for item in sublist
            ]
        )

    def set_question() -> None:
        st.session_state.question = (
            st.session_state.chat_input or st.session_state.sample_question
        )

    st.chat_input("Enter a question...", key="chat_input", on_submit=set_question)

    st.selectbox(
        label="Select a sample question (optional):",
        options=sample_questions_for_dataset,
        key="sample_question",
        on_change=set_question,
    )

    if sidebar.clear:
        st.session_state.question = ""
    question = st.session_state.get("question", "")

    class QueryStatus(Enum):
        SUBMITTED = 1
        SUCCEEDED = 2
        FAILED = 3

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Display chat messages from history on app rerun
    if sidebar.clear:
        st.session_state["messages"] = []
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            if message.get("type", None) == "chart":
                chart = message["content"]
                st.plotly_chart(chart, use_container_width=True)
                # TODO Re-enable sharing of charts
                # chart_id = message["chart_id"]
                # st.button(
                #     "Copy chart URL",
                #     type="primary",
                #     key=chart_id,
                #     on_click=copy_url_to_clipboard,
                #     args=(f"/?chart_id={chart_id}",),
                # )
            else:
                st.markdown(message["content"])

    class StreamHandler(BaseCallbackHandler):
        def on_llm_new_token(self, token: str, **kwargs) -> None:
            if "text" not in st.session_state:
                # NOTE This is necessary because of a bug in Streamlit state after st.stop()
                return
            st.session_state["text"] += token
            # Using regex, find ``` followed by a word and add a newline after ``` unless the word is "python"
            st.session_state["text"] = re.sub(
                r"```(?=\w)(?!python)", "```\n\n", st.session_state["text"]
            )
            # Using regex, find and remove `Action Input:` etc.
            st.session_state["text"] = re.sub(
                r"Action Input:\s*", "", st.session_state["text"], flags=re.IGNORECASE
            )
            st.session_state["text"] = re.sub(
                r"Analysis Complete:\s*",
                "",
                st.session_state["text"],
                flags=re.IGNORECASE,
            )
            st.session_state["empty_container"].markdown(st.session_state["text"])

    # get_agent() is cached by Streamlit, where the cache is invalidated if dataset_ids changes
    # if "agent" not in st.session_state:
    stream_handler = StreamHandler()
    st.session_state["agent"] = chartgpt.get_agent(
        secure_execution=True,
        temperature=sidebar.model_temperature,
        datasets=[dataset],
        callbacks=[stream_handler],
    )

    if question:
        if sidebar.stop:
            st.stop()
        # Create new Firestore document with unique ID:
        # query_ref = db_queries.document()
        # Create new Firestore document with timestamp ID:
        timestamp_start = str(datetime.datetime.now())
        query_ref = db_queries.document(timestamp_start)
        query_metadata = {
            "user_id": user_id,
            "env": app.ENV,
            "timestamp_start": timestamp_start,
            "query": question,
            "dataset_id": f"{dataset.project}.{dataset.id}",
            "status": QueryStatus.SUBMITTED.name,
            "model_temperature": sidebar.model_temperature,
        }
        query_ref.set(query_metadata)
        st.session_state["query_metadata"] = query_metadata

        # Display user message in chat message container
        st.session_state["messages"].append({"role": "user", "content": question})
        st.chat_message("user").write(question)

        if not sidebar.model_verbose_mode:
            question += "\n\nRespond with one output. Do not explain your process."

        # with st.spinner('Thinking...'):
        with st.chat_message("assistant"):
            assistant_response = "Coming right up, let me think..."
            st.session_state["messages"].append(
                {"role": "assistant", "content": assistant_response}
            )
            st.write(assistant_response)
            try:
                if not is_nda_broken(question):
                    with get_openai_callback() as cb:
                        container = st.container()
                        st.session_state["text"] = ""
                        st.session_state["container"] = container
                        st.session_state["empty_container"] = st.session_state[
                            "container"
                        ].empty()
                        response = st.session_state.agent(
                            question
                        )  # callbacks=[stream_handler]
                        app.logger.info("response = %s", response)
                        app.logger.info(cb)
                else:
                    raise OutputParserException("Your question breaks the NDA.")

                final_output = response["output"]
                intermediate_steps = response["intermediate_steps"]
                timestamp_end = str(datetime.datetime.now())
                query_ref.update(
                    {
                        "timestamp_end": timestamp_end,
                        "status": QueryStatus.SUCCEEDED.name,
                        "final_output": final_output,
                        "number_of_steps": len(intermediate_steps),
                        "steps": [str(step) for step in intermediate_steps],
                        "total_tokens": cb.total_tokens,
                        "prompt_tokens": cb.prompt_tokens,
                        "completion_tokens": cb.completion_tokens,
                        "estimated_total_cost": cb.total_cost,
                    }
                )

                st.success(
                    """
                    Analysis complete!
        
                    Enjoying ChartGPT and eager for more? Join our waitlist to stay ahead with the latest updates.
                    You'll also be among the first to gain access when we roll out new features! Sign up [here](https://ne6tibkgvu7.typeform.com/to/ZqbYQVE6).
                    """
                )
            except OutputParserException as e:
                timestamp_end = str(datetime.datetime.now())
                query_ref.update(
                    {
                        "timestamp_end": timestamp_end,
                        "status": QueryStatus.FAILED.name,
                        "failure": str(e),
                    }
                )
                st.error(
                    "Analysis failed."
                    + "\n\n"
                    + str(e)
                    + "\n\n"
                    + "[We welcome any feedback or bug reports.](https://ne6tibkgvu7.typeform.com/to/jZnnMGjh)"
                )
            except Exception as e:
                timestamp_end = str(datetime.datetime.now())
                query_ref.update(
                    {
                        "timestamp_end": timestamp_end,
                        "status": QueryStatus.FAILED.name,
                        "failure": str(e),
                    }
                )
                if app.DEBUG:
                    raise e
                else:
                    st.error(
                        "Analysis failed for unknown reason, please try again."
                        + "\n\n"
                        + "[We welcome any feedback or bug reports.](https://ne6tibkgvu7.typeform.com/to/jZnnMGjh)"
                    )
            finally:
                st.session_state.question = ""
                # st.markdown("How was the analysis?")
                # col1, col2 = st.columns([.1, 1])
                # positive_review = col1.button("👍")
                # negative_review = col2.button("👎")
                # if positive_review or negative_review:
                #     user_rating = 1 if positive_review else 0
                #     query_ref.update({'user_rating': user_rating})


if __name__ == "__main__":
    main()
