# coding: utf-8

"""
    ChartGPT API

    The ChartGPT API is a REST API that generates charts and SQL queries based on natural language questions.

    The version of the OpenAPI document: 0.1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json


from typing import Optional
from pydantic import BaseModel, Field, StrictBool, StrictInt, StrictStr
from chartgpt_client.models.output_type import OutputType

class ApiRequestAskChartgptRequest(BaseModel):
    """
    ApiRequestAskChartgptRequest
    """
    prompt: Optional[StrictStr] = Field(None, description="The prompt based on which the response will be generated.")
    dataset_id: Optional[StrictStr] = Field('', description="The dataset ID based on which the response will be generated.")
    output_type: Optional[OutputType] = None
    max_outputs: Optional[StrictInt] = Field(10, description="The maximum number of outputs to generate.")
    max_attempts: Optional[StrictInt] = Field(10, description="The maximum number of attempts to generate an output.")
    max_tokens: Optional[StrictInt] = Field(10, description="The maximum number of tokens to use for generating an output.")
    stream: Optional[StrictBool] = Field(False, description="Whether to stream the response.")
    __properties = ["prompt", "dataset_id", "output_type", "max_outputs", "max_attempts", "max_tokens", "stream"]

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
    def from_json(cls, json_str: str) -> ApiRequestAskChartgptRequest:
        """Create an instance of ApiRequestAskChartgptRequest from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> ApiRequestAskChartgptRequest:
        """Create an instance of ApiRequestAskChartgptRequest from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return ApiRequestAskChartgptRequest.parse_obj(obj)

        _obj = ApiRequestAskChartgptRequest.parse_obj({
            "prompt": obj.get("prompt"),
            "dataset_id": obj.get("dataset_id") if obj.get("dataset_id") is not None else '',
            "output_type": obj.get("output_type"),
            "max_outputs": obj.get("max_outputs") if obj.get("max_outputs") is not None else 10,
            "max_attempts": obj.get("max_attempts") if obj.get("max_attempts") is not None else 10,
            "max_tokens": obj.get("max_tokens") if obj.get("max_tokens") is not None else 10,
            "stream": obj.get("stream") if obj.get("stream") is not None else False
        })
        return _obj


