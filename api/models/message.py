from __future__ import annotations
import pprint
import re  # noqa: F401
import json


from typing import Optional
from pydantic import BaseModel, Field, StrictInt, StrictStr
from api.models.role import Role



class Message(BaseModel):
    """
    The message based on which the response will be generated.
    """
    id: Optional[StrictStr] = Field(None, description="The ID of the message.")
    created_at: Optional[StrictInt] = Field(None, description="The timestamp of when the message was created.")
    content: Optional[StrictStr] = Field(None, description="The content of the message.")
    role: Optional[Role] = None
    __properties = ["id", "created_at", "content", "role"]

    class Config:
        """Pydantic configuration"""
        allow_population_by_field_name = True
        validate_assignment = True

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.dict(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Message:
        """Create an instance of RequestMessagesInner from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> Message:
        """Create an instance of RequestMessagesInner from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return Message.parse_obj(obj)

        _obj = Message.parse_obj({
            "id": obj.get("id"),
            "created_at": obj.get("created_at"),
            "content": obj.get("content"),
            "role": obj.get("role")
        })
        return _obj
