from fastapi import APIRouter

from app.api.api_v1.endpoints import items, login, users, utils, acls, collections, providers, sessions, health

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(users.router, prefix="", tags=["users"])
api_router.include_router(items.router, prefix="", tags=["items"])
api_router.include_router(acls.router, prefix="", tags=["acls"])
api_router.include_router(collections.router, prefix="", tags=["collections"])
api_router.include_router(providers.router, prefix="", tags=["providers"])
api_router.include_router(sessions.router, prefix="", tags=["sessions"])
api_router.include_router(health.router, prefix="", tags=["health"])
