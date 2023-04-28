import streamlit as st
from app.Intro import ai_token_engineer_description


PAGE_NAME = "AI Token Engineer"
st.set_page_config(page_title=PAGE_NAME, page_icon="🧠")
st.markdown("# " + PAGE_NAME + " 🧠")
st.markdown(ai_token_engineer_description)
st.success("Coming soon!")
