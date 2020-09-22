from functools import lru_cache

import sqlalchemy_mixins
from fastapi import FastAPI
from geojson_pydantic.features import FeatureCollection, Feature
from pydantic import ValidationError
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core import config
from fastapi.openapi.utils import get_openapi

from pydantic.schema import schema
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.errors import UnauthorizedError

@lru_cache()
def get_settings():
    return config.settings


settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


@app.exception_handler(sqlalchemy_mixins.ModelNotFoundError)
async def unicorn_exception_handler(request: Request, exc: sqlalchemy_mixins.ModelNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"message": f"Not found"},
    )


@app.exception_handler(PermissionError)
async def unicorn_exception_handler(request: Request, exc: PermissionError):
    return JSONResponse(
        status_code=403,
        content={"message": f"Permission error"},
    )


@app.exception_handler(UnauthorizedError)
async def unicorn_exception_handler(request: Request, exc: UnauthorizedError):
    return JSONResponse(
        status_code=401,
        content={"message": f"Unauthorized error"},
    )


@app.exception_handler(ValueError)
async def unicorn_exception_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"message": f"Value error"},
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
