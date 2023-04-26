
import streamlit as st
from functools import partial

# Custom imports
import analytics_bot_langchain
import analytics_bot
"""
# ***REMOVED*** Analytics AGI
"""

ENV = st.secrets["ENV"]
BQ_PROJECT_ID = st.secrets["BQ_PROJECT_ID"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]


class StreamlitWriter:
    def write(self, text):
        # Filter out newlines and other whitespace from the output
        if text.strip():
            st.write(text)

    def flush(self):
        # Streamlit doesn't need flush, but it's part of the file-like object API
        pass

# Reroute stdout to StreamlitWriter
# if ENV == "production":
#     original_stdout = sys.stdout
#     sys.stdout = StreamlitWriter()


sample_questions = {
    "dune_dataset": [
        "Plot the borrow volume across the protocols nftfi, benddao, arcade, jpegd from December 2022 to March 2023",
        "Give three visualizations from dune_dataset",
        "Plot the 30-day median number of users starting from August 2022",
        "Plot the weekly NFT finance market share percentage by unique users",
        "On what date x2y2 had the highest number of users?",
        "Plot the weekly distribution of unique users over time",
        "Using dataset 'dune_dataset', plot the borrow volume over time for nftfi, benddao, arcade, jpegd",
        "Plot the total loan volume per day using Plotly",
        "Return a chart which will help me understand user dynamics across protocols",
        "Give one powerful visualization on dune_dataset which a primary and secondary y-axis or stacked bar charts, and return it with good layout including legend and colors. You may use log y axis",
        # "Give two powerful visualization on dune_dataset which use primary and secondary y-axis and return it with good layout including legend and colors",
    ],
    "nft_lending_aggregated_users": [
        "Plot daily users for nftfi, x2y2 and arcade",
        "Plot the weekly distribution of unique users over time",
        "On what date x2y2 had the highest number of users?",  # data request
    ],
    "nft_lending_aggregated_borrow": [
        "Plot the borrow volume over time for nftfi, benddao, arcade, x2y2, jpegd",
    ],
    "nftfi_loan_data": [
        "Plot the loan principal amount of the top 5 asset classes by volume over time",
    ],
    "run_all_dune": None,
}

sample_agents = {
    'Langchain': analytics_bot_langchain.agents.run,
    'Chartbot': analytics_bot.run,
}


with st.echo(code_location='above'):
    agent = st.selectbox('Select agent:', sample_agents.keys())

    dataset_id = st.selectbox('Select dataset:', sample_questions.keys())

    sample_questions_for_dataset = [""]  # Create unselected option
    sample_questions_for_dataset.extend(sample_questions[dataset_id])
    sample_question = st.selectbox('Select sample question (optional):', sample_questions_for_dataset)

    run = sample_agents[agent]
    if agent == 'Chartbot':
        # Charbot run function (i.e. analytics_bot.run) has more arguments than analytics_bot_langchain.agents.run,
        # so create a partial function of it to match signatures.
        run = partial(run, dataset_id=dataset_id, project_id=BQ_PROJECT_ID)

    if not sample_question:
        question = st.text_input("Enter your question:")
    else:
        question = sample_question

    # Button for submitting the input
    submit_button = st.button("Submit")

    # If the button is clicked or the user presses enter
    if submit_button:
        with st.spinner('Thinking...'):
            run(question=question)
        st.success('Analytics complete!')
        st.balloons()
