# chartgpt_client.DefaultApi

All URIs are relative to *https://api.chartgpt.***REMOVED****

Method | HTTP request | Description
------------- | ------------- | -------------
[**api_request_ask_chartgpt**](DefaultApi.md#api_request_ask_chartgpt) | **POST** /v1/ask_chartgpt | Ask ChartGPT a question


# **api_request_ask_chartgpt**
> Response api_request_ask_chartgpt(api_request_ask_chartgpt_request)

Ask ChartGPT a question

This endpoint takes a question and returns a response.

### Example

* Api Key Authentication (ApiKeyAuth):
```python
import time
import os
import chartgpt_client
from chartgpt_client.models.api_request_ask_chartgpt_request import ApiRequestAskChartgptRequest
from chartgpt_client.models.response import Response
from chartgpt_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.chartgpt.***REMOVED***
# See configuration.py for a list of all supported configuration parameters.
configuration = chartgpt_client.Configuration(
    host = "https://api.chartgpt.***REMOVED***"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: ApiKeyAuth
configuration.api_key['ApiKeyAuth'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['ApiKeyAuth'] = 'Bearer'

# Enter a context with an instance of the API client
with chartgpt_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chartgpt_client.DefaultApi(api_client)
    api_request_ask_chartgpt_request = chartgpt_client.ApiRequestAskChartgptRequest() # ApiRequestAskChartgptRequest | 

    try:
        # Ask ChartGPT a question
        api_response = api_instance.api_request_ask_chartgpt(api_request_ask_chartgpt_request)
        print("The response of DefaultApi->api_request_ask_chartgpt:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->api_request_ask_chartgpt: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_request_ask_chartgpt_request** | [**ApiRequestAskChartgptRequest**](ApiRequestAskChartgptRequest.md)|  | 

### Return type

[**Response**](Response.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |
**400** | Bad request |  -  |
**401** | API key is missing or invalid |  * WWW_Authenticate -  <br>  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

