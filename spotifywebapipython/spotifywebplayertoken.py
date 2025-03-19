# external package imports.
from datetime import datetime
import json
import math
import os.path
import platformdirs
from pyotp import TOTP
import requests
import time

# our package imports.
from .saappmessages import SAAppMessages
from .sautils import GetUnixTimestampMSFromUtcNow
from .spotifyapierror import SpotifyApiError
from .const import (
    SPOTIFY_WEBAPI_URL_BASE,
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

SPOTIFY_WEBUI_URL_GET_SERVER_TIME = SPOTIFY_WEBUI_URL_BASE + "/server-time"
""" Url used to get Spotify server time. """


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
            raise SpotifyApiError("Spotify Web Player Cookie credentials were not found for user: \"%s\"" % (self._ProfileId), None, logsi=_logsi)
                        
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

            # set initial TOTP request reason to "transport".
            totpReason:str = "transport"

            # request retry loop for failed requests that are temporary in nature (504 Gateway Timeout, etc).
            loopTotalDelay:float = 0
            LOOP_DELAY:float = 0.200
            LOOP_TIMEOUT:float = 1.000
            LOOP_TOTP_RETRY_CNT:int = 0
            while True:
            
                # get our current utc timestamp (current utc date, in epoch seconds).
                totpTimestamp:int = math.floor(GetUnixTimestampMSFromUtcNow() / 1000)

                # create a TOTP processing instance.
                totpObj:TOTP = None
                serverTimeSeconds:int = 0
                totpObj, serverTimeSeconds = self.GetTotpObject()

                # generate the Time-based One Time Password (TOTP) value.
                totpValue:str = totpObj.at(serverTimeSeconds)
                _logsi.LogString(SILevel.Verbose, "Spotify TOTP (Time-based One Time Password) value (len=%d)" % (len(totpValue)), totpValue)

                # create a session, using the specified header and cookie data.
                session = requests.Session()
                reqUrl:str = SPOTIFY_WEBUI_URL_GET_ACCESS_TOKEN
                reqHeaders = {'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"}
                reqCookies = {
                    "sp_dc": self._sp_dc, 
                    "sp_key": self._sp_key,  # sp_key is not required if totp value present.
                    }
                reqParms={
                    # "reason": totpReason,
                    # "productType": "web_player",
                    # "totp": totpValue,
                    # "totpVer": 5,
                    # "ts": totpTimestamp,
                    "reason": totpReason,
                    "productType": "web-player",
                    "totp": totpValue,
                    "totpServer": totpValue,
                    "totpVer": 5,
                    "sTime": serverTimeSeconds,
                    "cTime": serverTimeSeconds,
                }

                # trace.
                _logsi.LogVerbose("Exchanging Spotify Web Player cookie credentials for OAuth2 authorization access token")
                _logsi.LogDictionary(SILevel.Verbose, "%s http request: \"%s\" (cookies)" % (tracePrefix, reqUrl), reqCookies)
                _logsi.LogDictionary(SILevel.Debug, "%s http request: \"%s\" (headers)" % (tracePrefix, reqUrl), reqHeaders)
                _logsi.LogDictionary(SILevel.Verbose, "%s http request: \"%s\" (parms)" % (tracePrefix, reqUrl), reqParms)

                # convert the spotify web player cookie credentials to an access token.
                response = session.get(
                    reqUrl, 
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

                    # process next while iteration.
                    continue

                # trace.
                if _logsi.IsOn(SILevel.Debug):
                    _logsi.LogObject(SILevel.Debug, "%s http response object - type=\"%s\", module=\"%s\"" % (tracePrefix, type(response).__name__, type(response).__module__), response)
                    _logsi.LogObject(SILevel.Debug, "%s http response [%s-%s] (response)" % (tracePrefix, response.status_code, response.reason), response)
                    if (response.headers):
                        _logsi.LogCollection(SILevel.Debug, "%s http response [%s-%s] (headers)" % (tracePrefix, response.status_code, response.reason), response.headers.items())

                # raise exception if we could not get the access token, or if a redirect occured.
                # the redirect usually indicates the sp_dc and sp_key are expired, and it's redirecting to a login page.
                respHdrLocation:str = response.headers.get("location", "")
                if ((response.status_code == 302) and (respHdrLocation.find("_authfailed=1") != -1)):
                    raise SpotifyApiError("Token exchange request failed with status 302 and \"authfailed\" indicator. sp_dc and sp_key could be expired; please update values in configuration options.", None, logsi=_logsi)

                # if successful request, then process response; otherwise, it's an exception.
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

                # at this point we have an authorization token, but we don't know if it's really valid!
                # we will verify token is valid by requesting the current users profile.
                # if user profile request is valid, then we know it's good; otherwise, we will
                # repeat the whole process uing a totp reason of "init".
                # sometimes it takes a few tries to get a valid token (we limit it to 5 tries).

                # verify token is valid by retrieving current users profile.
                _logsi.LogVerbose("Verifying Spotify Web Player authorization token is valid")

                # request current users profile to check token validity.
                reqUrl:str = SPOTIFY_WEBAPI_URL_BASE + "/me"
                reqHeaders = {
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
                    "Authorization":self.HeaderValue
                }

                # trace.
                _logsi.LogVerbose("Requesting Spotify Current Users Profile to check Spotify Web Player authorization access token validity")
                _logsi.LogDictionary(SILevel.Debug, "%s http request: \"%s\" (headers)" % (tracePrefix, reqUrl), reqHeaders)

                # execute spotify web api request.
                response = session.get(reqUrl, headers=reqHeaders)

                # trace.
                if _logsi.IsOn(SILevel.Debug):
                    _logsi.LogObject(SILevel.Debug, "%s http response object - type=\"%s\", module=\"%s\"" % (tracePrefix, type(response).__name__, type(response).__module__), response)
                    _logsi.LogObject(SILevel.Debug, "%s http response [%s-%s] (response)" % (tracePrefix, response.status_code, response.reason), response)
                    if (response.headers):
                        _logsi.LogCollection(SILevel.Debug, "%s http response [%s-%s] (headers)" % (tracePrefix, response.status_code, response.reason), response.headers.items())

                # was request successful?
                if (response.status_code == 200):

                    # yes - break out of while loop; we have a valid token!
                    _logsi.LogVerbose("Spotify Web Player authorization token is valid (TOTP Retry Count=%s)" % (LOOP_TOTP_RETRY_CNT), colorValue=SIColors.Gold)
                    break

                else:

                    # no - set TOTP request reason to "init" for token retry requests.
                    totpReason:str = "init"
                    _logsi.LogVerbose("Spotify Web Player authorization token is NOT valid; retrying (TOTP Retry Count=%s) ..." % (LOOP_TOTP_RETRY_CNT), colorValue=SIColors.Red)

                # bump TOTP retry count; break out of the loop if limit is exceeded.
                LOOP_TOTP_RETRY_CNT += 1
                if (LOOP_TOTP_RETRY_CNT > 5):
                    raise SpotifyApiError("Spotify Web Player authorization token could not be retrieved!", None, logsi=_logsi)

            # trace.
            _logsi.LogObject(SILevel.Verbose, "Spotify Web Player access token object", self, excludeNonPublic=True)

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except requests.TooManyRedirects as ex:

            # trace.
            raise SpotifyApiError("Could not get Spotify Web Player access token; sp_dc could be expired - please update value", ex, logsi=_logsi)
        
        except Exception as ex:
            
            # trace.
            raise SpotifyApiError("Could not get Spotify Web Player access token", ex, logsi=_logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetTotpObject(self) -> tuple[TOTP, int]:
        """ 
        Creates a TOTP (Time-based One Time Password) object that can be used to generate a time-based
        one time password value for the Spotify `get_access_token` request.

        Returns:
            totpObj (TOTP):
                A TOTP object, which can be used to generate the One Time Password value.
            serverTimeSeconds (int):
                Spotify server time value (in utc epoch seconds).

        TOTP authentication is a 2-factor verification method that uses the time as a variable.

        TOTP codes are valid for a short period (typically 30 or 60 seconds) to enhance 
        security by preventing replay attacks. 

        Here's how a TOTP algorithm works:
        
        1. A user wants to log into a TOTP 2FA protected application or website. 
           For the OTP authentication to run, the user and the TOTP server need to initially share 
           a static parameter (a secret key).

        2. When the client logs into the protected website, they have to confirm they possess the secret key. 
           So their TOTP token merges the seed and the current timestep and generates a HASH value by running 
           a predetermined HASH function. This value essentially is the OTP code the user sees on the token.

        3. Since the secret key, the HASH function, and the timestep are the same for both parties, the server 
           makes the same computation as the user's OTP generator.

        4. The user enters the OTP and if it is identical to the server's value, the access is granted. 
           If the results of the calculations aren't identical, the access is, naturally, denied.
        """
        apiMethodName:str = 'GetTotpObject'
        apiMethodParms:SIMethodParmListContext = None
        tracePrefix:str = 'SpotifyWebPlayerAccessToken TOTP Object'
        
        try:

            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            _logsi.LogMethodParmList(SILevel.Verbose, "Generating Spotify TOTP (Time-based One Time Password) value", apiMethodParms)

            # characters allowed in the generated base32 secret string value.
            secretSauce:str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"

            # perform a bitwise XOR (^) on each cipherbyte.
            secretCipherBytesRaw:list = [12, 56, 76, 33, 88, 44, 88, 33, 78, 78, 11, 66, 22, 22, 55, 69, 54]
            _logsi.LogArray(SILevel.Debug, "%s - secretCipherBytesRaw (len=%d)" % (tracePrefix, len(secretCipherBytesRaw)), secretCipherBytesRaw)
            secretCipherBytes:list = [
                elm ^ ((idx % 33) + 9) 
                for idx, elm in enumerate(secretCipherBytesRaw)
            ]
            _logsi.LogArray(SILevel.Debug, "%s - secretCipherBytes (len=%d)" % (tracePrefix, len(secretCipherBytes)), secretCipherBytes)

            # convert secret cipher bytes into a string, then encode as UTF-8.
            secretCipherString:str = "".join(str(num) for num in secretCipherBytes)
            _logsi.LogString(SILevel.Debug, "%s - secretCipherString (len=%d)" % (tracePrefix, len(secretCipherString)), secretCipherString)
            secretCipherBytesEncoded:bytes = secretCipherString.encode("utf-8")
            _logsi.LogBinary(SILevel.Debug, "%s - secretCipherBytesEncoded (len=%d)" % (tracePrefix, len(secretCipherBytesEncoded)), secretCipherBytesEncoded)

            # convert each byte to hexadecimal string.
            secretCipherBytesHex:str = "".join(["{:02x}".format(byte) for byte in secretCipherBytesEncoded])
            _logsi.LogString(SILevel.Debug, "%s - secretCipherBytesHex (len=%d)" % (tracePrefix, len(secretCipherBytesHex)), secretCipherBytesHex)

            # clean the result using the CleanBuffer function.
            secretBytes:bytes = self.CleanBuffer(secretCipherBytesHex)
            _logsi.LogBinary(SILevel.Debug, "%s - secretBytes (len=%d)" % (tracePrefix, len(secretBytes)), secretBytes)

            # convert bytes to base32 string value.
            secretBase32:str = self.Base32FromBytes(secretBytes, secretSauce)
            _logsi.LogString(SILevel.Debug, "%s - secretBase32 (len=%d)" % (tracePrefix, len(secretBase32)), secretBase32)

            # create a session, using the specified header data.
            session = requests.Session()
            reqUrl:str = SPOTIFY_WEBUI_URL_GET_SERVER_TIME
            reqHeaders = {'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"}

            # trace.
            _logsi.LogVerbose("Retrieving Spotify TOTP server time value")
            _logsi.LogDictionary(SILevel.Debug, "%s http request: \"%s\" (headers)" % (tracePrefix, SPOTIFY_WEBUI_URL_GET_SERVER_TIME), reqHeaders)

            # request retry loop for failed requests that are temporary in nature (504 Gateway Timeout, etc).
            loopTotalDelay:float = 0
            LOOP_DELAY:float = 0.200
            LOOP_TIMEOUT:float = 1.000
            while True:
            
                # get Spotify server time value.
                response = session.get(
                    reqUrl, 
                    headers=reqHeaders, 
                    allow_redirects=False,
                    )

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
                _logsi.LogObject(SILevel.Debug, "%s http response [%s-%s] (response)" % (tracePrefix, response.status_code, response.reason), response)
                if (response.headers):
                    _logsi.LogCollection(SILevel.Debug, "%s http response [%s-%s] (headers)" % (tracePrefix, response.status_code, response.reason), response.headers.items())

            # if successful request, then process response; otherwise, it's an exception.
            if (response.status_code == 200):
                _logsi.LogVerbose("Spotify TOTP server time request was successful within %f seconds from initial request; processing results" % (loopTotalDelay))
            else:
                raise SpotifyApiError("Spotify TOTP Server Time request failed: %s - %s" % (response.status_code, response.reason), None, logsi=_logsi)

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

            # parse server time value; if not found, then it's an error.
            serverTimeSeconds:int = responseData.get("serverTime", None);
            if (serverTimeSeconds == None):
                raise SpotifyApiError("Spotify TOTP server time response was not recognized: \"%s\"" % (str(data)), None, logsi=_logsi)

            # trace.
            _logsi.LogVerbose("Spotify TOTP server time value = \"%s\"" % (serverTimeSeconds))

            # create TOTP instance.
            totp:TOTP = TOTP(
                secretBase32,
                digest="SHA1",
                digits=6,
                interval=30,
            )

            # return TOTP related variables to caller.
            return totp, serverTimeSeconds

        except Exception as ex:
            
            # trace.
            raise SpotifyApiError("Could not get Spotify Web Player TOTP value", ex, logsi=_logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def Base32FromBytes(self, inputBytes:bytes, secretSauce:str) -> str:
        """
        Converts an array of bytes to a base32 string value.

        Args:
            inputBytes (bytearray):
                Array of bytes to convert to Base32.
            secretSauce (str):
                Characters allowed in the generated base32 string value.

        Returns:
            A generated base32 string value.
        """

        t:int = 0  # This will store the number of bits processed
        n:int = 0  # This will store the accumulated bits
        result:str = ""  # This will store the resulting base32 string

        for byte in inputBytes:

            # shift accumulated bits to the left and add the current byte.
            n = (n << 8) | byte
            t += 8

            # while we have more than 5 bits, we process them.
            while t >= 5:
                # extract 5 bits and append the corresponding character from secret sauce.
                result += secretSauce[(n >> (t - 5)) & 31]
                t -= 5

        # if there are any remaining bits, process them.
        if t > 0:
            result += secretSauce[(n << (5 - t)) & 31]

        # return result to caller.
        return result


    def CleanBuffer(self, value:str) -> bytes:
        """
        Converts a displayable hex string value to a bytes object.

        Args:
            value (str):
                Input value in displayable hex format (e.g. "0140FF").

        Returns:
            A bytes object that contains the converted `value` contents.
        """

        # create a list of zeroes of length half the size of input value.
        result:bytes = [0] * (len(value) // 2)
    
        # convert the hexadecimal pairs to integers.
        for idx in range(0, len(value), 2):
            result[idx // 2] = int(value[idx:idx+2], 16)
    
        # return result to caller.
        return bytes(result)


