from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st

# Custom imports
import sys
from nftBot.ChartBot.single_stream import run
import plotly.express as px

"""
# NFTfi Analytics AGI
"""

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
# original_stdout = sys.stdout
# sys.stdout = StreamlitWriter()


sample_questions = {
    "nft_lending_aggregated_borrow": [
        "Plot the loan principal amount across nftfi, benddao, arcade, x2y2, jpegd",
    ],
    "nftfi_loan_data": [
    ],
}


with st.echo(code_location='above'):
    dataset_id = st.selectbox(
        'Select dataset:', (
                'nft_lending_aggregated_borrow',
                'dune_dataset',
                'nftfi_loan_data'
            )
        )
    
    sample_questions_for_dataset = [""]
    sample_questions_for_dataset.extend(sample_questions[dataset_id])
    
    sample_question = st.selectbox(
        'Select sample question (optional):', (
            sample_questions_for_dataset
        )
    )

    if not sample_question:
        question = st.text_input("Enter your question:")
    else:
        question = sample_question

    # Button for submitting the input
    submit_button = st.button("Submit")

    # If the button is clicked or the user presses enter
    if submit_button:
        with st.spinner('Thinking...'):
            run(questions=[{'question': question}], dataset_id=dataset_id, project_id=BQ_PROJECT_ID)
        st.success('Analytics complete!')
        st.balloons()
