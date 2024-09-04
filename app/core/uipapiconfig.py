import uipath_orchestrator_rest
from authlib.integrations.requests_client import OAuth2Session
from uipath_orchestrator_rest import ApiClient, Configuration

from app.core.config import settings

oauth2_session = OAuth2Session(
    client_id=settings.UIP_CLIENT_ID,
    client_secret=settings.UIP_CLIENT_SECRET,
    scope=settings.UIP_SCOPE,
)
uipclient_config = Configuration()
uipclient_config.host = settings.UIP_API_URL


# On application startup, we'll get a new token and add it to uipath api configuration to get everything ready


uipclient_folders = uipath_orchestrator_rest.FoldersApi(ApiClient(uipclient_config))
uipclient_jobs = uipath_orchestrator_rest.JobsApi(ApiClient(uipclient_config))
uipclient_queueuitems = uipath_orchestrator_rest.QueueItemsApi(ApiClient(uipclient_config))
uipclient_queueuitemevents = uipath_orchestrator_rest.QueueItemEventsApi(ApiClient(uipclient_config))
uipclient_queuedefinitions = uipath_orchestrator_rest.QueueDefinitionsApi(ApiClient(uipclient_config))
uipclient_processes = uipath_orchestrator_rest.ReleasesApi(ApiClient(uipclient_config))
uipclient_sessions = uipath_orchestrator_rest.SessionsApi(ApiClient(uipclient_config))
