from copy import copy
from dataclasses import dataclass
import streamlit as st
from PIL import Image
import os
import traceback
from app.config.content import chartgpt_description
import analytics_bot_langchain
from analytics_bot_langchain.app import client
from analytics_bot_langchain.agents.agent_toolkits.bigquery.utils import get_sample_dataframes
from app.config.default import Dataset
from langchain.schema import OutputParserException
from google.cloud.bigquery import Client
import app


# Display app name
PAGE_NAME = "ChartGPT"
st.set_page_config(page_title=PAGE_NAME, page_icon="📈")

st.markdown(
"""
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-5LQTQQQK06"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-5LQTQQQK06');
</script>
""", unsafe_allow_html=True)

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

# logo = Image.open('media/logo.png')
logo = Image.open('media/logo_chartgpt.png')
st.image(logo)
# st.markdown("# " + PAGE_NAME + " 📈")
st.markdown(chartgpt_description)

st.info("""
This is an **early access** version of ChartGPT.
We're still working on improving the model's performance, finding bugs, and adding more features and datasets.
""", icon="🚨")

if app.DISPLAY_USER_UPDATES:
    st.warning("""
    **Update: 10 May 2023, 15:00 CET**

    Due to limits on OpenAI's API, we are now using GPT-3.5 instead of GPT-4. We are actively resolving this with OpenAI support.
    In the meantime you may experience inconsistent or less reliable results.
    """)

if app.MAINTENANCE_MODE:
    st.warning("""
    **Offline for maintenance**

    This app is undergoing maintenance right now.
    Please check back later.

    In the meantime, [check us out on Product Hunt](https://www.producthunt.com/products/chartgpt)!
    """)
    ph_1 = Image.open('media/product_hunt_1.jpeg')
    ph_2 = Image.open('media/product_hunt_2.jpeg')
    ph_3 = Image.open('media/product_hunt_3.jpeg')
    st.image(ph_1)
    st.image(ph_2)
    st.image(ph_3)
    st.stop()

# Import sample question for project
if os.environ["PROJECT"] == "NFTFI":
    from app.config.nftfi import datasets
else:
    from app.config.default import datasets

# dataset_ids = [dataset.id for dataset in datasets]

st.markdown("### 1. Select a dataset")

# st.write("You have access to the following datasets:")
# for dataset in datasets:
#     st.markdown(f"- **{dataset.name}**: {dataset.description}")

# dataset_id = st.selectbox('Select dataset (optional):', [""] + dataset_ids)
dataset = st.selectbox('Select a dataset:', datasets, index=0, label_visibility="collapsed")

# Monkey patching of BigQuery list_datasets()
@dataclass
class MockBQDataset:
    dataset_id: str

Client.list_datasets = lambda *kwargs: [MockBQDataset(dataset.id)]
# tables = list(client.list_tables(dataset.id))
# Client.list_tables = lambda *kwargs: tables

st.markdown(f"#### Dataset description")
st.markdown(dataset.description)

@st.cache_data
def display_sample_dataframes(dataset: Dataset) -> None:
    sample_dataframes = get_sample_dataframes(client, dataset.id)
    for table_id, df in sample_dataframes.items():
        st.markdown(f"**\`{table_id}\` table:**")
        st.dataframe(df.head())

st.markdown(f"#### Table sample data")
display_sample_dataframes(dataset)

st.markdown("### 2. Ask a question")

sample_questions_for_dataset = [""]  # Create unselected option
if dataset:
    # Get a list of all sample questions for the selected dataset
    sample_questions_for_dataset.extend(dataset.sample_questions)
else:
    # Get a list of all sample questions from the dataclass using list comprehension
    sample_questions_for_dataset.extend([item for sublist in [dataset.sample_questions for dataset in datasets] for item in sublist])

sample_question = st.selectbox('Select a sample question (optional):', sample_questions_for_dataset)

# custom_question = None
# if not sample_question:
st.markdown("**OR**")
custom_question = st.text_area(
    "Enter a question:",
    disabled=bool(sample_question)
)

# Button for submitting the input
submit_button = st.button("Submit")

st.markdown("### 3. Get an answer")

# TODO Add coming soon features
# file = ...
# _ = st.download_button(
#     label="Download data (coming soon!)",
#     data=file,
#     # file_name="flower.png",
#     mime="text/csv",
#     disabled=True,
# )
# _ = st.download_button(
#     label="Download chart (coming soon!)",
#     data=file,
#     # file_name="flower.png",
#     mime="image/png",
#     disabled=True,
# )

# If the button is clicked or the user presses enter
if submit_button:
    question = sample_question or custom_question
    with st.spinner('Thinking...'):
        try:
            # get_agent() is cached by Streamlit, where the cache is invalidated if dataset_ids changes
            agent = analytics_bot_langchain.get_agent(dataset_ids=[dataset.id])
            agent.run(input=question)
            st.success('Analytics complete!')
            st.balloons()
        except OutputParserException as e:
            st.error("Analytics failed." + "\n\n" + str(e))
        except Exception as e:
            if app.DEBUG:
                raise e
            else:
                st.error("Analytics failed for unknown reason, please try again.")
else:
    st.markdown("...")

# if 'answers' not in st.session_state:
#     st.session_state['answers'] = {}

# if submit_button:
#     st.session_state.answers[copy(current_question)] = False

# st.write(st.session_state)

# for question, answer in st.session_state.answers.items():
#     with st.expander(label=question, expanded=(not answer)):
#         # If the button is clicked or the user presses enter
#         if not answer:
#             with st.spinner('Thinking...'):
#                 try:
#                     # get_agent() is cached by Streamlit, where the cache is invalidated if dataset_ids changes
#                     agent = analytics_bot_langchain.get_agent(dataset_ids=dataset_ids)
#                     st.session_state.answers[question] = agent.run(input=question)
#                     st.success('Analytics complete!')
#                     st.balloons()
#                     st.write(st.session_state)
#                 except Exception as e:
#                     # For example, catch LangChain OutputParserException:
#                     st.error("Analytics failed." + "\n\n" + str(e))
#                     traceback.print_stack()
#                     st.write(st.session_state)
