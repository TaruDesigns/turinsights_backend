from app.core.config import settings
from app.schemas import UIPathTokenResponse

from UIPathAPI import Configuration, ApiClient
import UIPathAPI
from authlib.integrations.requests_client import OAuth2Session


oauth2_session = OAuth2Session(
    client_id=settings.UIP_CLIENT_ID, client_secret=settings.UIP_CLIENT_SECRET, scope=settings.UIP_SCOPE
)
uipclient_config = Configuration()


def FetchUIPathToken(uipclient_config=uipclient_config):
    """Fetch UIPath Access Token.
    Helper function to fetch token and update the "config" setting

    Returns:
        UIPathTokenResponse: Pydantic model with all the parameters from repsonse (access token, expiration)
    """
    response = oauth2_session.fetch_token(url=settings.UIP_AUTH_TOKENURL, grant_type=settings.UIP_GRANT_TYPE)
    tokenresponse = UIPathTokenResponse.parse_obj(response)
    # We update the UIPConfig variable
    if uipclient_config is not None:
        uipclient_config.access_token = tokenresponse.access_token
    return tokenresponse


# On application startup, we'll get a new token and add it to uipath api configuration to get everything ready
FetchUIPathToken()


uipclient_folders = UIPathAPI.FoldersApi(ApiClient(uipclient_config))
uipclient_jobs = UIPathAPI.JobsApi(ApiClient(uipclient_config))
uipclient_queues = UIPathAPI.QueuesApi(ApiClient(uipclient_config))
uipclient_queueuitems = UIPathAPI.QueueItemsApi(ApiClient(uipclient_config))
uipclient_queuedefinitions = UIPathAPI.QueueDefinitionsApi(ApiClient(uipclient_config))
uipclient_processes = UIPathAPI.ReleasesApi(ApiClient(uipclient_config))
