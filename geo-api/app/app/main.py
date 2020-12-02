import sys
from functools import lru_cache
from typing import cast

import sentry_sdk
import sqlalchemy_mixins
from fastapi import FastAPI, applications
from fastapi_utils.openapi import simplify_operation_ids
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app import patch
from app.api.api_v1.api import api_router
from app.core import config
from app.core.config import Settings
from app.errors import UnauthorizedError, UserAlreadyExistsError

applications.get_openapi = patch.get_openapi
applications.get_swagger_ui_html = patch.get_swagger_ui_html


@lru_cache()
def get_settings() -> Settings:
    return config.settings


settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


@app.exception_handler(sqlalchemy_mixins.ModelNotFoundError)
async def model_not_found_exception_handler(
    request: Request, exc: sqlalchemy_mixins.ModelNotFoundError
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"message": "Not found"})


@app.exception_handler(PermissionError)
async def permission_exception_handler(
    request: Request, exc: PermissionError
) -> JSONResponse:
    return JSONResponse(status_code=403, content={"message": "Permission error"})


@app.exception_handler(UnauthorizedError)
async def unauthorized_exception_handler(
    request: Request, exc: UnauthorizedError
) -> JSONResponse:
    return JSONResponse(status_code=401, content={"message": "Unauthorized error"})


@app.exception_handler(ValueError)
async def value_exception_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"message": "Value error"})


@app.exception_handler(UserAlreadyExistsError)
async def user_already_exists_exception_handler(
    request: Request, exc: UserAlreadyExistsError
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"message": "The specified email is already registered"},
    )


# @app.exception_handler(ValidationError)
# async def unicorn_exception_handler(request: Request, exc: ValidationError):
#     return JSONResponse(
#         status_code=422,
#         content={"message": f"Validation error"},
#     )


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

simplify_operation_ids(app)

if "pytest" not in sys.modules and False:
    sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.2)
    app = cast(FastAPI, SentryAsgiMiddleware(app))
