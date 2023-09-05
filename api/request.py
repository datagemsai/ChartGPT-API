import base64
import uuid
import time
from dataclasses import asdict

from api.chartgpt import answer_user_query
from api.guards import is_nda_broken
# from api.types import OutputType, QueryResult, Request, Response, Usage
from api.types import OutputType, QueryResult
from api.errors import ContextLengthError

from chartgpt_client import ApiRequestAskChartgptRequest as Request
from chartgpt_client import Response, Usage


def generate_uuid() -> str:
    r_uuid = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode("utf-8")
    return r_uuid.replace('=', '')


def ask_chartgpt(body) -> Response:
    request: Request = Request.from_dict(body)
    if is_nda_broken(request.prompt):
        return {"error": "Could not complete analysis: NDA broken"}, 400

    try:
        job_uuid = f"ask-{generate_uuid()}"
        created_at = int(time.time())
        result: QueryResult = answer_user_query(
            request=request
        )
        finished_at = int(time.time())
        return Response(
            id=job_uuid,
            created_at=created_at,
            finished_at=finished_at,
            status="succeeded",
            prompt=request.prompt,
            dataset_id="",
            attempts=result.attempts,
            output_type=request.output_type,
            outputs=result.outputs,
            errors=result.errors,
            usage=Usage(tokens=len(result.attempts)),
        ).to_dict(), 200
    except ContextLengthError:
        return {"error": "Could not complete analysis: ran out of context"}, 400
    except Exception as ex:
        return {"error": f"Could not complete analysis: {ex}"}, 400
