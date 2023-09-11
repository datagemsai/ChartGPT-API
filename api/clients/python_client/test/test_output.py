# coding: utf-8

"""
    ChartGPT API

    The ChartGPT API is a REST API that generates charts and SQL queries based on natural language questions.

    The version of the OpenAPI document: 0.1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import datetime
import unittest

import chartgpt_client
from chartgpt_client.models.output import Output  # noqa: E501
from chartgpt_client.rest import ApiException


class TestOutput(unittest.TestCase):
    """Output unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test Output
        include_option is a boolean, when False only required
        params are included, when True both required and
        optional params are included"""
        # uncomment below to create an instance of `Output`
        """
        model = chartgpt_client.models.output.Output()  # noqa: E501
        if include_optional :
            return Output(
                index = 56, 
                created_at = 56, 
                description = '', 
                type = '', 
                value = ''
            )
        else :
            return Output(
        )
        """

    def testOutput(self):
        """Test Output"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == "__main__":
    unittest.main()
