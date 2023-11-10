from __future__ import annotations
import pprint
import re  # noqa: F401
import json


from typing import Optional
from pydantic import BaseModel, Field, StrictInt, StrictStr


class Output(BaseModel):
    """
    Output
    """
    index: Optional[StrictInt] = Field(None, description="The index of the output.")
    created_at: Optional[StrictInt] = Field(None, description="The timestamp of when the output was created.")
    description: Optional[StrictStr] = Field(None, description="The description of the output.")
    type: Optional[StrictStr] = Field(None, description="The type of the output.")
    value: Optional[StrictStr] = Field(None, description="The value of the output.")
    __properties = ["index", "created_at", "description", "type", "value"]

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
    def from_json(cls, json_str: str) -> Output:
        """Create an instance of Output from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> Output:
        """Create an instance of Output from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return Output.parse_obj(obj)

        _obj = Output.parse_obj({
            "index": obj.get("index"),
            "created_at": obj.get("created_at"),
            "description": obj.get("description"),
            "type": obj.get("type"),
            "value": obj.get("value")
        })
        return _obj
