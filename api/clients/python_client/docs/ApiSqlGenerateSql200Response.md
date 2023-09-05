# ApiSqlGenerateSql200Response


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**query** | **str** | The generated SQL query. | [optional] 

## Example

```python
from chartgpt_client.models.api_sql_generate_sql200_response import ApiSqlGenerateSql200Response

# TODO update the JSON string below
json = "{}"
# create an instance of ApiSqlGenerateSql200Response from a JSON string
api_sql_generate_sql200_response_instance = ApiSqlGenerateSql200Response.from_json(json)
# print the JSON string representation of the object
print ApiSqlGenerateSql200Response.to_json()

# convert the object into a dict
api_sql_generate_sql200_response_dict = api_sql_generate_sql200_response_instance.to_dict()
# create an instance of ApiSqlGenerateSql200Response from a dict
api_sql_generate_sql200_response_form_dict = api_sql_generate_sql200_response.from_dict(api_sql_generate_sql200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


