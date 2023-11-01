from __future__ import annotations
import pprint
import re  # noqa: F401
import json


from typing import Optional
from pydantic import BaseModel, Field, StrictInt, StrictStr


class Error(BaseModel):
    """
    Error
    """
    index: Optional[StrictInt] = Field(None, description="The index of the error.")
    created_at: Optional[StrictInt] = Field(None, description="The timestamp of when the error was created.")
    type: Optional[StrictStr] = Field(None, description="The type of the error.")
    value: Optional[StrictStr] = Field(None, description="The value of the error.")
    __properties = ["index", "created_at", "type", "value"]

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
    def from_json(cls, json_str: str) -> Error:
        """Create an instance of Error from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> Error:
        """Create an instance of Error from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return Error.parse_obj(obj)

        _obj = Error.parse_obj({
            "index": obj.get("index"),
            "created_at": obj.get("created_at"),
            "type": obj.get("type"),
            "value": obj.get("value")
        })
        return _obj
