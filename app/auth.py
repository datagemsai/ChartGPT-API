"""
The following code was inspired by:
https://github.com/rsarosh/streamlit/tree/main

Remember to enable the Google People API:
https://console.developers.google.com/apis/api/people.googleapis.com/overview
"""

import streamlit as st
from streamlit.components.v1 import html
import os
import asyncio
# See https://frankie567.github.io/httpx-oauth/oauth2/
from httpx_oauth.clients.google import GoogleOAuth2
from typing import Optional, Tuple
import json
import app
from app import db_users
from app.cookies import cookies
from app.cookies_v2 import clear_cookies
from sentry_sdk import set_user
from app.config.content import chartgpt_description
from app.users import UserCredits


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
    clear_cookies()
    for key in ["access_token", "user_id", "user_email"]:
        if key in cookies:
            cookies[key] = ""
            del cookies[key]
        if key in st.session_state:
            del st.session_state[key]

import jwt
from functools import wraps


class AuthError(Exception):
    pass

def get_token() -> Optional[str]:
    url = st.experimental_get_query_params()
    if 'token' in url:
        token = url['token'][0]
        return token
    else:
        return None

def requires_auth(f=lambda *args, **kwargs: None):
    """Determines if the Access Token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token()
        user_id = None
        user_email = None
        if not token:
            st.error("Authorisation failed. Please visit https://app.chartgpt.***REMOVED*** to log in.")
            st.stop()
        else:
            set_user({"id": "anonymous", "email": "anonymous"})
            try:
                decoded_token = jwt.decode(token, key=os.environ["JWT_SECRET_KEY"], algorithms=['HS256'])
                user_id = decoded_token['user_id']
                user_email = decoded_token['user_email']
                closed_beta_email_addresses_result = app.db.collection('closed_beta_email_addresses').get()
                closed_beta_email_addresses = [doc.id.lower() for doc in closed_beta_email_addresses_result]
                query_params = st.experimental_get_query_params()
                chart_id = query_params.get('chart_id', None)
                if user_id and user_email:
                    # st.toast(f"Logging in...", icon='🔒')
                    set_user({"id": user_id, "email": user_email})
                    if user_email.lower() in closed_beta_email_addresses:
                        # Save user details in Firestore
                        user_ref = db_users.document(user_id)
                        if not user_ref.get().exists:
                            # Create user if they don't exist
                            user_ref.create({
                                'user_id': user_id,
                                'user_email': user_email,
                            })
                        else:
                            # Update user if they exist
                            user_ref.update({
                                'user_id': user_id,
                                'user_email': user_email,
                            })

                        # Create user credits if they don't exist
                        if not (user_credits := UserCredits.collection.get(key=f"user_credits/{user_id}")):
                            user_credits = UserCredits()
                            user_credits.user_id = user_id
                            user_credits.free_credits = 20
                            user_credits.save()

                        # Save user details in session state
                        st.session_state["user_id"] = user_id
                        st.session_state["user_email"] = user_email
                        st.session_state["user_free_credits"] = user_credits.free_credits

                        if chart_id:
                            st.experimental_set_query_params(**{"token": token, "chart_id": chart_id})
                        else:
                            st.experimental_set_query_params(**{"token": token})
                        # if token:
                            # st.toast(f"Logged in as {user_email}.", icon='🎉')
                    else:
                        st.info(f"{user_email} does not have access to the ChartGPT Marketplace closed beta. Please join the waitlist.")
                        show_sign_up_form(user_email=user_email)
                        st.stop()
                else:
                    st.stop()
            except jwt.ExpiredSignatureError:
                st.info("Your session has expired. Please log in again.")
                st.stop()
            except jwt.InvalidTokenError:
                st.error("Authorisation failed.")
                st.stop()
            if not user_id and user_email:
                raise AuthError("User is not authenticated")
            return f(user_id, user_email, *args, **kwargs)
    if not f:
        decorated()
    else:
        return decorated


def authenticate_user() -> None:
    hydrate_session_state()
    oauth_code_list = None
    access_token = None
    if (
        (oauth_code_list := st.experimental_get_query_params().get('code', None))
        or (access_token := st.session_state.get('access_token', None))
    ):
        if oauth_code_list:
            st.session_state["oauth_code"] = oauth_code_list[0]
        query_params = st.experimental_get_query_params()
        state_param = query_params.get('state', [])
        state = json.loads(state_param[0]) if state_param else {}
        chart_id = state.get('chart_id', None) or query_params.get('chart_id', None)
        user_id, user_email = get_user_id_and_email()
        closed_beta_email_addresses_result = app.db.collection('closed_beta_email_addresses').get()
        closed_beta_email_addresses = [doc.id.lower() for doc in closed_beta_email_addresses_result]
        set_user({"id": "anonymous", "email": "anonymous"})
        if user_id and user_email:
            set_user({"id": user_id, "email": user_email})
            if user_email.lower() in closed_beta_email_addresses:
                # Save user details in Firestore
                user_ref = db_users.document(user_id)
                if not user_ref.get().exists:
                    # Create user if they don't exist
                    user_ref.create({
                        'user_id': user_id,
                        'user_email': user_email,
                    })
                else:
                    # Update user if they exist
                    user_ref.update({
                        'user_id': user_id,
                        'user_email': user_email,
                    })

                # Create user credits if they don't exist
                if not (user_credits := UserCredits.collection.get(key=f"user_credits/{user_id}")):
                    user_credits = UserCredits()
                    user_credits.user_id = user_id
                    user_credits.free_credits = 20
                    user_credits.save()

                # Save user details in session state
                st.session_state["user_id"] = user_id
                st.session_state["user_email"] = user_email
                st.session_state["user_free_credits"] = user_credits.free_credits

                if chart_id:
                    st.experimental_set_query_params(**{"chart_id": chart_id})
                else:
                    st.experimental_set_query_params()
                update_auth_cookies()
                if oauth_code_list:
                    st.toast(f"Logged in as {user_email}.", icon='🎉')
            else:
                display_log_in_header()
                st.info(f"{user_email} does not have access to the ChartGPT Marketplace closed beta. Please join the waitlist.")
                show_sign_up_form(user_email=user_email)
                clear_auth_cookies_and_state()
                st.experimental_set_query_params()
                st.stop()
        else:
            display_log_in_header()
            # If access token exists, then session has expired
            if access_token:
                st.info("Your session has expired. Please log in again.")
            else:
                st.error("Authorisation failed.")
            # show_sign_up_form(user_email=user_email)
            clear_auth_cookies_and_state()
            st.experimental_set_query_params()
            st.stop()
    else:
        display_log_in_header()
        join_waitlist = st.button("Join the Waitlist")
        if join_waitlist:
            show_sign_up_form()
        clear_auth_cookies_and_state()
        st.experimental_set_query_params()
        st.stop()

def check_user_credits() -> None:
    # Check user credit usage
    user_query_count = st.session_state["user_query_count"]
    user_free_credits = st.session_state["user_free_credits"]
    free_trial_usage = min(1.0, user_query_count / user_free_credits)
    free_trial_credits_depleted = free_trial_usage >= 1.0
    if free_trial_credits_depleted:
        st.info("Thank you for using ChartGPT! All your free trial queries have been used. We'll get in touch when more are available.")
        st.stop()

def display_log_in_header() -> None:
    st.markdown("## Welcome to the ChartGPT Marketplace!")
    st.markdown(chartgpt_description)
    st.button("Log In with Google", on_click=login_with_google, key="login", type="primary")

def show_sign_up_form(user_email="") -> None:
    with st.form("sign_up_form"):
        st.markdown("### Join the waitlist")
        st.markdown("We'll contact you when the next round of users is onboarded.")
        st.text_input("Google account email address", value=user_email, key="email")
        def submit_form():
            email = st.session_state["email"]
            if email:
                app.db.collection('closed_beta_email_addresses_waitlist').document(email).set({})
                st.success("Thanks for signing up! We'll be in touch soon.")
            else:
                st.error("Please enter a valid email address.")
            clear_auth_cookies_and_state()
            st.experimental_set_query_params()
            st.stop()
        st.form_submit_button("Sign Up", on_click=submit_form)

def is_user_admin() -> bool:
    return st.session_state["user_email"] in [
        "ben@***REMOVED***",
        "konrad@***REMOVED***",
        "***REMOVED***"
    ]

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
