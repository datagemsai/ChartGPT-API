from dataclasses import dataclass
import streamlit as st
from PIL import Image

from app.config.content import chartgpt_description


@dataclass
class Sidebar:
    model_temperature: float
    model_verbose_mode: bool
    stop: bool
    clear: bool

    def __init__(self):
        with st.sidebar:
            logo = Image.open('media/logo_chartgpt.png')
            st.image(logo)
            st.markdown(chartgpt_description)
            st.divider()

            self.model_temperature = st.slider("Model temperature", 0.0, 1.0, 0.0, 0.1)
            self.model_verbose_mode = st.checkbox("Enable verbose analysis", value=False)
            self.stop = st.button("Stop Analysis")
            self.clear = st.button("Clear Chat History")
