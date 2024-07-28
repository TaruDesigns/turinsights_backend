import logging
from time import sleep

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1.mainrouter import api_router

# For startup
from app.core.config import settings

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


from fastapi.responses import RedirectResponse


@app.get("/")
async def redirect_typer():
    return RedirectResponse("/docs")


@app.on_event("startup")
async def startscheduler():
    logging.info("Starting scheduler...")
    scheduler.start()
    start_basic_schedules()


if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv

    load_dotenv()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
