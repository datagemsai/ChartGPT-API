import time

from chartgpt_client import ApiRequestAskChartgptRequest as Request
from chartgpt_client import Response, Usage

from api.chartgpt import answer_user_query
from api.errors import ContextLengthError
from api.guards import is_nda_broken
from api.types import QueryResult
from api.utils import generate_uuid, parse_data_source_url


def ask_chartgpt(body) -> Response:
    request: Request = Request.from_dict(body)
    if is_nda_broken(request.prompt):
        return {"error": "Could not complete analysis: insecure request"}, 400

    data_source, _, _, _ = parse_data_source_url(request.data_source_url)

    if not request.prompt:
        return {"error": "Could not complete analysis: prompt is empty"}, 400

    if data_source != "bigquery":
        return {"error": "Could not complete analysis: data source not supported"}, 400

    try:
        job_uuid = f"ask-{generate_uuid()}"
        created_at = int(time.time())
        result: QueryResult = answer_user_query(request=request)
        finished_at = int(time.time())
        return (
            Response(
                id=job_uuid,
                created_at=created_at,
                finished_at=finished_at,
                status="succeeded",
                prompt=request.prompt,
                data_source_url=request.data_source_url,
                attempts=result.attempts,
                output_type=request.output_type,
                outputs=result.outputs,
                errors=result.errors,
                usage=Usage(tokens=len(result.attempts)),
            ).to_dict(),
            200,
        )
    except ContextLengthError:
        return {"error": "Could not complete analysis: ran out of context"}, 400
    except Exception as ex:
        return {"error": f"Could not complete analysis: {ex}"}, 400
