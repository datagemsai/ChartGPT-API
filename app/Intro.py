import streamlit as st
from PIL import Image

from config.content import *

st.set_page_config(
    page_title="cadGPT",
    page_icon="🧠",
)

image = Image.open("logo.png")
st.image(image)

st.write("# Welcome to cadGPT! 👋")

st.write("## Discover the cadGPT chatbot suite")
st.sidebar.success("Select a model above")

st.write("#### AI Data Scientist")
st.write(ai_data_scientist_description)

st.write("#### radCAD Assistant")
st.write(radcad_assistant_description)

st.write("#### AI Token Engineer")
st.write(ai_token_engineer_description)

st.write("### 👈 Select a cadGPT AI model from the sidebar")
