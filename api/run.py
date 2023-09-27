import asyncio
import time
from logging.config import dictConfig
from typing import AsyncGenerator, Optional

from chartgpt_client import (Attempt, Error, Output, OutputType, Request,
                             Response, Usage)
from fastapi import FastAPI, HTTPException, Security, status
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import APIKeyHeader
from fastapi.middleware.gzip import GZipMiddleware

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


def stream_response(response: Response) -> str:
    """Format the stream response."""
    return f"data: {response.to_json()}\n\n"


@app.get("/health")
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


async def data_generator(
        request: Request,
        job_id: str,
        created_at: int,
        queue: asyncio.Queue,
        stop_event: asyncio.Event,
) -> AsyncGenerator[Response, None]:
    try:
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
        await queue.put("event: stream_start\n")
        await queue.put(stream_response(response=response))
        async for result in answer_user_query(request=request, stream=True):
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
                await queue.put("event: attempt\n")
                await queue.put(stream_response(response=response))
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
                await queue.put("event: output\n")
                await queue.put(stream_response(response=response))
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
                await queue.put("event: output\n")
                await queue.put(stream_response(response=response))
            else:
                logger.error("Unhandled result type: %s", type(result))
            # Sleep briefly so concurrent tasks can run
            # 1 ms (0.001 s) limits max throughput to 1,000 requests per second
            # See https://github.com/openai/openai-cookbook/blob/main/examples/api_request_parallel_processor.py
            await asyncio.sleep(0.01)
        stop_event.set()
    except asyncio.CancelledError:
        pass


@app.post("/v1/ask_chartgpt", response_model=Response)
async def ask_chartgpt(
    request: Request, api_key: str = Security(get_api_key), stream=False
) -> Response:
    """Answer a user query using the ChartGPT API."""
    logger.info("Request: %s", request)
    job_id = utils.generate_job_id()
    # flask.g.job_id = job_id
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

    if is_nda_broken(query):
        message = "Could not complete analysis: insecure request"
        logger.error(message)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
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

    try:
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
                    job_id=job_id,
                    created_at=created_at,
                    queue=queue,
                    stop_event=stop_event,
                ))

                try:
                    while not stop_event.is_set():
                        event = await queue.get()
                        yield event
                    yield "event: stream_end\n"
                    yield "data: [DONE]\n\n"
                finally:
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
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": message},
        )
    except Exception as ex:
        message = f"Could not complete analysis: {ex}"
        logger.exception(message)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": message},
        )


@app.post("/v1/ask_chartgpt/stream", response_model=Response)
async def ask_chartgpt_stream(
    request: Request, api_key: str = Security(get_api_key)
) -> Response:
    """Stream the response from the ChartGPT API."""
    return await ask_chartgpt(request, api_key=api_key, stream=True)
