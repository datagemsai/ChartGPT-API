from connexion.exceptions import OAuthProblem
import secrets
from typing import List
from google.cloud.firestore import ArrayRemove, ArrayUnion
from app import db_users


def apikey_auth(token, required_scopes):
    """Secure an endpoint with an API key"""
    valid = check_api_key(token)

    if not valid:
        raise OAuthProblem("Invalid token")

    return {"uid": "anonymous"}


def create_api_key(user_id) -> None:
    """Create an API key for a user's account"""
    user_ref = db_users.document(user_id)
    api_key = secrets.token_hex(16)
    user_ref.update({"api_keys": ArrayUnion([api_key])})


def delete_api_key(user_id, api_key) -> None:
    """Delete an API key from a user's account"""
    user_ref = db_users.document(user_id)
    user_ref.update({"api_keys": ArrayRemove([api_key])})


def get_api_keys(user_id) -> List[str]:
    """Get all API keys for a user's account"""
    user_ref = db_users.document(user_id)
    user = user_ref.get()
    return user.to_dict().get("api_keys", [])


def check_api_key(api_key) -> bool:
    """Check if an API key is valid"""
    valid = db_users.where("api_keys", "array_contains", api_key)
    return bool(valid)
