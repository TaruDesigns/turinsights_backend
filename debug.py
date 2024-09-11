# Helper debug file to avoid having to do remote debug in the container, for quick tests

from dotenv import load_dotenv

load_dotenv()


if __name__ == "__main__":
    # Debug whole app
    import asyncio
    import json
    from time import sleep

    import uvicorn

    from app.crud import uip_job
    from app.db.session import get_db
    from app.worker.uipath import (
        OLDEVENTS,
        FetchUIPathToken,
        fetchfolders,
        fetchjobs,
        fetchprocesses,
        fetchqueuedefinitions,
        fetchqueueitemevents,
        fetchqueueitems,
        fetchsessions,
    )

    FetchUIPathToken()
    # fetchqueueitems(folderlist=[4572437])
    # result = fetchfolders()
    # result = fetchjobs()
    # result = fetchprocesses()
    # result = fetchqueuedefinitions()
    # result = fetchsessions()
    # result = fetchqueueitems()
    # results = OLDEVENTS(synctimes=True)
    # result = fetchjobs(synctimes=True)
    # result = fetchqueueitemevents()
    result = fetchqueueitemevents(
        synctimes=True,
        fulldata=True,
        upsert=True,
        filter=None,
        folderlist=[2440043, 4572437, 4572438, 4572440, 4572441, 4602674],
    )

    # from app.schedules.scheduler import refresh_jobsunfinished
    # asyncio.run(refresh_jobsunfinished())

    # uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
    # fetchqueueitemevents(synctimes=True)
