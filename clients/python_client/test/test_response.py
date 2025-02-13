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
from chartgpt_client.models.response import Response  # noqa: E501
from chartgpt_client.rest import ApiException

class TestResponse(unittest.TestCase):
    """Response unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional):
        """Test Response
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `Response`
        """
        model = chartgpt_client.models.response.Response()  # noqa: E501
        if include_optional :
            return Response(
                attempts = [
                    chartgpt_client.models.attempt.Attempt(
                        created_at = 56, 
                        errors = [
                            chartgpt_client.models.error.Error(
                                created_at = 56, 
                                index = 56, 
                                type = '', 
                                value = '', )
                            ], 
                        index = 56, 
                        outputs = [
                            chartgpt_client.models.output.Output(
                                created_at = 56, 
                                description = '', 
                                index = 56, 
                                type = '', 
                                value = '', )
                            ], )
                    ], 
                created_at = 56, 
                data_source_url = '', 
                errors = [
                    chartgpt_client.models.error.Error(
                        created_at = 56, 
                        index = 56, 
                        type = '', 
                        value = '', )
                    ], 
                finished_at = 56, 
                messages = [
                    chartgpt_client.models.message.Message(
                        content = '', 
                        created_at = 56, 
                        id = '', 
                        role = 'system', )
                    ], 
                output_type = 'any', 
                outputs = [
                    chartgpt_client.models.output.Output(
                        created_at = 56, 
                        description = '', 
                        index = 56, 
                        type = '', 
                        value = '', )
                    ], 
                session_id = '', 
                status = 'succeeded', 
                usage = chartgpt_client.models.response_usage.ResponseUsage(
                    tokens = 56, )
            )
        else :
            return Response(
        )
        """

    def testResponse(self):
        """Test Response"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
