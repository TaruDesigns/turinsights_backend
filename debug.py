# Helper debug file to avoid having to do remote debug in the container, for quick tests

from dotenv import load_dotenv

load_dotenv()


if __name__ == "__main__":
    # Debug whole app

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
