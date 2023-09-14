# ApiRequestAskChartgptRequestMessagesInner

The message based on which the response will be generated.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the message. | [optional] 
**created_at** | **int** | The timestamp of when the message was created. | [optional] 
**content** | **str** | The content of the message. | [optional] 
**role** | [**Role**](Role.md) |  | [optional] 

## Example

```python
from chartgpt_client.models.api_request_ask_chartgpt_request_messages_inner import ApiRequestAskChartgptRequestMessagesInner

# TODO update the JSON string below
json = "{}"
# create an instance of ApiRequestAskChartgptRequestMessagesInner from a JSON string
api_request_ask_chartgpt_request_messages_inner_instance = ApiRequestAskChartgptRequestMessagesInner.from_json(json)
# print the JSON string representation of the object
print ApiRequestAskChartgptRequestMessagesInner.to_json()

# convert the object into a dict
api_request_ask_chartgpt_request_messages_inner_dict = api_request_ask_chartgpt_request_messages_inner_instance.to_dict()
# create an instance of ApiRequestAskChartgptRequestMessagesInner from a dict
api_request_ask_chartgpt_request_messages_inner_form_dict = api_request_ask_chartgpt_request_messages_inner.from_dict(api_request_ask_chartgpt_request_messages_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


