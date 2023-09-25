# coding: utf-8

"""
    ChartGPT API

    The ChartGPT API is a REST API that generates insights from data based on natural language questions.

    The version of the OpenAPI document: 0.1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations

import json
import pprint
import re  # noqa: F401
from typing import List, Optional

from chartgpt_client.models.attempt import Attempt
from chartgpt_client.models.error import Error
from chartgpt_client.models.output import Output
from chartgpt_client.models.output_type import OutputType
from chartgpt_client.models.response_messages_inner import \
    ResponseMessagesInner
from chartgpt_client.models.response_usage import ResponseUsage
from chartgpt_client.models.status import Status
from pydantic import BaseModel, Field, StrictInt, StrictStr, conlist


class Response(BaseModel):
    """
    Response
    """

    id: Optional[StrictStr] = Field(None, description="The ID of the request.")
    created_at: Optional[StrictInt] = Field(
        None, description="The timestamp of when the request was created."
    )
    finished_at: Optional[StrictInt] = Field(
        None, description="The timestamp of when the request was finished."
    )
    status: Optional[Status] = None
    messages: Optional[conlist(ResponseMessagesInner)] = Field(
        None, description="The messages of the request."
    )
    dataset_id: Optional[StrictStr] = Field(
        None, description="The dataset ID of the request."
    )
    attempts: Optional[conlist(Attempt)] = Field(
        None, description="The attempts of the request."
    )
    output_type: Optional[OutputType] = None
    outputs: Optional[conlist(Output)] = Field(
        None, description="The outputs of the request."
    )
    errors: Optional[conlist(Error)] = Field(
        None, description="The errors of the request."
    )
    usage: Optional[ResponseUsage] = None
    __properties = [
        "id",
        "created_at",
        "finished_at",
        "status",
        "messages",
        "dataset_id",
        "attempts",
        "output_type",
        "outputs",
        "errors",
        "usage",
    ]

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
    def from_json(cls, json_str: str) -> Response:
        """Create an instance of Response from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True, exclude={}, exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of each item in messages (list)
        _items = []
        if self.messages:
            for _item in self.messages:
                if _item:
                    _items.append(_item.to_dict())
            _dict["messages"] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in attempts (list)
        _items = []
        if self.attempts:
            for _item in self.attempts:
                if _item:
                    _items.append(_item.to_dict())
            _dict["attempts"] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in outputs (list)
        _items = []
        if self.outputs:
            for _item in self.outputs:
                if _item:
                    _items.append(_item.to_dict())
            _dict["outputs"] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in errors (list)
        _items = []
        if self.errors:
            for _item in self.errors:
                if _item:
                    _items.append(_item.to_dict())
            _dict["errors"] = _items
        # override the default output from pydantic by calling `to_dict()` of usage
        if self.usage:
            _dict["usage"] = self.usage.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> Response:
        """Create an instance of Response from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return Response.parse_obj(obj)

        _obj = Response.parse_obj(
            {
                "id": obj.get("id"),
                "created_at": obj.get("created_at"),
                "finished_at": obj.get("finished_at"),
                "status": obj.get("status"),
                "messages": [
                    ResponseMessagesInner.from_dict(_item)
                    for _item in obj.get("messages")
                ]
                if obj.get("messages") is not None
                else None,
                "dataset_id": obj.get("dataset_id"),
                "attempts": [Attempt.from_dict(_item) for _item in obj.get("attempts")]
                if obj.get("attempts") is not None
                else None,
                "output_type": obj.get("output_type"),
                "outputs": [Output.from_dict(_item) for _item in obj.get("outputs")]
                if obj.get("outputs") is not None
                else None,
                "errors": [Error.from_dict(_item) for _item in obj.get("errors")]
                if obj.get("errors") is not None
                else None,
                "usage": ResponseUsage.from_dict(obj.get("usage"))
                if obj.get("usage") is not None
                else None,
            }
        )
        return _obj
