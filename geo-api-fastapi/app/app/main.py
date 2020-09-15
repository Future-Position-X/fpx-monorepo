from fastapi import FastAPI
from geojson_pydantic.features import FeatureCollection, Feature
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings
from fastapi.openapi.utils import get_openapi

from pydantic.schema import schema


app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

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

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Custom title",
        version="2.5.0",
        description="This is a very custom OpenAPI schema",
        routes=app.routes,
    )
    #openapi_schema["components"]["schemas"] = FeatureCollection.schema()
    openapi_schema["components"]["schemas"].update(schema([FeatureCollection, Feature], ref_prefix="#/components/schemas/")["definitions"])
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
