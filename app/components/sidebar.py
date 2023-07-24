from dataclasses import dataclass
import streamlit as st
from PIL import Image
import os

from app.config.content import chartgpt_description


@dataclass
class Sidebar:
    model_temperature: float
    model_verbose_mode: bool
    stop: bool
    clear: bool

    def __init__(self):
        with st.sidebar:
            # Initialise ChartGPT header
            logo = Image.open('media/logo_chartgpt.png')
            st.image(logo)
            st.markdown(chartgpt_description)

    def display_settings(self):
        with st.sidebar:
            st.divider()
            self.stop = st.button("Stop Analysis")
            self.clear = st.button("Clear Chat History")
            st.divider()

            st.markdown("### Advanced settings")
            self.model_temperature = st.slider(
                label="Model temperature",
                min_value=0.0,
                max_value=1.0,
                value=float(os.environ.get("DEFAULT_MODEL_TEMPERATURE", 0.0)),
                step=0.1,
            )
            self.model_verbose_mode = st.checkbox("Enable verbose analysis", value=True)
