import secrets
from typing import List

from connexion.exceptions import AuthenticationProblem

from api.connectors.firestore import db_api_keys, db_users


def apikey_auth(token, required_scopes):
    """Secure an endpoint with an API key"""
    valid = check_api_key(token)

    if not valid:
        raise AuthenticationProblem("Invalid token")

    return {"uid": "anonymous"}


def create_api_key(user_id) -> bool:
    """Create an API key for a user's account"""
    if db_users.document(user_id).get():
        api_key = secrets.token_hex(16)
        db_api_keys.document(api_key).set(
            {
                "user_id": user_id,
                "creation_date": db.SERVER_TIMESTAMP,
                "expiration_date": db.SERVER_TIMESTAMP + db.timedelta(days=365),
                "status": "ACTIVE",
            }
        )
        return True
    else:
        return False


def delete_api_key(user_id, api_key) -> bool:
    """Delete an API key from a user's account"""
    if db_users.document(user_id).get():
        db_api_keys.document(api_key).set(
            {
                "status": "INACTIVE",
            }
        )
        return True
    else:
        return False


def get_api_keys(user_id) -> List[str]:
    """Get all API keys for a user's account"""
    if db_users.document(user_id).get():
        api_keys = (
            db_api_keys.where("user_id", "==", user_id)
            .where("status", "==", "ACTIVE")
            .get()
        )
        return [api_key.id for api_key in api_keys]
    else:
        return []


def check_api_key(api_key) -> bool:
    """Check if an API key is valid"""
    if db_api_keys.document(api_key).get().exists:
        return True
    else:
        return False
