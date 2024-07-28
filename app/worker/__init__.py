from celery.app import trace

from app.core.celery_app import celery_app
from app.worker.uipath import (
    FetchUIPathToken,
    GetUIPathToken,
    fetchfolders,
    fetchjobs,
    fetchprocesses,
    fetchqueuedefinitions,
    fetchqueueitemevents,
    fetchqueueitems,
    fetchsessions,
)

trace.LOG_SUCCESS = """\
Task %(name)s[%(id)s] succeeded in %(runtime)ss\
"""
