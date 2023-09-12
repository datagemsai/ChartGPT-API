import json
import os

import firebase_admin
from firebase_admin import firestore

from api import config

# Initialise Google Cloud Firestore
if not firebase_admin._apps:
    try:
        if config.ENV == "LOCAL":
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
db_api_keys = db.collection("api_keys")
