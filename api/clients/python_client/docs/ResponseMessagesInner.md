# ResponseMessagesInner

The message of the request.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the message. | [optional] 
**created_at** | **int** | The timestamp of when the message was created. | [optional] 
**content** | **str** | The content of the message. | [optional] 
**role** | [**Role**](Role.md) |  | [optional] 

## Example

```python
from chartgpt_client.models.response_messages_inner import ResponseMessagesInner

# TODO update the JSON string below
json = "{}"
# create an instance of ResponseMessagesInner from a JSON string
response_messages_inner_instance = ResponseMessagesInner.from_json(json)
# print the JSON string representation of the object
print ResponseMessagesInner.to_json()

# convert the object into a dict
response_messages_inner_dict = response_messages_inner_instance.to_dict()
# create an instance of ResponseMessagesInner from a dict
response_messages_inner_form_dict = response_messages_inner.from_dict(response_messages_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


