import json

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import openai


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(openai.APIError)
    async def openai_error_handler(request: Request, exc: openai.APIError):
        return JSONResponse(
            status_code=502,
            content={"detail": "AI service error. Please try again later."},
        )

    @app.exception_handler(json.JSONDecodeError)
    async def json_parse_error_handler(request: Request, exc: json.JSONDecodeError):
        return JSONResponse(
            status_code=502,
            content={"detail": "AI returned an unexpected response format."},
        )
