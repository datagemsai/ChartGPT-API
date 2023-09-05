# Output


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**index** | **int** | The index of the output. | [optional] 
**created_at** | **int** | The timestamp of when the output was created. | [optional] 
**description** | **str** | The description of the output. | [optional] 
**type** | **str** | The type of the output. | [optional] 
**value** | **str** | The value of the output. | [optional] 

## Example

```python
from chartgpt_client.models.output import Output

# TODO update the JSON string below
json = "{}"
# create an instance of Output from a JSON string
output_instance = Output.from_json(json)
# print the JSON string representation of the object
print Output.to_json()

# convert the object into a dict
output_dict = output_instance.to_dict()
# create an instance of Output from a dict
output_form_dict = output.from_dict(output_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


