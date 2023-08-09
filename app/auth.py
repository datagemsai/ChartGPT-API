"""
The following code was inspired by https://github.com/rsarosh/streamlit/tree/main

Remember to enable the Google People API: https://console.developers.google.com/apis/api/people.googleapis.com/overview
"""

from typing import Optional
import streamlit as st
from streamlit.components.v1 import html
import os
from numpy import void
import asyncio
# See https://frankie567.github.io/httpx-oauth/oauth2/
from httpx_oauth.clients.google import GoogleOAuth2
from typing import Optional, Tuple
import json
import app


CLIENT_ID = os.environ['GOOGLE_OAUTH_CLIENT_ID']
CLIENT_SECRET = os.environ['GOOGLE_OAUTH_CLIENT_SECRET']
REDIRECT_URI = os.environ['REDIRECT_URI']


def basic_auth():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == os.environ["PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True


async def get_authorization_url(client: GoogleOAuth2, redirect_uri: str, state: str):
    authorization_url = await client.get_authorization_url(
        redirect_uri=redirect_uri,
        scope=["profile", "email"],
        state=state,
        extras_params={"access_type": "offline"},
    )
    return authorization_url


async def get_access_token(client: GoogleOAuth2, redirect_uri: str, code: str):
    token = await client.get_access_token(code, redirect_uri)
    return token["access_token"]


async def get_email(client: GoogleOAuth2, token: str):
    user_id, user_email = await client.get_id_email(token)
    return str(user_id.split("/")[-1]), user_email


def login_with_google():
    client: GoogleOAuth2 = GoogleOAuth2(CLIENT_ID, CLIENT_SECRET)
    state = {}
    if chart_id := st.experimental_get_query_params().get('chart_id', None):
        state["chart_id"] = chart_id
    authorization_url = asyncio.run(get_authorization_url(client, REDIRECT_URI, json.dumps(state)))
    script = f"""
        <script type="text/javascript">
            parent.window.open('{authorization_url}', '_self');
        </script>
    """
    html(script)


def get_user_id_and_email() -> Tuple[Optional[str], Optional[str]]:
    oauth_user_email = st.session_state.get('user_email', None)
    oauth_access_token = st.session_state.get('access_token', None)
    oauth_code = st.session_state.get('oauth_code', None)

    oauth_client = initialize_oauth_client(oauth_user_email)

    if oauth_access_token is None and oauth_code:
        oauth_access_token = obtain_oauth_access_token(oauth_client, oauth_code)
        if oauth_access_token is None:
            app.logger.warning("Failed to obtain OAuth access token")
            return None, None

    if oauth_access_token is None:
        app.logger.warning("No OAuth access token found")
        return None, None

    try:
        user_id, user_email = asyncio.run(get_email(oauth_client, oauth_access_token))
    except Exception as e:
        app.logger.error(f"Failed to get user ID and email: {e}")
        return None, None

    if user_id:
        return user_id, user_email
    else:
        app.logger.warning("No user ID found")
        return None, None


def initialize_oauth_client(oauth_user_email: Optional[str]) -> GoogleOAuth2:
    if oauth_user_email:
        return GoogleOAuth2(oauth_user_email, CLIENT_SECRET)
    else:
        return GoogleOAuth2(CLIENT_ID, CLIENT_SECRET)


def obtain_oauth_access_token(oauth_client: GoogleOAuth2, oauth_code: str) -> Optional[str]:
    try:
        access_token = asyncio.run(get_access_token(oauth_client, REDIRECT_URI, oauth_code))
        st.session_state['access_token'] = access_token
        return access_token
    except Exception as e:
        app.logger.error(f"Error while obtaining OAuth access token: {e}")
        return None
