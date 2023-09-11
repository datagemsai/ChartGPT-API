import json
import logging
import os
import sys
from importlib import import_module

import firebase_admin
import sentry_sdk
import streamlit as st
from dotenv import load_dotenv
from firebase_admin import firestore
from google.cloud import bigquery
from google.oauth2 import service_account
from sentry_sdk import capture_exception, set_tag

# Load environment variables from .env
load_dotenv()
# If set, Streamlit secrets take preference over environment variables
os.environ.update(st.secrets)

ENV = os.environ.get("ENV", "LOCAL")
PROJECT = os.environ.get("PROJECT", None)
URL = os.environ.get("URL", "http://localhost:8501")

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if ENV == "LOCAL":
    import app_secrets.gcp_service_accounts

if DEBUG := (os.getenv("DEBUG", "false").lower() == "true"):
    logger.warning("Application in debug mode, disable for production")
    fh = logging.FileHandler("logs/debug.log")
    fh.setLevel(logging.INFO)
    fh.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
    )
    logger.addHandler(fh)

if DISPLAY_USER_UPDATES := (
    os.getenv("DISPLAY_USER_UPDATES", "false").lower() == "true"
):
    logger.info("User updates will be displayed")

script_runner = sys.modules["streamlit.runtime.scriptrunner.script_runner"]
handle_uncaught_app_exception = script_runner.handle_uncaught_app_exception


def exception_handler(e):
    # Custom error handling
    if os.getenv("DEBUG", "true").lower() == "true":
        handle_uncaught_app_exception(e)
    else:
        set_tag("environment", ENV)
        set_tag("project", PROJECT)
        capture_exception(e)


script_runner.handle_uncaught_app_exception = exception_handler

if ENV != "LOCAL":
    sentry_sdk.init(
        dsn="https://76086ca93fddeba3df0b1a5512d41ae7@o4505696591544320.ingest.sentry.io/4505696597114880",
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
        # To set a uniform sample rate
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production
        profiles_sample_rate=1.0,
    )

# Display app name
PAGE_NAME = "ChartGPT"
st.set_page_config(page_title=PAGE_NAME, page_icon="📈")

# Initialise Google Cloud Firestore
if not firebase_admin._apps:
    try:
        if ENV == "LOCAL":
            cred = firebase_admin.credentials.Certificate(
                json.loads(os.environ["GCP_SERVICE_ACCOUNT"])
            )
            _ = firebase_admin.initialize_app(cred)
        else:
            _ = firebase_admin.initialize_app()
    except ValueError as e:
        _ = firebase_admin.get_app(name="[DEFAULT]")

db = firestore.client()
db_charts = db.collection("charts")
db_users = db.collection("users")
db_queries = db.collection("queries")

st.markdown(
    """
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-5LQTQQQK06"></script>
<script crossorigin='anonymous'>
    parent.window.dataLayer = parent.window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());

    gtag('config', 'G-5LQTQQQK06');
</script>
""",
    unsafe_allow_html=True,
)

scopes = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/bigquery",
]

if ENV == "LOCAL":
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(os.environ["GCP_SERVICE_ACCOUNT"], strict=False)
    ).with_scopes(scopes)
    bigquery_client = bigquery.Client(credentials=credentials)
else:
    # If deployed using App Engine, use default App Engine credentials
    bigquery_client = bigquery.Client()

datasets = import_module(f'app.config.{os.environ["PROJECT"].lower()}').datasets
