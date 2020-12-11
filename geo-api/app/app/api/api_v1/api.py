from fastapi import APIRouter, Depends

from app.api.api_v1.endpoints import (
    acls,
    collections,
    health,
    items,
    login,
    providers,
    sessions,
    users,
    utils,
    series,
    metrics,
)
from app.api.deps import get_db

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"], dependencies=[Depends(get_db)])
api_router.include_router(
    utils.router, prefix="/utils", tags=["utils"], dependencies=[Depends(get_db)]
)
api_router.include_router(
    users.router, prefix="", tags=["users"], dependencies=[Depends(get_db)]
)
api_router.include_router(
    items.router, prefix="", tags=["items"], dependencies=[Depends(get_db)]
)
api_router.include_router(
    acls.router, prefix="", tags=["acls"], dependencies=[Depends(get_db)]
)
api_router.include_router(
    collections.router, prefix="", tags=["collections"], dependencies=[Depends(get_db)]
)
api_router.include_router(
    providers.router, prefix="", tags=["providers"], dependencies=[Depends(get_db)]
)
api_router.include_router(
    sessions.router, prefix="", tags=["sessions"], dependencies=[Depends(get_db)]
)
api_router.include_router(
    health.router, prefix="", tags=["health"], dependencies=[Depends(get_db)]
)
api_router.include_router(
    series.router, prefix="", tags=["series"], dependencies=[Depends(get_db)]
)
api_router.include_router(
    metrics.router, prefix="", tags=["metrics"], dependencies=[Depends(get_db)]
)
