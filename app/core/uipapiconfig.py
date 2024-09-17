import uipath_orchestrator_rest
from authlib.integrations.requests_client import OAuth2Session
from loguru import logger
from uipath_orchestrator_rest import ApiClient, Configuration
from uipath_orchestrator_rest.rest import ApiException

from app import crud, schemas
from app.core.config import settings
from app.db.session import get_db

oauth2_session = OAuth2Session(
    client_id=settings.UIP_CLIENT_ID,
    client_secret=settings.UIP_CLIENT_SECRET,
    scope=settings.UIP_SCOPE,
)
uipclient_config = Configuration()
uipclient_config.host = settings.UIP_API_URL


def FetchUIPathToken(uipclient_config=uipclient_config) -> schemas.UIPathTokenResponse:
    """Fetch UIPath Access Token.
    Fetches a new token and update the "config" setting, deleting old tokens as well

    Returns:
        UIPathTokenResponse: Pydantic model with all the parameters from repsonse (access token, expiration)
    """
    logger.info("Refreshing token")
    response = oauth2_session.fetch_token(url=settings.UIP_AUTH_TOKENURL, grant_type=settings.UIP_GRANT_TYPE)
    tokenresponse = schemas.UIPathTokenResponse.parse_obj(response)
    # We update the UIPConfig variable
    if uipclient_config is not None:
        uipclient_config.access_token = tokenresponse.access_token
    with get_db() as db:
        crud.uipath_token.upsert(db=db, obj_in=tokenresponse)
        crud.uipath_token.remove_expired(db=db)
    logger.info("Token Updated")
    return tokenresponse


class SafeApiWrapper:
    """Wrapper to automatically refresh token when it's expired"""

    def __init__(self, api_instance):
        self._api_instance = api_instance

    def __getattr__(self, name):
        api_method = getattr(self._api_instance, name)

        if callable(api_method):

            def wrapped_method(*args, **kwargs):
                try:
                    return api_method(*args, **kwargs)
                except ApiException as e:
                    if e.status == 401 and "not authenticated" in e.body:
                        logger.error(f"An error occurred in method {name}: {e}")
                        try:
                            # Call the "refreshtoken" function (assumed to exist)
                            FetchUIPathToken()
                            # Retry the API method after refreshing the token
                            return api_method(*args, **kwargs)
                        except Exception as retry_exception:
                            raise e

            return wrapped_method
        else:
            return api_method


# On application startup, we'll get a new token and add it to uipath api configuration to get everything ready


unsafe_uipclient_folders = uipath_orchestrator_rest.FoldersApi(ApiClient(uipclient_config))
uipclient_folders = SafeApiWrapper(unsafe_uipclient_folders)
uipclient_jobs = uipath_orchestrator_rest.JobsApi(ApiClient(uipclient_config))
uipclient_queueuitems = uipath_orchestrator_rest.QueueItemsApi(ApiClient(uipclient_config))
uipclient_queueuitemevents = uipath_orchestrator_rest.QueueItemEventsApi(ApiClient(uipclient_config))
uipclient_queuedefinitions = uipath_orchestrator_rest.QueueDefinitionsApi(ApiClient(uipclient_config))
uipclient_processes = uipath_orchestrator_rest.ReleasesApi(ApiClient(uipclient_config))
uipclient_sessions = uipath_orchestrator_rest.SessionsApi(ApiClient(uipclient_config))
