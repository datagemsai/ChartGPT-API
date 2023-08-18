import typing_extensions

from openapi_client.paths import PathValues
from openapi_client.apis.paths.chart import Chart
from openapi_client.apis.paths.sql import Sql

PathToApi = typing_extensions.TypedDict(
    'PathToApi',
    {
        PathValues.CHART: Chart,
        PathValues.SQL: Sql,
    }
)

path_to_api = PathToApi(
    {
        PathValues.CHART: Chart,
        PathValues.SQL: Sql,
    }
)
