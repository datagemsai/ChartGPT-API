# coding: utf-8

"""
    ChartGPT API

    The ChartGPT API is a REST API that generates insights from data based on natural language questions.

    The version of the OpenAPI document: 0.1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import json
import pprint
import re  # noqa: F401

from aenum import Enum, no_arg


class Status(str, Enum):
    """
    The status of the request.
    """

    """
    allowed enum values
    """
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    STREAM = "stream"

    @classmethod
    def from_json(cls, json_str: str) -> Status:
        """Create an instance of Status from a JSON string"""
        return Status(json.loads(json_str))
