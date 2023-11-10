# coding: utf-8

"""
    ChartGPT API

    The ChartGPT API is a REST API that generates insights from data based on natural language questions.

    The version of the OpenAPI document: 0.1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest
import datetime

import chartgpt_client
from chartgpt_client.models.request import Request  # noqa: E501
from chartgpt_client.rest import ApiException

class TestRequest(unittest.TestCase):
    """Request unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test Request
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `Request`
        """
        model = chartgpt_client.models.request.Request()  # noqa: E501
        if include_optional :
            return Request(
                data_source_url = None, 
                max_attempts = None, 
                max_outputs = None, 
                max_tokens = None, 
                messages = None, 
                output_type = any, 
                session_id = None
            )
        else :
            return Request(
        )
        """

    def testRequest(self):
        """Test Request"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
