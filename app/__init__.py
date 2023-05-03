import streamlit as st
from dotenv import load_dotenv
import os


# Load environment variables from .env
load_dotenv()
# If set, Streamlit secrets take preference over environment variables
os.environ.update(st.secrets)

DEBUG = (os.getenv('DEBUG', 'false').lower() == 'true')
if DEBUG: print("Application in debug mode, disable for production")
