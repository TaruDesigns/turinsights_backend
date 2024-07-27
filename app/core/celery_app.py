from datetime import timedelta

from celery import Celery
from celery.signals import worker_init
from app.core.config import settings

celery_app = Celery(
    "worker",
    backend=f"db+postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{5432}/{settings.POSTGRES_DB}",
    broker=settings.BROKER_CONNECTION_STRING,
)


@worker_init.connect
def worker_initialize(**kwargs):
    # Add your initialization code here
    print("Startup worker...custom code")


celery_app.conf.task_routes = {
    "app.worker.tests.*": "main-queue",
    "app.worker.uipath.*": "main-queue",
}
celery_app.conf.update(
    task_serializer="json", result_serializer="json", accept_content=["json"]
)
celery_app.conf.timezone = "UTC"
# Note that this will only work when run as a beat instead of a regular worker
celery_app.conf.beat_schedule = {
    "refresh-token": {
        "task": "app.worker.uipath.FetchUIPathToken",
        "schedule": timedelta(seconds=30),
        "options": {
            "expires": 30
        },  # This will ensure the task runs immediately when the worker starts
    },
}

celery_app.send_task("app.worker.uipath.FetchUIPathToken")
