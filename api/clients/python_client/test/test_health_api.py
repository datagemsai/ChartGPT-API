# coding: utf-8

"""
    FastAPI

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

    The version of the OpenAPI document: 0.1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

import chartgpt_client
from chartgpt_client.api.health_api import HealthApi  # noqa: E501
from chartgpt_client.rest import ApiException


class TestHealthApi(unittest.TestCase):
    """HealthApi unit test stubs"""

    def setUp(self):
        self.api = chartgpt_client.api.health_api.HealthApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_alth_get(self):
        """Test case for alth_get

        Ping  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
