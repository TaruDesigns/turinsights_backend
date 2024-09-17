# Helper debug file to avoid having to do remote debug in the container, for quick tests

from dotenv import load_dotenv

load_dotenv()


if __name__ == "__main__":
    # Debug whole app
    """
    from app.worker.uipath import (
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
    result = fetchfolders()
    result = fetchjobs()
    result = fetchprocesses()
    result = fetchqueuedefinitions()
    result = fetchsessions()
    result = fetchqueueitems()
    result = fetchjobs(synctimes=True)
    result = fetchqueueitemevents()
"""
    import uvicorn

    from app.core.uipapiconfig import uipclient_folders
    from app.main import app
    from app.schedules import scheduler

    try:
        res = uipclient_folders.folders_get()
    except Exception as e:
        print(e)
        print("Test")

    # uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
    # scheduler.scheduler.start(paused=True)
    # jobs = scheduler.scheduler.get_jobs()

    print("")
