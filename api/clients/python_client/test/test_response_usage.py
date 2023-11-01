# coding: utf-8

"""
    FastAPI

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

    The version of the OpenAPI document: 0.1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest
import datetime

import chartgpt_client
from chartgpt_client.models.response_usage import ResponseUsage  # noqa: E501
from chartgpt_client.rest import ApiException

class TestResponseUsage(unittest.TestCase):
    """ResponseUsage unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test ResponseUsage
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `ResponseUsage`
        """
        model = chartgpt_client.models.response_usage.ResponseUsage()  # noqa: E501
        if include_optional :
            return ResponseUsage(
                tokens = None
            )
        else :
            return ResponseUsage(
        )
        """

    def testResponseUsage(self):
        """Test ResponseUsage"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
