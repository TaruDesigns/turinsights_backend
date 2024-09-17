from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.frontend import schedules

front_router = APIRouter()


@front_router.get("/")
async def indexredirect():
    return RedirectResponse("/docs")


front_router.include_router(schedules.router, prefix="/schedules", tags=["main frontend"])
