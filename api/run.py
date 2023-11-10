import asyncio
import time
from logging.config import dictConfig
from typing import AsyncGenerator, Optional

from api.models import (Attempt, Error, Output, OutputType, Request,
                             Response, Usage)
from fastapi import FastAPI, HTTPException, Security, status
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import APIKeyHeader
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.utils import get_openapi

import motor
import motor.motor_asyncio
import os

from api import auth, utils
from api.chartgpt import answer_user_query
from api.errors import ContextLengthError, PythonExecutionError
from api.security.guards import is_nda_broken
from api.log import log_response, logger
from api.types import QueryResult


# MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
db = client.api


dictConfig(
    {
        "version": 1,
        "filters": {
            "session_id": {
                "()": "api.log.SessionIdFilter",
            },
        },
        "formatters": {
            "default": {
                "format": "[%(asctime)s session_id:%(session_id)s %(module)s->%(funcName)s():%(lineno)s] %(levelname)s: %(message)s"
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
                "filters": ["session_id"],
            },
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
        "loggers": {
            "chartgpt": {"level": "DEBUG"},
        },
    }
)


app = FastAPI()


def openapi_config():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="ChartGPT API",
        version="0.1.0",
        # summary="",
        description="The ChartGPT API is a REST API that generates insights from data based on natural language questions.",
        routes=app.routes,
    )
    # openapi_schema["info"]["x-logo"] = {
    #     "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    # }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = openapi_config


api_key_header = APIKeyHeader(name="X-API-KEY")
def get_api_key(api_key: str = Security(api_key_header)) -> str:
    """Authenticate using the API key from the request."""
    if auth.check_api_key(api_key):
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )


