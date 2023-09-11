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
from chartgpt_client.models.error import Error  # noqa: E501
from chartgpt_client.rest import ApiException


class TestError(unittest.TestCase):
    """Error unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test Error
        include_option is a boolean, when False only required
        params are included, when True both required and
        optional params are included"""
        # uncomment below to create an instance of `Error`
        """
        model = chartgpt_client.models.error.Error()  # noqa: E501
        if include_optional :
            return Error(
                index = 56, 
                created_at = 56, 
                type = '', 
                value = ''
            )
        else :
            return Error(
        )
        """

    def testError(self):
        """Test Error"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)


if __name__ == "__main__":
    unittest.main()
