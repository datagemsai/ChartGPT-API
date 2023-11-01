from __future__ import annotations
import pprint
import re  # noqa: F401
import json


from typing import List, Optional
from pydantic import BaseModel, Field, StrictInt, conlist
from api.models.error import Error
from api.models.output import Output


class Attempt(BaseModel):
    """
    Attempt
    """
    index: Optional[StrictInt] = Field(None, description="The index of the attempt.")
    created_at: Optional[StrictInt] = Field(None, description="The timestamp of when the attempt was created.")
    outputs: Optional[conlist(Output)] = Field(None, description="The outputs of the attempt.")
    errors: Optional[conlist(Error)] = Field(None, description="The errors of the attempt.")
    __properties = ["index", "created_at", "outputs", "errors"]

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
    def from_json(cls, json_str: str) -> Attempt:
        """Create an instance of Attempt from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of each item in outputs (list)
        _items = []
        if self.outputs:
            for _item in self.outputs:
                if _item:
                    _items.append(_item.to_dict())
            _dict['outputs'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in errors (list)
        _items = []
        if self.errors:
            for _item in self.errors:
                if _item:
                    _items.append(_item.to_dict())
            _dict['errors'] = _items
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> Attempt:
        """Create an instance of Attempt from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return Attempt.parse_obj(obj)

        _obj = Attempt.parse_obj({
            "index": obj.get("index"),
            "created_at": obj.get("created_at"),
            "outputs": [Output.from_dict(_item) for _item in obj.get("outputs")] if obj.get("outputs") is not None else None,
            "errors": [Error.from_dict(_item) for _item in obj.get("errors")] if obj.get("errors") is not None else None
        })
        return _obj
