# external package imports.
from datetime import datetime
import json
import os.path
import platformdirs
import requests
import time

# our package imports.
from .saappmessages import SAAppMessages
from .spotifyapierror import SpotifyApiError
from .const import (
    SPOTIFY_WEBUI_URL_BASE,
    SPOTIFYWEBAPIPYTHON_TOKEN_CACHE_FILE,
)

# get smartinspect logger reference; create a new session for this module name.
from smartinspectpython.siauto import SIAuto, SILevel, SISession, SIMethodParmListContext, SIColors
import logging
_logsi:SISession = SIAuto.Si.GetSession(__name__)
if (_logsi == None):
    _logsi = SIAuto.Si.AddSession(__name__, True)
_logsi.SystemLogger = logging.getLogger(__name__)


SPOTIFY_WEBUI_URL_GET_ACCESS_TOKEN = SPOTIFY_WEBUI_URL_BASE + "/get_access_token"
""" Url used to get access token. """


class SpotifyWebPlayerToken:
    """
    Represents a Spotify web player token for an account.
    """

    def __init__(
        self, 
        clientId:str=None,
        profileId:str=None,
        tokenProviderId:str=None,
        tokenStorageDir:str=None,
        tokenStorageFile:str=None,
        spotifyWebPlayerCookieSpdc:str=None,
        spotifyWebPlayerCookieSpkey:str=None,
        ) -> None:
        """
        Initializes a new instance of the class.

        Args:
            clientId (str):
                The unique identifier of the application.
                A null value will default to `Shared`.  
                Default: `Shared`
            profileId (str):
                Profile identifier used when loading / storing the token to disk.  
                A null value will default to `Shared`.  
                Default: `Shared`
            tokenProviderId (str):
                Provider identifier used when storing the token to disk.
                A null value will default to `Shared`.  
                Default: `Shared`
            tokenStorageDir (str):
                The directory path that will contain the Token Cache file.  
                A null value will default to the platform specific storage location:  
                Example for Windows OS = `C:\\ProgramData\\SpotifyWebApiPython`
            tokenStorageFile (str):
                The filename and extension of the Token Cache file.  
                Default is `tokens.json`.
            spotifyWebPlayerCookieSpdc (str):
                Spotify Web Player Cookie credentials `sp_dc` value.  
            spotifyWebPlayerCookieSpkey (str):
                Spotify Web Player Cookie credentials `sp_key` value.

        If the `spotifyWebPlayerCookieSpdc` and `spotifyWebPlayerCookieSpkey` values are specified,
        then the Token Cache File parameters will be ignored and a token created from the specified
        values.

        Otherwise, the Token Cache File is queried to retrieve the `sp_dc` and `sp_key` values.
        """
        # validations.
        if clientId is None:
            clientId = "Shared"
        if profileId is None:
            profileId = 'Shared'

        # verify token storage directory exists.
        if tokenStorageDir is None:
            tokenStorageDir = platformdirs.site_config_dir('SpotifyWebApiPython', ensure_exists=True, appauthor=False)
        os.makedirs(tokenStorageDir, exist_ok=True)  # succeeds even if directory exists.

        # verify token storage filename was specified.
        if tokenStorageFile is None:
            tokenStorageFile = SPOTIFYWEBAPIPYTHON_TOKEN_CACHE_FILE

        # if token providerId not set, then default to shared.
        if tokenProviderId is None:
            tokenProviderId = 'SpotifyWebPlayerCookieCredentials'

        # initializa storage.
        self._AccessToken = None
        self._ClientId:str = clientId
        self._ExpiresAt:int = 0
        self._ExpireDateTimeUtc:datetime = None
        self._ExpiresIn:int = 0
        self._IsAnonymous:bool = False
        self._ProfileId:str = profileId
        self._TokenProviderId:str = tokenProviderId
        self._TokenStorageDir:str = tokenStorageDir
        self._TokenStorageFile:str = tokenStorageFile
        self._TokenStoragePath:str = os.path.join(tokenStorageDir, tokenStorageFile)
        self._sp_dc:str = spotifyWebPlayerCookieSpdc
        self._sp_key:str = spotifyWebPlayerCookieSpkey

        # were cookie credentials provided?
        if (spotifyWebPlayerCookieSpdc is not None) and (spotifyWebPlayerCookieSpkey is not None):

            # yes - create cookie credentials dictionary from parameters.
            token:dict = {
                "sp_dc": spotifyWebPlayerCookieSpdc ,
                "sp_key": spotifyWebPlayerCookieSpkey,
                "title": "SpotifyClient Credentials for user: " + profileId,
                "token_type": "CookieCredentials"
            }

            # trace.
            _logsi.LogDictionary(SILevel.Verbose, "Cookie credentials were created from passed parameters for profileId: \"%s\"" % (profileId), token, prettyPrint=True)

        else:

            # no - load cookie credentials from the token storage file.
            token:dict = self._LoadCookieCredentials()

        # get Spotify Web Player access token from stored Spotify Web Player cookie credentials.
        self.GetAccessTokenFromCookieCredentials()


    @property
    def AccessToken(self) -> str:
        """ 
        An access token that can be provided to a Spotify Web Player application.
        """
        return self._AccessToken


    @property
    def ClientId(self) -> str:
        """
        The unique identifier of the application.
        """
        return self._ClientId


    @property
    def ExpiresAt(self) -> int:
        """ 
        DateTime (in epoch seconds) that the authorization token will expire.
        """
        return self._ExpiresAt
    

    @property
    def ExpireDateTimeUtc(self) -> datetime:
        """ 
        DateTime (in UTC format) that the authorization token will expire.
        """
        return self._ExpireDateTimeUtc


    @property
    def ExpiresIn(self) -> int:
        """ 
        The time period (in seconds) for which the access token is valid.
        """
        return self._ExpiresIn
    

    @property
    def HeaderKey(self) -> str:
        """
        Returns a string containing the header key to assign the authorization token value to.
        This will always return 'Authorization'.
        """
        return 'Authorization'


    @property
    def HeaderValue(self) -> str:
        """
        Returns the value portion of the authorization header, in the form of 'Bearer {token}'.

        Example: `Bearer {token value ...}'
        """
        return 'Bearer {token}'.format(token=self.AccessToken)


    @property
    def IsExpired(self) -> bool:
        """ 
        Returns true if the token has expired; otherwise, False if not expired.
        """
        if self._ExpiresAt is not None:
            nowsecs:int = int(time.time())
            # subtract 30 seconds in case we are right at the edge of expiring.
            if (nowsecs + 30) > self._ExpiresAt:
                return True
        return False
    

    @property
    def ProfileId(self) -> str:
        """ 
        Profile identifier used when loading / storing the token to disk.
        """
        return self._ProfileId
    

    def _LoadCookieCredentials(self) -> dict:
        """
        Loads a token from the token storage file for the ProviderId / ClientId key.
        
        Returns:
            A token dictionary, if one was found in the token storage file for the
            specified ProviderId and ClientId key; otherwise, null.
        """
        apiMethodName:str = '_LoadCookieCredentials'
        apiMethodParms:SIMethodParmListContext = None
        
        try:

            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            _logsi.LogMethodParmList(SILevel.Verbose, "Loading Spotify Web Player cookie credentials from token storage", apiMethodParms)
                
            # formulate token storage key.
            tokenKey:str = f'{self._TokenProviderId}/{self._ClientId}/{self._ProfileId}'
            _logsi.LogVerbose("Cookie credentials storage key: \"%s\"" % (tokenKey))           
            _logsi.LogVerbose("Cookie credentials storage file path: \"%s\"" % (self._TokenStoragePath))
            
            # does the token storage file exist?
            if os.path.exists(self._TokenStoragePath):

                # open the token storage file, and load it's contents.
                _logsi.LogVerbose("Opening cookie credentials token storage file")
                with open(self._TokenStoragePath, 'r') as f:
                    
                    tokens = json.load(f)

                    # if token key exists then load the token.
                    if tokenKey in tokens:
                        _logsi.LogDictionary(SILevel.Verbose, "Cookie credentials were loaded from token storage file for provider: \"%s\"" % (tokenKey), tokens[tokenKey], prettyPrint=True)

                        # parse token for cookie data parameters.
                        token:dict = tokens[tokenKey]
                        self._sp_dc = token.get("sp_dc", None)
                        self._sp_key = token.get("sp_key", None)

                        # validation.
                        if (self._sp_dc is None):
                            raise SpotifyApiError("Cookie credentials storage key \"%s\" did not contain an \"sp_dc\" key value" % (tokenKey), None, logsi=_logsi)
                        if (self._sp_key is None):
                            raise SpotifyApiError("Cookie credentials storage key \"%s\" did not contain an \"sp_key\" key value" % (tokenKey), None, logsi=_logsi)

                        # return token to caller.
                        return tokens[tokenKey]
                    
            # if we make it here, then it denotes that a token was not found
            # for the specified key.
            raise SpotifyApiError("Cookie credentials storage key not found: \"%s\"" % (tokenKey), None, logsi=_logsi)
                        
        except SpotifyApiError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # trace.
            raise SpotifyApiError("Could not load Spotify Web Player cookie credentials", ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetAccessTokenFromCookieCredentials(self) -> None:
        """ 
        Get Spotify Web Player access token from stored Spotify Web Player cookie
        credentials.

        This will create a new session to the "https://open.spotify.com" url, passing
        it the stored cookie credentials.
        """
        apiMethodName:str = 'GetAccessTokenFromCookieCredentials'
        apiMethodParms:SIMethodParmListContext = None
        tracePrefix:str = 'SpotifyWebPlayerAccessToken exchange'
        
        try:

            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("sp_dc", self._sp_dc)
            apiMethodParms.AppendKeyValue("sp_key", self._sp_key)
            _logsi.LogMethodParmList(SILevel.Verbose, "Exchange Spotify Web Player cookie credentials for OAuth2 authorization access token", apiMethodParms)

            # create a session, using the specified header and generated cookie data.
            session = requests.Session()
            reqHeaders = {'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"}
            reqCookies = {'sp_dc': self._sp_dc, 'sp_key': self._sp_key}
            reqParms={
                "reason": "transport",
                "productType": "web_player",
            }

            # trace.
            _logsi.LogVerbose("Exchanging Spotify Web Player cookie credentials for OAuth2 authorization access token")
            _logsi.LogDictionary(SILevel.Verbose, "%s http request: \"%s\" (cookies)" % (tracePrefix, SPOTIFY_WEBUI_URL_GET_ACCESS_TOKEN), reqCookies)
            _logsi.LogDictionary(SILevel.Debug, "%s http request: \"%s\" (headers)" % (tracePrefix, SPOTIFY_WEBUI_URL_GET_ACCESS_TOKEN), reqHeaders)
            _logsi.LogDictionary(SILevel.Verbose, "%s http request: \"%s\" (parms)" % (tracePrefix, SPOTIFY_WEBUI_URL_GET_ACCESS_TOKEN), reqParms)

            # request retry loop for failed requests that are temporary in nature (504 Gateway Timeout, etc).
            loopTotalDelay:float = 0
            LOOP_DELAY:float = 0.200
            LOOP_TIMEOUT:float = 1.000
            while True:
            
                # convert the spotify web player cookie credentials to an access token.
                response = session.get(
                    SPOTIFY_WEBUI_URL_GET_ACCESS_TOKEN, 
                    cookies=reqCookies,
                    headers=reqHeaders, 
                    params=reqParms,
                    allow_redirects=False,
                    )

                # TEST TODO - for testing retry logic.
                # if (response.status_code == 200) and (loopTotalDelay <= 0.200):
                #     _logsi.LogWarning("TEST TODO - Testing Spotify Web API 504 status (Gateway timeout) condition ...", colorValue=SIColors.Red)
                #     response.status_code = 404
                #     response.reason = "URL Not Found"
                # if (response.status_code == 200) and (loopTotalDelay <= 0.200):
                #     _logsi.LogWarning("TEST TODO - Testing Spotify Web API 504 status (Gateway timeout) condition ...", colorValue=SIColors.Red)
                #     response.status_code = 504
                #     response.reason = "Gateway Timeout"

                # check for errors that are temporary in nature; for these errors, we will retry the 
                # request for a specified number of tries with a small wait period in between.
                if (response.status_code == 504):

                    # only retry so many times before we give up.
                    if (loopTotalDelay >= LOOP_TIMEOUT):
                        raise SpotifyApiError(SAAppMessages.MSG_SPOTIFY_WEB_API_RETRY_TIMEOUT % (loopTotalDelay), None, logsi=_logsi)

                    # trace.
                    _logsi.LogVerbose(SAAppMessages.MSG_SPOTIFY_WEB_API_RETRY_RESPONSE_STATUS % (response.status_code, response.reason), colorValue=SIColors.Red)

                    # wait just a bit between requests.
                    _logsi.LogVerbose(SAAppMessages.MSG_SPOTIFY_WEB_API_RETRY_REQUEST_DELAY % (LOOP_DELAY))
                    time.sleep(LOOP_DELAY)
                    loopTotalDelay = loopTotalDelay + LOOP_DELAY

                else:

                    # otherwise, break out of retry loop and process response.
                    break

            # trace.
            if _logsi.IsOn(SILevel.Debug):
                _logsi.LogObject(SILevel.Debug, "%s http response object - type=\"%s\", module=\"%s\"" % (tracePrefix, type(response).__name__, type(response).__module__), response)

            # trace.
            if _logsi.IsOn(SILevel.Debug):
                _logsi.LogObject(SILevel.Debug, "%s http response [%s-%s] (response)" % (tracePrefix, response.status_code, response.reason), response)
                if (response.headers):
                    _logsi.LogCollection(SILevel.Debug, "%s http response [%s-%s] (headers)" % (tracePrefix, response.status_code, response.reason), response.headers.items())

            # raise exception if we could not get the access token, or if a redirect occured.
            # the redirect usually indicates the sp_dc and sp_key are expired, and it's redirecting to a login page.
            respHdrLocation:str = response.headers.get("Location", None)
            if (response.status_code == 302 and respHdrLocation == "/get_access_token?reason=transport&productType=web_player&_authfailed=1"):
                raise SpotifyApiError("Unsuccessful token request, received status 302 and Location header \"%s\". sp_dc and sp_key could be expired. Please update values in token storage file." % (respHdrLocation), None, logsi=_logsi)

            # if successful request, then break out of the retry loop.
            if (response.status_code == 200):
                _logsi.LogVerbose("Token exchange request was successful within %f seconds from initial request; processing results" % (loopTotalDelay))
            else:
                raise SpotifyApiError("Token exchange request failed: %s - %s" % (response.status_code, response.reason), None, logsi=_logsi)

            # load request response.
            data = response.content.decode('utf-8')
            responseData = json.loads(data)

            # trace.
            if _logsi.IsOn(SILevel.Verbose):
                if isinstance(responseData, dict):
                    _logsi.LogDictionary(SILevel.Verbose, "%s http response [%s-%s] (json dict)" % (tracePrefix, response.status_code, response.reason), responseData, prettyPrint=True)
                elif isinstance(responseData, list):
                    _logsi.LogArray(SILevel.Verbose, "%s http response [%s-%s] (json array)" % (tracePrefix, response.status_code, response.reason), responseData)
                else:
                    _logsi.LogObject(SILevel.Verbose, "%s http response [%s-%s] (json object)" % (tracePrefix, response.status_code, response.reason), responseData)

            # process the access token information.
            self._AccessToken = responseData.get('accessToken', None)
            self._ExpiresAt = int(responseData.get('accessTokenExpirationTimestampMs', 0)) // 1000
            self._ExpiresIn = self._ExpiresAt - int(time.time())
            self._IsAnonymous = bool(responseData.get('isAnonymous', False))

            # set non-JSON response properties.
            # calculate expire time based on ExpiresAt (epoch) seconds.
            self._ExpireDateTimeUtc = datetime.utcfromtimestamp(self._ExpiresAt)

            # the following can be used if the `datetime.utcfromtimestamp` is ever removed from python:
            # unix_epoch = datetime(1970, 1, 1)
            # dtUtcNow:datetime = datetime.now(timezone.utc)
            # self._ExpireDateTimeUtc = dtUtcNow + timedelta(seconds=self._ExpiresIn)

            # trace.
            _logsi.LogObject(SILevel.Verbose, "Spotify Web Player access token object", self, excludeNonPublic=True)

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except requests.TooManyRedirects as ex:

            # trace.
            raise SpotifyApiError("Could not get Spotify Web Player access token; sp_dc and sp_key could be expired; Please update values in token storage file", ex, logsi=_logsi)
        
        except Exception as ex:
            
            # trace.
            raise SpotifyApiError("Could not get Spotify Web Player access token", ex, logsi=_logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)