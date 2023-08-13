from dataclasses import dataclass
import streamlit as st
from PIL import Image
import os
from google.cloud.firestore_v1.base_query import FieldFilter

import app
from app.config.content import chartgpt_description
from app.auth import get_user_id_and_email, log_out


@dataclass
class Sidebar:
    stop: bool
    clear: bool
    model_temperature: float = float(os.environ.get("DEFAULT_MODEL_TEMPERATURE", 0.0))
    model_verbose_mode: bool = True

    def __init__(self):
        with st.sidebar:
            # Header
            logo = Image.open('media/logo_chartgpt.png')
            st.image(logo)
            st.markdown(chartgpt_description)
            st.divider()

            # User Profile
            user_id, user_email = get_user_id_and_email()

            user_query_count = app.db_queries.where(
                filter=FieldFilter("user_id", "==", user_id)
            ).count().get()[0][0].value

            user_insight_count = app.db_charts.where(
                filter=FieldFilter("user_id", "==", user_id)
            ).count().get()[0][0].value

            st.markdown(f"""
            ### User Profile
            Google account: {user_email}\n
            Number of queries: {user_query_count}\n
            Number of charts generated: {user_insight_count}
            """)

            st.button(f"Log Out", on_click=log_out)

    def display_settings(self):
        with st.sidebar:
            st.divider()
            st.markdown("### Query")
            self.stop = st.button("Stop Analysis")
            self.clear = st.button("Clear Chat History")
            st.divider()

            st.markdown("### Advanced Settings")
            advanced_settings = st.form("advanced_settings")
            self.model_temperature = advanced_settings.slider(
                label="Model temperature",
                min_value=0.0,
                max_value=1.0,
                value=float(os.environ.get("DEFAULT_MODEL_TEMPERATURE", 0.0)),
                step=0.1,
            )
            self.model_verbose_mode = advanced_settings.checkbox("Enable verbose analysis", value=True)
            submitted = advanced_settings.form_submit_button("Update settings")
            if submitted:
                # Clear prior query
                st.session_state.question = ""
