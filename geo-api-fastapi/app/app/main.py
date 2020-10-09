from functools import lru_cache

import sqlalchemy_mixins
from fastapi_utils.openapi import simplify_operation_ids
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app import patch
from app.api.api_v1.api import api_router
from app.core import config
from app.core.config import Settings
from app.errors import UnauthorizedError
from fastapi import FastAPI, applications

applications.get_openapi = patch.get_openapi


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
