import streamlit as st
from dotenv import load_dotenv
import os


# Load environment variables from .env
load_dotenv()
# If set, Streamlit secrets take preference over environment variables
os.environ.update(st.secrets)
