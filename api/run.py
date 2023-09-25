import time
from logging.config import dictConfig
from typing import Iterator

from chartgpt_client import (Attempt, Error, Output, OutputType, Request,
                             Response, Usage)
from fastapi import FastAPI, HTTPException, Security
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

from api import auth, utils
from api.chartgpt import answer_user_query
from api.errors import ContextLengthError
from api.guards import is_nda_broken
from api.log import log_response, logger
from api.types import QueryResult

dictConfig(
    {
        "version": 1,
        "filters": {
            "job_id": {
                "()": "api.log.JobIdFilter",
            },
        },
        "formatters": {
            "default": {
                "format": "[%(asctime)s job_id:%(job_id)s %(module)s->%(funcName)s():%(lineno)s] %(levelname)s: %(message)s"
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
                "filters": ["job_id"],
            },
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
        "loggers": {
            "chartgpt": {"level": "DEBUG"},
        },
    }
)

app = FastAPI()

api_key_header = APIKeyHeader(name="X-API-KEY")


def get_api_key(api_key: str = Security(api_key_header)) -> str:
    if auth.check_api_key(api_key):
        return api_key
    raise HTTPException(
        status_code=401,
        detail="Invalid or missing API Key",
    )


@app.exception_handler(Exception)
async def value_error_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=400,
        content={"error": str(exc)},
    )


def stream_response(response: Response) -> Iterator[str]:
    yield "data: " + response.to_json() + "<end>\n"


@app.get("/ping/")
async def ping():
    logger.info("Ping")
    return "pong"


@app.post("/v1/ask_chartgpt/", response_model=Response)
async def ask_chartgpt(
    request: Request, api_key: str = Security(get_api_key), stream=False
) -> Response:
    logger.info("Request: %s", request)
    job_id = utils.generate_job_id()
    # flask.g.job_id = job_id
    created_at = int(time.time())

    if not request.messages:
        message = "Could not complete analysis: messages is empty"
        logger.error(message)
        return JSONResponse(
            status_code=400,
            content={"error": message},
        )
    else:
        query = request.messages[-1].content

    if is_nda_broken(query):
        message = "Could not complete analysis: insecure request"
        logger.error(message)
        return JSONResponse(
            status_code=400,
            content={"error": message},
        )

    data_source, _, _, _ = utils.parse_data_source_url(request.data_source_url)

    if data_source != "bigquery":
        message = "Could not complete analysis: data source not supported"
        logger.error(message)
        return JSONResponse(
            status_code=400,
            content={"error": message},
        )

    try:
        if stream:

            def generate_response(request: Request) -> Iterator[Response]:
                # Respond with the job ID to indicate that the job has started
                response = Response(
                    id=job_id,
                    created_at=created_at,
                    status="stream",
                    messages=request.messages,
                    data_source_url=request.data_source_url,
                    attempts=[],
                    output_type=request.output_type,
                    outputs=[],
                    errors=[],
                )
                log_response(response)
                yield from stream_response(response=response)
                for result in answer_user_query(request=request, stream=True):
                    finished_at = int(time.time())
                    if isinstance(result, Attempt):
                        attempt = result
                        response = Response(
                            id=job_id,
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
                        )
                        log_response(response)
                        yield from stream_response(response=response)
                    elif isinstance(result, Output):
                        output = result
                        response = Response(
                            id=job_id,
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
                        )
                        log_response(response)
                        yield from stream_response(response=response)
                    elif isinstance(result, QueryResult):
                        query_result = result
                        response = Response(
                            id=job_id,
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
                        )
                        log_response(response)
                        yield from stream_response(response=response)
                    else:
                        logger.error("Unhandled result type: %s", type(result))

            return StreamingResponse(
                generate_response(request=request),
                media_type="text/event-stream",
            )
        else:
            result: QueryResult = next(
                answer_user_query(
                    request=request,
                ),
                None,
            )
            finished_at = int(time.time())
            if not result:
                message = "Could not complete analysis: no result"
                logger.error(message)
                return JSONResponse(
                    status_code=400,
                    content={"error": message},
                )
            response = Response(
                id=job_id,
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
            )
            log_response(response)
            return response
    except ContextLengthError:
        message = "Could not complete analysis: ran out of context"
        logger.error(message)
        return JSONResponse(
            status_code=400,
            content={"error": message},
        )
    except Exception as ex:
        message = f"Could not complete analysis: {ex}"
        logger.exception(message)
        return JSONResponse(
            status_code=400,
            content={"error": message},
        )


@app.post("/v1/ask_chartgpt/stream/", response_model=Response)
async def ask_chartgpt_stream(
    request: Request, api_key: str = Security(get_api_key)
) -> Response:
    return await ask_chartgpt(request, api_key=api_key, stream=True)
