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
    result = fetchfolders()
    print(result)
    result = fetchjobs()
    print(result)
    result = fetchprocesses()
    print(result)
    result = fetchqueuedefinitions()
    print(result)
    result = fetchsessions()
    print(result)
    result = fetchqueueitems()
    print(result)
    """


    print(result)
"""
    # from app.worker.uipath import uipclient_queueuitems

    # res = uipclient_queueuitems.queue_items_get(select="Id", top=1, count="true", x_uipath_organization_unit_id=4572437)
    # testresponse = int(json.loads(uipclient_queueuitems.api_client.last_response.data)["@odata.count"])
    # print(testresponse)

    print("a")

    # from app.schedules.scheduler import refresh_jobsunfinished
    # asyncio.run(refresh_jobsunfinished())

    # uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
    # fetchqueueitemevents(synctimes=True)
