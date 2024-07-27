from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    items,
    login,
    proxy,
    services,
    tracking,
    uipath,
    users,
    utils,
)

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(proxy.router, prefix="/proxy", tags=["proxy"])
api_router.include_router(services.router, prefix="/service", tags=["service"])
api_router.include_router(uipath.router, prefix="/uipath", tags=["uipath"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(tracking.router, prefix="/tracking", tags=["tracking"])
