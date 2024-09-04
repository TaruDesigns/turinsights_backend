# Helper debug file to avoid having to do remote debug in the container, for quick tests

from dotenv import load_dotenv

load_dotenv()


if __name__ == "__main__":
    # Debug whole app
    import asyncio

    import uvicorn

    from app.crud import uip_job
    from app.db.session import get_db
    from app.worker import FetchUIPathToken, fetchqueueitemevents, fetchqueueitems

    FetchUIPathToken()
    fetchqueueitems(folderlist=[4572437])

    # from app.schedules.scheduler import refresh_jobsunfinished
    # asyncio.run(refresh_jobsunfinished())

    # uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
    # fetchqueueitemevents(synctimes=True)
