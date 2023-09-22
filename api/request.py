import time
from typing import Iterator

from flask import (
    Response as FlaskResponse,
    stream_with_context
)

from chartgpt_client import Request, Response, Usage, Attempt, Error, Output, OutputType

from api.chartgpt import answer_user_query
from api.errors import ContextLengthError
from api.guards import is_nda_broken
from api.types import QueryResult
from api.utils import generate_uuid, parse_data_source_url
from api.logging import logger


def ask_chartgpt(body, stream=False) -> Response:
    request: Request = Request.from_dict(body)
    job_uuid = f"ask-{generate_uuid()}"
    created_at = int(time.time())
    logger.debug("Request %s: %s", job_uuid, request.to_dict())

    if not request.messages:
        message = "Could not complete analysis: messages is empty"
        logger.error(message)
        return {"error": message}, 400
    else:
        query = request.messages[-1].content

    if is_nda_broken(query):
        message = "Could not complete analysis: insecure request"
        logger.error(message)
        return {"error": message}, 400

    data_source, _, _, _ = parse_data_source_url(request.data_source_url)

    if data_source != "bigquery":
        message = "Could not complete analysis: data source not supported"
        logger.error(message)
        return {"error": message}, 400

    try:
        if stream:
            def generate_response(request: Request) -> Iterator[Response]:
                # Respond with the job ID to indicate that the job has started
                yield Response(
                    id=job_uuid,
                    created_at=created_at,
                    status="stream",
                    messages=request.messages,
                    data_source_url=request.data_source_url,
                    attempts=[],
                    output_type=request.output_type,
                    outputs=[],
                    errors=[],
                )
                for result in answer_user_query(
                    request=request,
                    stream=True
                ):
                    finished_at = int(time.time())
                    if isinstance(result, Attempt):
                        attempt = result
                        yield "data: " + Response(
                            id=job_uuid,
                            created_at=created_at,
                            finished_at=finished_at,
                            status="stream",
                            # TODO Update messages with each output
                            messages=request.messages,
                            data_source_url=request.data_source_url,
                            attempts=[attempt],
                            output_type=request.output_type,
                            outputs=[],
                            errors=[],
                            # usage=Usage(tokens=len(result.attempts)),
                        ).to_json() + '<end>\n'
                    elif isinstance(result, Output):
                        output = result
                        yield "data: " + Response(
                            id=job_uuid,
                            created_at=created_at,
                            finished_at=finished_at,
                            status="stream",
                            # TODO Update messages with each output
                            messages=request.messages,
                            data_source_url=request.data_source_url,
                            attempts=[],
                            output_type=request.output_type,
                            outputs=[output],
                            errors=[],
                            # usage=Usage(tokens=len(result.attempts)),
                        ).to_json() + '<end>\n'
                    elif isinstance(result, QueryResult):
                        query_result = result
                        yield "data: " + Response(
                            id=job_uuid,
                            created_at=created_at,
                            finished_at=finished_at,
                            status="stream",
                            # TODO Update messages
                            messages=request.messages,
                            data_source_url=request.data_source_url,
                            attempts=query_result.attempts,
                            output_type=request.output_type,
                            outputs=query_result.outputs,
                            errors=query_result.errors,
                            usage=Usage(tokens=len(query_result.attempts)),
                        ).to_json() + '<end>\n'
                    else:
                        logger.error("Unhandled result type: %s", type(result))
            return FlaskResponse(stream_with_context(generate_response(request=request)), content_type='text/event-stream')
        else:
            result: QueryResult = next(answer_user_query(
                request=request,
            ), None)
            finished_at = int(time.time())
            if not result:
                message = "Could not complete analysis: no result"
                logger.error(message)
                return {"error": message}, 400
            return (
                Response(
                    id=job_uuid,
                    created_at=created_at,
                    finished_at=finished_at,
                    status="succeeded",
                    # TODO Update messages
                    messages=request.messages,
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
        message = "Could not complete analysis: ran out of context"
        logger.error(message)
        return {"error": message}, 400
    except Exception as ex:
        message = f"Could not complete analysis: {ex}"
        logger.exception(message)
        return {"error": message}, 400


def ask_chartgpt_stream(body) -> Response:
    return ask_chartgpt(body, stream=True)