# Enable GZip compression for responses larger than 5 MB
# app.add_middleware(GZipMiddleware, minimum_size=5_000_000)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.exception_handler(Exception)
async def uncaught_exception_handler(_: Request, exc: Exception):
    """Handle uncaught exceptions raised by the API."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": str(exc)},
    )


def format_response_event(response: Response) -> str:
    """Format the response for event stream."""
    return f"data: {response.to_json()}\n\n"


@app.get("/health", tags=["health"])
async def ping():
    """Ping the API to check if it is running."""
    logger.info("Health check")
    return "ok"


async def keep_alive_generator(queue: asyncio.Queue, stop_event: asyncio.Event) -> AsyncGenerator[str, None]:
    try:
        while not stop_event.is_set():
            await asyncio.sleep(15)
            await queue.put("event: keep-alive\n")
            await queue.put("data: {}\n\n")
    except asyncio.CancelledError:
        pass


async def handle_response(response: Response, queue: asyncio.Queue) -> None:
    log_response(response)
    await queue.put(format_response_event(response=response))
    await db["responses"].insert_one(response.dict())


async def data_generator(
        request: Request,
        session_id: str,
        created_at: int,
        queue: asyncio.Queue,
        stop_event: asyncio.Event,
) -> AsyncGenerator[Response, None]:
    try:
        # Respond with the job ID to indicate that the job has started
        response = Response(
            session_id=session_id,
            created_at=created_at,
            status="stream",
            messages=request.messages,
            data_source_url=request.data_source_url,
            attempts=[],
            output_type=request.output_type,
            outputs=[],
            errors=[],
        )
        await queue.put("event: stream_start\n")
        await handle_response(response=response, queue=queue)
        async for result in answer_user_query(request=request, stream=True):
            finished_at = int(time.time())
            if isinstance(result, Attempt):
                attempt = result
                response = Response(
                    session_id=session_id,
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
                await queue.put("event: attempt\n")
                await handle_response(response=response, queue=queue)
            elif isinstance(result, Output):
                output = result
                response = Response(
                    session_id=session_id,
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
                await queue.put("event: output\n")
                await handle_response(response=response, queue=queue)
            elif isinstance(result, QueryResult):
                query_result = result
                response = Response(
                    session_id=session_id,
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
                await queue.put("event: output\n")
                await handle_response(response=response, queue=queue)
            else:
                logger.error("Unhandled result type: %s", type(result))
            # Sleep briefly so concurrent tasks can run
            # 1 ms (0.001 s) limits max throughput to 1,000 requests per second
            # See https://github.com/openai/openai-cookbook/blob/main/examples/api_request_parallel_processor.py
            await asyncio.sleep(0.01)
        stop_event.set()
    except PythonExecutionError as ex:
        # TODO Return user friendly errors
        logger.error("Stream PythonExecutionError: %s", ex)
        response = Response(
            session_id=session_id,
            created_at=created_at,
            finished_at=int(time.time()),
            status="failed",
            messages=request.messages,
            data_source_url=request.data_source_url,
            attempts=[],
            output_type=request.output_type,
            outputs=[],
            errors=[Error(
                index=0,
                created_at=int(time.time()),
                type="PythonExecutionError",
                value=str(ex),
            )],
        )
        await queue.put("event: error\n")
        await handle_response(response=response, queue=queue)
    except asyncio.CancelledError:
        pass
    finally:
        stop_event.set()


# TODO Complete get_data_source_sample_rows endpoint
# @app.get("/v1/data_sources/{data_source_url}/sample_rows", tags=["data_sources"])
# async def get_data_source_sample_rows(...)


@app.post("/v1/ask_chartgpt", response_model=Response, tags=["chat"])
async def ask_chartgpt(
    request: Request, api_key: str = Security(get_api_key), stream=False
) -> Response:
    """Answer a user query using the ChartGPT API."""
    try:
        session_id = utils.generate_session_id()
        request.session_id = session_id
        logger.info("Request: %s", request)
        await db["requests"].insert_one({
            **request.dict(),
            "api_key": api_key
        })
        created_at = int(time.time())

        if not request.messages:
            message = "Could not complete analysis: messages is empty"
            logger.error(message)
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": message},
            )
        else:
            query = request.messages[-1].content

        if await is_nda_broken(query):
            message = "Could not complete analysis: insecure request"
            logger.error(message)
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"error": message},
            )

        data_source, _, _, _ = utils.parse_data_source_url(request.data_source_url)

        if data_source != "bigquery":
            message = "Could not complete analysis: data source not supported"
            logger.error(message)
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": message},
            )

        if stream:
            async def generate_response(request: Request) -> AsyncGenerator[str, None]:
                queue = asyncio.Queue()
                stop_event = asyncio.Event()

                keep_alive_task = asyncio.create_task(keep_alive_generator(
                    queue=queue,
                    stop_event=stop_event
                ))
                
                data_task = asyncio.create_task(data_generator(
                    request=request,
                    session_id=session_id,
                    created_at=created_at,
                    queue=queue,
                    stop_event=stop_event,
                ))
                try:
                    while not stop_event.is_set():
                        event = await queue.get()
                        yield event
                finally:
                    yield "event: stream_end\n"
                    yield "data: [DONE]\n\n"
                    keep_alive_task.cancel()
                    data_task.cancel()
                    await asyncio.gather(keep_alive_task, data_task, return_exceptions=True)

            return StreamingResponse(
                generate_response(request=request),
                status_code=status.HTTP_200_OK,
                headers={
                    "Content-type": "text/event-stream",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    # TODO Investigate compression techniques
                    # "Content-Encoding": "deflate",
                }
            )
        else:
            result: Optional[QueryResult] = None
            async for temp_result in answer_user_query(request=request):
                result = temp_result
                break
            finished_at = int(time.time())
            if not result:
                message = "Could not complete analysis: no result"
                logger.error(message)
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"error": message},
                )
            response = Response(
                session_id=session_id,
                created_at=created_at,
                finished_at=finished_at,
                status="succeeded",
                messages=request.messages,
                data_source_url=request.data_source_url,
                attempts=result.attempts,
                output_type=request.output_type,
                outputs=result.outputs,
                errors=result.errors,
                usage=Usage(tokens=len(result.attempts)),
            )
            log_response(response)
            await db["responses"].insert_one(response.dict())
            return response
    except asyncio.exceptions.CancelledError:
        message = "Could not complete analysis: request cancelled"
        logger.error(message)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": message},
        )
    except ContextLengthError:
        message = "Could not complete analysis: ran out of context"
        logger.error(message)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": message},
        )
    except Exception:
        message = "Could not complete analysis"
        logger.exception(message)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": message},
        )


@app.post("/v1/ask_chartgpt/stream", response_model=Response, tags=["chat"])
async def ask_chartgpt_stream(
    request: Request, api_key: str = Security(get_api_key)
) -> Response:
    """Stream the response from the ChartGPT API."""
    return await ask_chartgpt(request, api_key=api_key, stream=True)
