import streamlit as st
from dotenv import load_dotenv, dotenv_values
from copy import copy
import os
import ast
from PIL import Image
from app.config.content import *

# Environment variables take preference over Streamlit secrets
load_dotenv()
# If .env exists, give preference
env_variables = copy(dotenv_values() or os.environ)

for key, value in env_variables.items():
    try:
        # Use ast.literal_eval so that dictionaries are converted appropriately
        converted_value = ast.literal_eval(value.replace("\n", "\\n"))
        print(key)
        print(type(converted_value))
        print(converted_value)
        env_variables[key] = converted_value
    except Exception as e:
        pass

print(type(env_variables["gcp_service_account"]))
st.secrets._secrets = env_variables
print(type(st.secrets["gcp_service_account"]))

st.set_page_config(
    page_title="cadGPT",
    page_icon="🧠",
)

image = Image.open('logo.png')
st.image(image)

st.write("# Welcome to cadGPT! 👋")

st.write("## Discover the cadGPT chatbot suite")
st.sidebar.success("Select a model above")

st.write("#### AI Data Scientist")
st.write(ai_data_scientist_description)

st.write("#### radCAD Assistant")
st.write(radcad_assistant_description)

st.write("#### AI Token Engineer​")
st.write(ai_token_engineer_description)

st.write("### 👈 Select a cadGPT AI model from the sidebar​")
