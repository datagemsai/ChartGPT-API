# chartgpt_client.ChatApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ask_chartgpt_stream_v1_ask_chartgpt_stream_post**](ChatApi.md#ask_chartgpt_stream_v1_ask_chartgpt_stream_post) | **POST** /v1/ask_chartgpt/stream | Ask Chartgpt Stream
[**ask_chartgpt_v1_ask_chartgpt_post**](ChatApi.md#ask_chartgpt_v1_ask_chartgpt_post) | **POST** /v1/ask_chartgpt | Ask Chartgpt


# **ask_chartgpt_stream_v1_ask_chartgpt_stream_post**
> Response ask_chartgpt_stream_v1_ask_chartgpt_stream_post(request)

Ask Chartgpt Stream

Stream the response from the ChartGPT API.

### Example

* Api Key Authentication (APIKeyHeader):
```python
import time
import os
import chartgpt_client
from chartgpt_client.models.request import Request
from chartgpt_client.models.response import Response
from chartgpt_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chartgpt_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: APIKeyHeader
configuration.api_key['APIKeyHeader'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['APIKeyHeader'] = 'Bearer'

# Enter a context with an instance of the API client
with chartgpt_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chartgpt_client.ChatApi(api_client)
    request = chartgpt_client.Request() # Request | 

    try:
        # Ask Chartgpt Stream
        api_response = api_instance.ask_chartgpt_stream_v1_ask_chartgpt_stream_post(request)
        print("The response of ChatApi->ask_chartgpt_stream_v1_ask_chartgpt_stream_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChatApi->ask_chartgpt_stream_v1_ask_chartgpt_stream_post: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request** | [**Request**](Request.md)|  | 

### Return type

[**Response**](Response.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **ask_chartgpt_v1_ask_chartgpt_post**
> Response ask_chartgpt_v1_ask_chartgpt_post(request, stream=stream)

Ask Chartgpt

Answer a user query using the ChartGPT API.

### Example

* Api Key Authentication (APIKeyHeader):
```python
import time
import os
import chartgpt_client
from chartgpt_client.models.request import Request
from chartgpt_client.models.response import Response
from chartgpt_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chartgpt_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: APIKeyHeader
configuration.api_key['APIKeyHeader'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['APIKeyHeader'] = 'Bearer'

# Enter a context with an instance of the API client
with chartgpt_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chartgpt_client.ChatApi(api_client)
    request = chartgpt_client.Request() # Request | 
    stream = None # object |  (optional)

    try:
        # Ask Chartgpt
        api_response = api_instance.ask_chartgpt_v1_ask_chartgpt_post(request, stream=stream)
        print("The response of ChatApi->ask_chartgpt_v1_ask_chartgpt_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChatApi->ask_chartgpt_v1_ask_chartgpt_post: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request** | [**Request**](Request.md)|  | 
 **stream** | [**object**](.md)|  | [optional] 

### Return type

[**Response**](Response.md)

### Authorization

[APIKeyHeader](../README.md#APIKeyHeader)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

