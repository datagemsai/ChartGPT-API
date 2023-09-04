from dataclasses import dataclass
import streamlit as st
import os
from google.cloud.firestore_v1.base_query import FieldFilter

import app


@dataclass
class Sidebar:
    stop: bool
    clear: bool
    model_temperature: float = float(os.environ.get("DEFAULT_MODEL_TEMPERATURE", 0.0))
    model_verbose_mode: bool = True

    def __init__(self):
        with st.sidebar:
            # User Profile
            user_id = st.session_state["user_id"]
            user_email = st.session_state["user_email"]

            user_query_count = (
                app.db_queries.where(filter=FieldFilter("user_id", "==", user_id))
                .count()
                .get()[0][0]
                .value
            )
            st.session_state["user_query_count"] = user_query_count

            user_chart_count = (
                app.db_charts.where(filter=FieldFilter("user_id", "==", user_id))
                .count()
                .get()[0][0]
                .value
            )
            st.session_state["user_chart_count"] = user_chart_count

            st.markdown(
                f"""
            ### User Profile
            Google account: {user_email}\n
            Total queries performed: {user_query_count}\n
            Total charts generated: {user_chart_count}
            """
            )

            st.divider()

            st.markdown("### Usage")
            user_free_credits = st.session_state["user_free_credits"]
            used_free_credits = min(user_query_count, user_free_credits)
            free_trial_usage = min(1.0, used_free_credits / user_free_credits)
            st.progress(
                free_trial_usage,
                text=f"Free trial usage: {used_free_credits} / {int(user_free_credits)} queries",
            )

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
            self.model_verbose_mode = advanced_settings.checkbox(
                "Enable verbose analysis", value=True
            )
            submitted = advanced_settings.form_submit_button("Update Settings")
            if submitted:
                # Clear prior query
                st.session_state.question = ""
