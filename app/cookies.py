import os
import streamlit as st
from app.streamlit_cookies_manager.encrypted_cookie_manager import EncryptedCookieManager


def get_cookies():
    # This should be on top of your script
    cookies_manager: EncryptedCookieManager = EncryptedCookieManager(
        # This prefix will get added to all your cookie names.
        # This way you can run your app on Streamlit Cloud without cookie name clashes with other apps.
        prefix="chartgpt",
        # You should really setup a long COOKIES_PASSWORD secret if you're running on Streamlit Cloud.
        password=os.environ["COOKIES_PASSWORD"],
    )
    return cookies_manager

cookies = get_cookies()
if not cookies.ready():
    # Wait for the component to load and send us current cookies.
    st.stop()
