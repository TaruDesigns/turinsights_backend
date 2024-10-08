from time import sleep

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1.mainrouter import api_router

# For startup
from app.core.config import settings
from app.frontend.mainrouter import front_router

from .schedules.scheduler import scheduler, start_basic_schedules

if settings.DEBUG_MODE:
    import debugpy

    try:
        debugpy.listen(("0.0.0.0", 5678))
        sleep(5)
    except Exception as e:
        print(f"Already set a remote debugger!: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    debug=settings.DEBUG_MODE,
)

app.mount("/static", StaticFiles(directory="./app/static"), name="static")

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
app.include_router(front_router, prefix="")


"""
@app.on_event("startup")
async def startscheduler():
    logger.info("Starting scheduler...")
    start_basic_schedules()
    scheduler.resume()
    logger.info("Schedule started")
"""

if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv

    load_dotenv()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
