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
from app import db_users
from app.cookies import cookies
from sentry_sdk import set_user


CLIENT_ID = os.environ['GOOGLE_OAUTH_CLIENT_ID']
CLIENT_SECRET = os.environ['GOOGLE_OAUTH_CLIENT_SECRET']
REDIRECT_URI = os.environ['REDIRECT_URI']


def hydrate_session_state():
    for key, value in cookies.items():
        st.session_state[key] = value


def update_auth_cookies():
    for key in ["access_token", "user_id", "user_email"]:
        cookies[key] = st.session_state[key]
    cookies.save()


def clear_auth_cookies_and_state():
    html("""
    <script language="javascript">
        (function () {
            var cookies = document.cookie.split("; ");
            for (var c = 0; c < cookies.length; c++) {
                var d = window.location.hostname.split(".");
                while (d.length > 0) {
                    var cookieBase = encodeURIComponent(cookies[c].split(";")[0].split("=")[0]) + '=; expires=Thu, 01-Jan-1970 00:00:01 GMT; domain=' + d.join('.') + ' ;path=';
                    var p = location.pathname.split('/');
                    document.cookie = cookieBase + '/';
                    while (p.length > 0) {
                        document.cookie = cookieBase + p.join('/');
                        p.pop();
                    };
                    d.shift();
                }
            }
        })();
    </script>
    """)
    for key in ["access_token", "user_id", "user_email"]:
        if key in cookies:
            cookies[key] = ""
            del cookies[key]
        if key in st.session_state:
            del st.session_state[key]


class Login:
    def __init__(self) -> None:
        hydrate_session_state()
        if ((oauth_code_list := st.experimental_get_query_params().get('code', None)) or st.session_state.get('access_token', None)):
            if oauth_code_list:
                st.session_state["oauth_code"] = oauth_code_list[0]
            query_params = st.experimental_get_query_params()
            state_param = query_params.get('state', [])
            state = json.loads(state_param[0]) if state_param else {}
            chart_id = state.get('chart_id', None) or query_params.get('chart_id', None)
            user_id, user_email = get_user_id_and_email()
            closed_beta_email_addresses_result = app.db.collection('closed_beta_email_addresses').get()
            closed_beta_email_addresses = [doc.id for doc in closed_beta_email_addresses_result]
            set_user({"id": "anonymous", "email": "anonymous"})
            if user_id and user_email:
                set_user({"id": user_id, "email": user_email})
                if user_email in closed_beta_email_addresses:
                    user_ref = db_users.document(user_id)
                    user_ref.set({
                        'user_id': user_id,
                        'user_email': user_email,
                    })
                    st.session_state["user_id"] = user_id
                    st.session_state["user_email"] = user_email
                    if chart_id:
                        st.experimental_set_query_params(**{"chart_id": chart_id})
                    else:
                        st.experimental_set_query_params()
                    update_auth_cookies()
                    if oauth_code_list:
                        st.toast(f"Logged in as {user_email}.", icon='🎉')
                else:
                    st.button("Log In with Google", on_click=login_with_google, key="login_1")
                    with st.form("sign_up_form"):
                        st.markdown("### Please sign up for the ChartGPT closed beta")
                        st.markdown("We'll contact you when the next round of users is onboarded.")
                        st.text_input("Email address", value=user_email, key="email")
                        def submit_form():
                            email = st.session_state["email"]
                            if email:
                                app.db.collection('closed_beta_email_addresses_waitlist').document(email).set({})
                                st.success("Thanks for signing up! We'll be in touch soon.")
                            else:
                                st.error("Please enter a valid email address.")
                        st.form_submit_button("Sign Up", on_click=submit_form)
                    clear_auth_cookies_and_state()
                    st.experimental_set_query_params()
                    st.stop()
            else:
                st.button("Log In with Google", on_click=login_with_google, key="login_2")
                st.error("Authorisation failed.")
                clear_auth_cookies_and_state()
                st.experimental_set_query_params()
                st.stop()
        else:
            st.button("Log In with Google", on_click=login_with_google, key="login_3")
            clear_auth_cookies_and_state()
            st.experimental_set_query_params()
            st.stop()


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
    oauth_user_email: Optional[str] = st.session_state.get('user_email', None)
    oauth_code: Optional[str] = st.session_state.get('oauth_code', None)
    oauth_access_token: Optional[str] = st.session_state.get('access_token', None)

    oauth_client = initialize_oauth_client(oauth_user_email)

    if not oauth_access_token and oauth_code:
        oauth_access_token = obtain_oauth_access_token(oauth_client, oauth_code)
        st.session_state['access_token'] = oauth_access_token
        if oauth_access_token is None:
            app.logger.warning("Failed to obtain OAuth access token")
            return None, None

    if not oauth_access_token:
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


@st.cache_resource(ttl="1h", show_spinner=False)
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


def log_out() -> None:
    clear_auth_cookies_and_state()
