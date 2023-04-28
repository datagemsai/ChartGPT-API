import streamlit as st
from dotenv import load_dotenv, dotenv_values
from copy import copy
import os
import ast
from PIL import Image

# Environment variables take preference over Streamlit secrets
load_dotenv()
# If .env exists, give preference
env_variables = copy(dotenv_values() or os.environ)

for key, value in env_variables.items():
    try:
        # Use ast.literal_eval so that dictionaries are converted appropriately
        converted_value = ast.literal_eval(value.replace("\n", "\\n"))
        print(key)
        print(converted_value)
        env_variables[key] = converted_value
    except Exception as e:
        pass

st.secrets._secrets = env_variables

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

ai_data_scientist_description = """
Master the art of data-driven insights with AI Data Scientist, your dependable resource for generating charts and answering data-centric questions. Let the bot be your personal data assistant, guiding you through your data exploration.​
"""
st.write(ai_data_scientist_description)

st.write("#### radCAD Assistant")
radcad_assistant_description = """
Effortlessly code in our radCAD framework with the help of radCAD Assistant. This intelligent chatbot streamlines your development process and ensures you stay on track. Try it now and witness the power of AI-driven assistance.
"""
st.write(radcad_assistant_description)

st.write("#### AI Token Engineer​")
ai_token_engineer_description = """
Elevate your token engineering expertise with AI Token Engineer. This advanced assistant will guide you through complex tasks and augment your work to enhance your productivity.
"""
st.write(ai_token_engineer_description)

st.write("### 👈 Select a cadGPT AI model from the sidebar​")
