# .ChatApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**askChartgptStreamV1AskChartgptStreamPost**](ChatApi.md#askChartgptStreamV1AskChartgptStreamPost) | **POST** /v1/ask_chartgpt/stream | Ask Chartgpt Stream
[**askChartgptV1AskChartgptPost**](ChatApi.md#askChartgptV1AskChartgptPost) | **POST** /v1/ask_chartgpt | Ask Chartgpt


# **askChartgptStreamV1AskChartgptStreamPost**
> Response askChartgptStreamV1AskChartgptStreamPost(request)

Stream the response from the ChartGPT API.

### Example


```typescript
import {  } from '';
import * as fs from 'fs';

const configuration = .createConfiguration();
const apiInstance = new .ChatApi(configuration);

let body:.ChatApiAskChartgptStreamV1AskChartgptStreamPostRequest = {
  // Request
  request: {
    dataSourceUrl: "",
    maxAttempts: 10,
    maxOutputs: 10,
    maxTokens: 10,
    messages: [
      {
        content: "content_example",
        createdAt: 1,
        id: "id_example",
        role: "system",
      },
    ],
    outputType: "any",
    sessionId: "sessionId_example",
  },
};

apiInstance.askChartgptStreamV1AskChartgptStreamPost(body).then((data:any) => {
  console.log('API called successfully. Returned data: ' + data);
}).catch((error:any) => console.error(error));
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request** | **Request**|  |


### Return type

**Response**

### Authorization

[APIKeyHeader](README.md#APIKeyHeader)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](README.md#documentation-for-api-endpoints) [[Back to Model list]](README.md#documentation-for-models) [[Back to README]](README.md)

# **askChartgptV1AskChartgptPost**
> Response askChartgptV1AskChartgptPost(request)

Answer a user query using the ChartGPT API.

### Example


```typescript
import {  } from '';
import * as fs from 'fs';

const configuration = .createConfiguration();
const apiInstance = new .ChatApi(configuration);

let body:.ChatApiAskChartgptV1AskChartgptPostRequest = {
  // Request
  request: {
    dataSourceUrl: "",
    maxAttempts: 10,
    maxOutputs: 10,
    maxTokens: 10,
    messages: [
      {
        content: "content_example",
        createdAt: 1,
        id: "id_example",
        role: "system",
      },
    ],
    outputType: "any",
    sessionId: "sessionId_example",
  },
  // any (optional)
  stream: null,
};

apiInstance.askChartgptV1AskChartgptPost(body).then((data:any) => {
  console.log('API called successfully. Returned data: ' + data);
}).catch((error:any) => console.error(error));
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request** | **Request**|  |
 **stream** | **any** |  | (optional) defaults to undefined


### Return type

**Response**

### Authorization

[APIKeyHeader](README.md#APIKeyHeader)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](README.md#documentation-for-api-endpoints) [[Back to Model list]](README.md#documentation-for-models) [[Back to README]](README.md)


