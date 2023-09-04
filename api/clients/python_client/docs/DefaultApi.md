# openapi_client.DefaultApi

All URIs are relative to *https://api.chartgpt.***REMOVED****

Method | HTTP request | Description
------------- | ------------- | -------------
[**api_chart_generate_chart**](DefaultApi.md#api_chart_generate_chart) | **POST** /chart | Generate a Plotly chart from a question
[**api_sql_generate_sql**](DefaultApi.md#api_sql_generate_sql) | **POST** /sql | Generate an SQL query from a question


# **api_chart_generate_chart**
> ApiChartGenerateChart200Response api_chart_generate_chart(api_chart_generate_chart_request)

Generate a Plotly chart from a question

This endpoint takes a question and returns a Plotly figure in either JSON or PNG format, depending on the `type` parameter.

### Example

* Api Key Authentication (ApiKeyAuth):
```python
import time
import os
import openapi_client
from openapi_client.models.api_chart_generate_chart200_response import ApiChartGenerateChart200Response
from openapi_client.models.api_chart_generate_chart_request import ApiChartGenerateChartRequest
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.chartgpt.***REMOVED***
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
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
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    api_chart_generate_chart_request = openapi_client.ApiChartGenerateChartRequest() # ApiChartGenerateChartRequest | 

    try:
        # Generate a Plotly chart from a question
        api_response = api_instance.api_chart_generate_chart(api_chart_generate_chart_request)
        print("The response of DefaultApi->api_chart_generate_chart:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->api_chart_generate_chart: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_chart_generate_chart_request** | [**ApiChartGenerateChartRequest**](ApiChartGenerateChartRequest.md)|  | 

### Return type

[**ApiChartGenerateChart200Response**](ApiChartGenerateChart200Response.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, image/png

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |
**400** | Bad request |  -  |
**401** | API key is missing or invalid |  * WWW_Authenticate -  <br>  |
**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **api_sql_generate_sql**
> ApiSqlGenerateSql200Response api_sql_generate_sql(api_sql_generate_sql_request)

Generate an SQL query from a question

This endpoint takes a question and returns an SQL query.

### Example

* Api Key Authentication (ApiKeyAuth):
```python
import time
import os
import openapi_client
from openapi_client.models.api_sql_generate_sql200_response import ApiSqlGenerateSql200Response
from openapi_client.models.api_sql_generate_sql_request import ApiSqlGenerateSqlRequest
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.chartgpt.***REMOVED***
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
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
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    api_sql_generate_sql_request = openapi_client.ApiSqlGenerateSqlRequest() # ApiSqlGenerateSqlRequest | 

    try:
        # Generate an SQL query from a question
        api_response = api_instance.api_sql_generate_sql(api_sql_generate_sql_request)
        print("The response of DefaultApi->api_sql_generate_sql:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->api_sql_generate_sql: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **api_sql_generate_sql_request** | [**ApiSqlGenerateSqlRequest**](ApiSqlGenerateSqlRequest.md)|  | 

### Return type

[**ApiSqlGenerateSql200Response**](ApiSqlGenerateSql200Response.md)

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

