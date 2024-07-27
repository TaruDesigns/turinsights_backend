import logging
from time import sleep

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router

# For startup
from app.core.config import settings

from .schedules.scheduler import scheduler, start_basic_schedules

if settings.DEBUG_MODE:
    import debugpy

    try:
        debugpy.listen(("0.0.0.0", 5678))
        sleep(5)
    except:
        print("Already set a remote debugger!")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    debug=settings.DEBUG_MODE,
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


@app.on_event("startup")
async def startscheduler():
    logging.info("Starting scheduler...")
    scheduler.start()
    start_basic_schedules()
