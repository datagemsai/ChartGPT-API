from __future__ import annotations
import pprint
import re  # noqa: F401
import json


from typing import List, Optional
from pydantic import BaseModel, Field, StrictInt, StrictStr, conlist, constr, validator
from api.models.output_type import OutputType
from api.models.message import Message


class Request(BaseModel):
    """
    Request
    """
    job_id: Optional[StrictStr] = Field(None, description="The job ID of the request.")
    messages: Optional[conlist(Message)] = Field(None, description="The messages based on which the response will be generated.")
    data_source_url: Optional[constr(strict=True)] = Field('', description="The data source URL based on which the response will be generated. The entity is optional. If not specified, the default data source will be used.")
    output_type: Optional[OutputType] = None
    max_outputs: Optional[StrictInt] = Field(10, description="The maximum number of outputs to generate.")
    max_attempts: Optional[StrictInt] = Field(10, description="The maximum number of attempts to generate an output.")
    max_tokens: Optional[StrictInt] = Field(10, description="The maximum number of tokens to use for generating an output.")
    __properties = ["job_id", "messages", "data_source_url", "output_type", "max_outputs", "max_attempts", "max_tokens"]

    @validator('data_source_url')
    def data_source_url_validate_regular_expression(cls, value):
        """Validates the regular expression"""
        if value is None:
            return value

        if not re.match(r"^(?:([a-z]+)\/([a-zA-Z0-9_-]+)\/([a-zA-Z0-9_-]+)(?:\/([a-zA-Z0-9_-]+))?)?$", value):
            raise ValueError(r"must validate the regular expression /^(?:([a-z]+)\/([a-zA-Z0-9_-]+)\/([a-zA-Z0-9_-]+)(?:\/([a-zA-Z0-9_-]+))?)?$/")
        return value

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
    def from_json(cls, json_str: str) -> Request:
        """Create an instance of Request from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of each item in messages (list)
        _items = []
        if self.messages:
            for _item in self.messages:
                if _item:
                    _items.append(_item.to_dict())
            _dict['messages'] = _items
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> Request:
        """Create an instance of Request from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return Request.parse_obj(obj)

        _obj = Request.parse_obj({
            "job_id": obj.get("job_id"),
            "messages": [Message.from_dict(_item) for _item in obj.get("messages")] if obj.get("messages") is not None else None,
            "data_source_url": obj.get("data_source_url") if obj.get("data_source_url") is not None else '',
            "output_type": obj.get("output_type"),
            "max_outputs": obj.get("max_outputs") if obj.get("max_outputs") is not None else 10,
            "max_attempts": obj.get("max_attempts") if obj.get("max_attempts") is not None else 10,
            "max_tokens": obj.get("max_tokens") if obj.get("max_tokens") is not None else 10
        })
        return _obj
