# coding: utf-8

"""
    ChartGPT API

    The ChartGPT API is a REST API that generates insights from data based on natural language questions.

    The version of the OpenAPI document: 0.1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json


from typing import Any, Optional
from pydantic import BaseModel, Field
from chartgpt_client.models.output_type import OutputType
from chartgpt_client.models.response_usage import ResponseUsage
from chartgpt_client.models.status import Status

class Response(BaseModel):
    """
    Response
    """
    attempts: Optional[Any] = Field(None, description="The attempts of the request.")
    created_at: Optional[Any] = Field(None, description="The timestamp of when the request was created.")
    data_source_url: Optional[Any] = Field(None, description="The data source URL of the request.")
    errors: Optional[Any] = Field(None, description="The errors of the request.")
    finished_at: Optional[Any] = Field(None, description="The timestamp of when the request was finished.")
    session_id: Optional[Any] = Field(None, description="The job ID of the response.")
    messages: Optional[Any] = Field(None, description="The messages of the request.")
    output_type: Optional[OutputType] = None
    outputs: Optional[Any] = Field(None, description="The outputs of the request.")
    status: Optional[Status] = None
    usage: Optional[ResponseUsage] = None
    __properties = ["attempts", "created_at", "data_source_url", "errors", "finished_at", "session_id", "messages", "output_type", "outputs", "status", "usage"]

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
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of usage
        if self.usage:
            _dict['usage'] = self.usage.to_dict()
        # set to None if attempts (nullable) is None
        # and __fields_set__ contains the field
        if self.attempts is None and "attempts" in self.__fields_set__:
            _dict['attempts'] = None

        # set to None if created_at (nullable) is None
        # and __fields_set__ contains the field
        if self.created_at is None and "created_at" in self.__fields_set__:
            _dict['created_at'] = None

        # set to None if data_source_url (nullable) is None
        # and __fields_set__ contains the field
        if self.data_source_url is None and "data_source_url" in self.__fields_set__:
            _dict['data_source_url'] = None

        # set to None if errors (nullable) is None
        # and __fields_set__ contains the field
        if self.errors is None and "errors" in self.__fields_set__:
            _dict['errors'] = None

        # set to None if finished_at (nullable) is None
        # and __fields_set__ contains the field
        if self.finished_at is None and "finished_at" in self.__fields_set__:
            _dict['finished_at'] = None

        # set to None if session_id (nullable) is None
        # and __fields_set__ contains the field
        if self.session_id is None and "session_id" in self.__fields_set__:
            _dict['session_id'] = None

        # set to None if messages (nullable) is None
        # and __fields_set__ contains the field
        if self.messages is None and "messages" in self.__fields_set__:
            _dict['messages'] = None

        # set to None if outputs (nullable) is None
        # and __fields_set__ contains the field
        if self.outputs is None and "outputs" in self.__fields_set__:
            _dict['outputs'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> Response:
        """Create an instance of Response from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return Response.parse_obj(obj)

        _obj = Response.parse_obj({
            "attempts": obj.get("attempts"),
            "created_at": obj.get("created_at"),
            "data_source_url": obj.get("data_source_url"),
            "errors": obj.get("errors"),
            "finished_at": obj.get("finished_at"),
            "session_id": obj.get("session_id"),
            "messages": obj.get("messages"),
            "output_type": obj.get("output_type"),
            "outputs": obj.get("outputs"),
            "status": obj.get("status"),
            "usage": ResponseUsage.from_dict(obj.get("usage")) if obj.get("usage") is not None else None
        })
        return _obj


