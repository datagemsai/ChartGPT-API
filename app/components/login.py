import streamlit as st
import json
from app import db_users
from app.auth import get_user_id_and_email, login_with_google


class Login:
    def __init__(self) -> None:
        if (oauth_code := st.session_state.get("oauth_code", None) or st.experimental_get_query_params().get('code', None)):
            st.session_state["oauth_code"] = oauth_code
            query_params = st.experimental_get_query_params()
            state_param = query_params.get('state', [])
            state = json.loads(state_param[0]) if state_param else {}
            user_id, user_email = get_user_id_and_email()
            if user_id:
                user_ref = db_users.document(user_id)
                user_ref.set({
                    'user_id': user_id,
                    'user_email': user_email,
                })
                st.session_state["user_id"] = user_id
                st.session_state["user_email"] = user_email
                st.experimental_set_query_params(**state)
                st.toast(f"Logged in as {user_email}.", icon='🎉')
            else:
                st.button("Log In with Google", on_click=login_with_google)
                st.error("Authorisation failed.")
                st.stop()
        else:
            st.button("Log In with Google", on_click=login_with_google)
            st.stop()
