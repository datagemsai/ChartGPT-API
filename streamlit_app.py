from enum import Enum
import streamlit as st

from dotenv import load_dotenv, dotenv_values
import os
import ast
from copy import copy

# Monkey patching
from plotly.graph_objs._figure import Figure
def st_show(self):
    st.plotly_chart(self, use_container_width=True)
Figure.show = st_show 

# Environment variables take preference over Streamlit secrets
load_dotenv()
# If .env exists, give preference
env_variables = copy(dotenv_values() or os.environ)

for key, value in env_variables.items():
    try:
        # Use ast.literal_eval so that dictionaries are converted appropriately
        env_variables[key] = ast.literal_eval(value.replace("\n", "\\n"))
    except Exception as e:
        pass

st.secrets._secrets = env_variables

# Custom imports that require Streamlit secrets
import analytics_bot_langchain
import analytics_bot

# Display app name
st.markdown(st.secrets["APP_NAME"])

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
}

class Agents(Enum):
    LangChain = 1
    ChartBot = 2

# Streamlit app execution
# agent = st.selectbox('Select agent:', Agents._member_names_)
agent = Agents.LangChain.name

sample_questions_for_dataset = [""]  # Create unselected option
dataset_ids = [""]  # Create unselected option
dataset_ids.extend(sample_questions.keys())

# TODO assert sample_questions.keys()

dataset_id = st.selectbox('Select dataset (optional):', dataset_ids)

if dataset_id:
    sample_questions_for_dataset.extend(sample_questions[dataset_id])
else:
    sample_questions_for_dataset.extend([item for sublist in sample_questions.values() for item in sublist])

sample_question = st.selectbox('Select sample question (optional):', sample_questions_for_dataset)

if not sample_question:
    question = st.text_input("Enter your question:")
else:
    question = sample_question

# Button for submitting the input
submit_button = st.button("Submit")

# If the button is clicked or the user presses enter
if submit_button:
    with st.spinner('Thinking...'):
        try:
            if agent == Agents.LangChain.name:
                analytics_bot_langchain.run(question=question)
                st.success('Analytics complete!')
                st.balloons()
            elif agent == Agents.ChartBot.name:
                analytics_bot.run(question=question, dataset_id=dataset_id)
                st.success('Analytics complete!')
                st.balloons()
            else:
                st.error(f'Invalid agent type: {agent}')
        except Exception as e:
            # For example, catch LangChain OutputParserException:
            st.error("Analytics failed." + "\n\n" + str(e))
