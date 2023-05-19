from dotenv import load_dotenv
from analytics_bot_langchain.app import get_agent


# Load environment variables from .env
load_dotenv()

__all__ = [
    "get_agent",
]
