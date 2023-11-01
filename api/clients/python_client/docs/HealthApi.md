# chartgpt_client.HealthApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**alth_get**](HealthApi.md#alth_get) | **GET** /health | Ping


# **alth_get**
> object alth_get()

Ping

Ping the API to check if it is running.

### Example

```python
import time
import os
import chartgpt_client
from chartgpt_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chartgpt_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with chartgpt_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chartgpt_client.HealthApi(api_client)

    try:
        # Ping
        api_response = api_instance.alth_get()
        print("The response of HealthApi->alth_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling HealthApi->alth_get: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

