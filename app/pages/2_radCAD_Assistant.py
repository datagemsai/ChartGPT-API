from collections import namedtuple
from typing import Dict
import altair as alt
import math
import pandas as pd
import streamlit as st
from PIL import Image
import os
from dotenv import load_dotenv, dotenv_values
from copy import copy
import ast

from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import DeepLake
from langchain.embeddings.openai import OpenAIEmbeddings

from app.Intro import radcad_assistant_description

st.markdown("# radCAD Assistant")
st.markdown(radcad_assistant_description)

st.warning('This assistant is still in beta and learning from the radCAD knowledge base.')

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

# def set_secret_from_env(secret_key: str) -> None:
#     st.secrets[secret_key] = os.environ[secret_key]

# load_dotenv()
# set_secret_from_env("OPENAI_API_KEY")
# set_secret_from_env("ACTIVELOOP_TOKEN")

# image = Image.open('logo.png')
# st.image(image)

@st.cache_resource(show_spinner=False)
def load_model() -> ConversationalRetrievalChain:
    # Load texts from DeepLake vectore store
    embeddings = OpenAIEmbeddings()
    dataset_path = 'hub://cadlabs/radcad_v3'
    db = DeepLake(dataset_path=dataset_path, read_only=True, embedding_function=embeddings)

    # Configure retriever search configuration
    retriever = db.as_retriever()
    retriever.search_kwargs['distance_metric'] = 'cos'
    retriever.search_kwargs['fetch_k'] = 100
    retriever.search_kwargs['maximal_marginal_relevance'] = True
    retriever.search_kwargs['k'] = 20

    # Create instance of OpenAI GPT model and chain
    model = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.7)
    qa = ConversationalRetrievalChain.from_llm(model, retriever=retriever)
    return qa

with st.spinner('Loading model...'):
    qa = load_model()

# Create list to store chat history for session
chat_history = []
# Text input for asking a question
question = st.text_input(label='Enter your question:', label_visibility='hidden', placeholder='Enter your question...')

# If the button is clicked or the user presses enter
if question:
    with st.spinner('Thinking...'):
        result = qa({'question': question, 'chat_history': chat_history})
        answer = result['answer']
    st.write(answer)

faqs = [
    'What is radCAD?',
    'What is a State Variable?',
    'How do I create a new State Variable?',
    'What Python type is a State Variable?',
    'How can I execute a simulation using multiprocessing?',
]

@st.cache_data(persist=True, show_spinner=False)
def get_faq_answers(_qa_chain, faqs=faqs) -> Dict[str, str]:
    return {question: _qa_chain({'question': question, 'chat_history': []})['answer'] for question in faqs}

with st.spinner('Answering FAQs...'):
    faq_answers = get_faq_answers(_qa_chain=qa)

st.markdown('## FAQs')

for question, answer in faq_answers.items():
    st.markdown(f'**{question}**')
    st.markdown(f'{answer}')
