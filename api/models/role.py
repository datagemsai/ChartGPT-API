import json
import pprint
import re  # noqa: F401
from aenum import Enum, no_arg


class Role(str, Enum):
    """
    The role of the message.
    """

    """
    allowed enum values
    """
    SYSTEM = 'system'
    USER = 'user'
    ASSISTANT = 'assistant'
    FUNCTION = 'function'

    @classmethod
    def from_json(cls, json_str: str) -> Role:
        """Create an instance of Role from a JSON string"""
        return Role(json.loads(json_str))
