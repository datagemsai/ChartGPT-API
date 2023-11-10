"""
The following code was inspired by:
https://github.com/rsarosh/streamlit/tree/main

Remember to enable the Google People API:
https://console.developers.google.com/apis/api/people.googleapis.com/overview
"""

import os
from typing import Optional
from functools import wraps
import jwt

import streamlit as st
from sentry_sdk import set_user

import app
from app import db_users
from app.users import UserCredits


class AuthError(Exception):
    pass


def get_token() -> Optional[str]:
    url = st.experimental_get_query_params()
    if "token" in url:
        token = url["token"][0]
        return token
    else:
        return None


def requires_auth(f=lambda *args, **kwargs: None):
    """Determines if the Access Token is valid"""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token()
        user_id = None
        user_email = None
        if not token:
            st.error(
                "Authorisation failed. Please visit https://app.chartgpt.cadlabs.org to log in."
            )
            st.stop()
        else:
            set_user({"id": "anonymous", "email": "anonymous"})
            with st.spinner("Loading..."):
                try:
                    decoded_token = jwt.decode(
                        token, key=os.environ["JWT_SECRET_KEY"], algorithms=["HS256"]
                    )
                    user_id = decoded_token["user_id"]
                    user_email = decoded_token["user_email"]
                    closed_beta_email_addresses_result = app.db.collection(
                        "closed_beta_email_addresses"
                    ).get()
                    closed_beta_email_addresses = [
                        doc.id.lower() for doc in closed_beta_email_addresses_result
                    ]
                    query_params = st.experimental_get_query_params()
                    chart_id = query_params.get("chart_id", None)
                    if user_id and user_email:
                        # st.toast(f"Logging in...", icon='🔒')
                        set_user({"id": user_id, "email": user_email})
                        if user_email.lower() in closed_beta_email_addresses:
                            # Save user details in Firestore
                            user_ref = db_users.document(user_id)
                            if not user_ref.get().exists:
                                # Create user if they don't exist
                                user_ref.create(
                                    {
                                        "user_id": user_id,
                                        "user_email": user_email,
                                    }
                                )
                            else:
                                # Update user if they exist
                                user_ref.update(
                                    {
                                        "user_id": user_id,
                                        "user_email": user_email,
                                    }
                                )

                            # Create user credits if they don't exist
                            if not (
                                user_credits := UserCredits.collection.get(
                                    key=f"user_credits/{user_id}"
                                )
                            ):
                                user_credits = UserCredits()
                                user_credits.user_id = user_id
                                user_credits.free_credits = 20
                                user_credits.save()

                            # Save user details in session state
                            st.session_state["user_id"] = user_id
                            st.session_state["user_email"] = user_email
                            st.session_state[
                                "user_free_credits"
                            ] = user_credits.free_credits

                            if chart_id:
                                st.experimental_set_query_params(
                                    **{"token": token, "chart_id": chart_id}
                                )
                            else:
                                st.experimental_set_query_params(**{"token": token})
                            # if token:
                            # st.toast(f"Logged in as {user_email}.", icon='🎉')
                        else:
                            st.info(
                                f"{user_email} does not have access to the ChartGPT Marketplace closed beta. Please join the waitlist."
                            )
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



def check_user_credits() -> None:
    # Check user credit usage
    user_query_count = st.session_state["user_query_count"]
    user_free_credits = st.session_state["user_free_credits"]
    free_trial_usage = min(1.0, user_query_count / user_free_credits)
    free_trial_credits_depleted = free_trial_usage >= 1.0
    if free_trial_credits_depleted:
        st.info(
            "Thank you for using ChartGPT! All your free trial queries have been used. We'll get in touch when more are available."
        )
        st.stop()


def show_sign_up_form(user_email="") -> None:
    with st.form("sign_up_form"):
        st.markdown("### Join the waitlist")
        st.markdown("We'll contact you when the next round of users is onboarded.")
        st.text_input("Google account email address", value=user_email, key="email")

        def submit_form():
            email = st.session_state["email"]
            if email:
                app.db.collection("closed_beta_email_addresses_waitlist").document(
                    email
                ).set({})
                st.success("Thanks for signing up! We'll be in touch soon.")
            else:
                st.error("Please enter a valid email address.")
            st.experimental_set_query_params()
            st.stop()

        st.form_submit_button("Sign Up", on_click=submit_form)


def is_user_admin() -> bool:
    return st.session_state["user_email"] in [
        "ben@cadlabs.org",
        "konrad@cadlabs.org",
        "mrsharadgupta@gmail.com",
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
