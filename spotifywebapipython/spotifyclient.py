# external package imports.
import base64
from datetime import datetime
import json
from io import BytesIO
from platform import architecture
from ssl import ALERT_DESCRIPTION_ACCESS_DENIED
from oauthlib.oauth2 import BackendApplicationClient, WebApplicationClient
import random
from soco import SoCo
from soco.core import (
    PLAY_MODE_BY_MEANING as SONOS_PLAY_MODE_BY_MEANING,
)
from soco.plugins.sharelink import ShareLinkPlugin
import time
import threading
from typing import Tuple, Callable, Union
from urllib3 import PoolManager, Timeout, HTTPResponse
from urllib.parse import urlencode
import urllib.parse
from lxml.etree import fromstring, Element
from lxml import etree
from zeroconf import Zeroconf

# our package imports.
from .oauthcli import AuthClient
from .vibrant import Vibrant, Palette
from .models import *
from .models import UserProfile as UserProfileCurrentUser
from .spotifyconnect import SpotifyConnectDirectoryTask, SpotifyConnectDeviceNotFound
from .saappmessages import SAAppMessages
from .spotifyapierror import SpotifyApiError
from .spotifyapimessage import SpotifyApiMessage
from .spotifyauthtoken import SpotifyAuthToken
from .spotifymediatypes import SpotifyMediaTypes
from .spotifywebapiauthenticationerror import SpotifyWebApiAuthenticationError
from .spotifywebapierror import SpotifyWebApiError
from .spotifywebplayertoken import SpotifyWebPlayerToken
from .zeroconfapi.zeroconfconnect import ZeroconfConnect, ZeroconfGetInfo, ZeroconfResponse, SpotifyZeroconfApiError
from .sautils import (
    _xmlGetInnerText, 
    export, 
    GetUnixTimestampMSFromUtcNow, 
    mediaPositionHMS_fromSeconds,
    mediaPositionHMS_toSeconds,
    validateDelay
)
from .const import (
    SPOTIFY_API_AUTHORIZE_URL,
    SPOTIFY_API_TOKEN_URL,
    SPOTIFY_DESKTOP_APP_CLIENT_ID,
    SPOTIFY_DEFAULT_MARKET,
    SPOTIFY_WEBAPI_URL_BASE,
    SPOTIFYWEBAPIPYTHON_TOKEN_CACHE_FILE,
    TRACE_METHOD_RESULT,
    TRACE_METHOD_RESULT_TYPE,
    TRACE_METHOD_RESULT_TYPE_CACHED,
    TRACE_METHOD_RESULT_TYPE_PAGE,
    TRACE_MSG_AUTHTOKEN_CREATE,
    TRACE_MSG_AUTOPAGING_NEXT,
    TRACE_MSG_DELAY_DEVICE,
    TRACE_MSG_DELAY_DEVICE_SONOS,
    TRACE_MSG_USERPROFILE,
    TRACE_WARN_SPOTIFY_SEARCH_NO_MARKET,
    VERSION
)

CACHE_SOURCE_CACHED:str = "cached"
CACHE_SOURCE_CURRENT:str = "current"

DELAY_DISCONNECT:float = 0.350
"""
Time to wait after a Spotify Connect Disconnect command is issued (350ms).
"""

SPOTIFY_DJ_PLAYLIST_ID = "37i9dqzf1eykqdzj48dyyq"

SPOTIFY_ONLINE_LINK_PREFIX = "https://open.spotify.com"

# get smartinspect logger reference; create a new session for this module name.
from smartinspectpython.siauto import SIAuto, SILevel, SISession, SIMethodParmListContext, SISourceId, SIColors
import logging
_logsi:SISession = SIAuto.Si.GetSession(__name__)
if (_logsi == None):
    _logsi = SIAuto.Si.AddSession(__name__, True)
_logsi.SystemLogger = logging.getLogger(__name__)


@export
class SpotifyClient:
    """
    The SpotifyClient uses the Spotify Web API to retrieve information from the
    Spotify music service.
    """

    SpotifyApiAuthorizeUrl = SPOTIFY_API_AUTHORIZE_URL
    """ Url used to request user authorization permission for an authorization token. """
    
    SpotifyApiTokenUrl = SPOTIFY_API_TOKEN_URL
    """ Url used to request or renew a Spotify authorization token. """
    
    SpotifyWebApiUrlBase = SPOTIFY_WEBAPI_URL_BASE
    """ Url base name used to access tthe Spotify Web API. """
    
    
    def __init__(
        self, 
        manager:PoolManager=None,
        tokenStorageDir:str=None,
        tokenStorageFile:str=None,
        tokenUpdater:Callable=None,
        zeroconfClient:Zeroconf=None,
        spotifyConnectUsername:str=None,
        spotifyConnectPassword:str=None,
        spotifyConnectLoginId:str=None,
        spotifyConnectDiscoveryTimeout:float=2.0,
        spotifyConnectDirectoryEnabled:bool=True,
        spotifyWebPlayerCookieSpdc:str=None,
        spotifyWebPlayerCookieSpkey:str=None,
        ) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            manager (urllib3.PoolManager):
                The manager for HTTP requests to the device.
            tokenStorageDir (str):
                The directory path that will contain the authorization Token Cache file.  
                A null value will default to the platform specific storage location:  
                Example for Windows OS = `C:\\ProgramData\\SpotifyWebApiPython`
            tokenStorageFile (str):
                The filename and extension of the authorization Token Cache file.  
                Default is `SpotifyWebApiPython_tokens.json`.
            tokenUpdater (Callable):
                A method to call when a token needs to be refreshed by an external provider.  
                The defined method is called with no parameters, and should return a token dictionary.  
                Default is null.  
            zeroconfClient (Zeroconf)
                A Zeroconf client instance that will be used to discover Spotify Connect devices,
                or null to create a new instance of Zeroconf.
                Default is null.
            spotifyConnectUsername (str):
                Spotify Connect user name used to login to a Spotify Connect device.
                This MUST match the account name (or one of them) that was used to configure Spotify Connect 
                on a manufacturer device.               
            spotifyConnectPassword (str):
                Spotify Connect password used to login to a Spotify Connect device.
                This value is required if a non-null value was specified for the `spotifyConnectUsername` argument.
            spotifyConnectLoginId (str):
                Spotify Connect login id to login with (e.g. "31l77fd87g8h9j00k89f07jf87ge").  
                This is also known as the canonical user id value.  
                This MUST be the value that relates to the `spotifyConnectUsername` argument.  
            spotifyConnectDiscoveryTimeout (float):
                Maximum amount of time to wait (in seconds) for the Spotify Connect discovery to complete.  
                Specify a value of zero (0) to disable Spotify Connect Zeroconf browsing features.
                Default is 2 seconds.
            spotifyConnectDirectoryEnabled (bool):
                True to enable the Spotify Connect Directory task features.
                otherwise, False to disable the Directory.
                Default is True.
            spotifyWebPlayerCookieSpdc (str):
                Spotify Web Player Cookie credentials `sp_dc` value.  
            spotifyWebPlayerCookieSpkey (str):
                Spotify Web Player Cookie credentials `sp_key` value.
                
        The `spotifyConnectUsername`, `spotifyConnectPassword` and `spotifyConnectLoginId` arguments are only used
        when a Spotify Connect account switch is performed on a selected player device.  Note that these credentials
        are NOT used to access the Spotify Web API (the Spotify Web API token is used for that).  
        Please see the `GetSpotifyConnectDevice` method for more details.  
        
        Note that if you don't have a password setup for your Spotify account (e.g. you utilize the "Continue with Google" 
        or other non-password methods for login), then you will need to define a "device password" in order to use the 
        ZeroConf Connect service; use the [Spotify Set Device Password](https://www.spotify.com/uk/account/set-device-password/) 
        page to define a device password.  You will then use your Spotify username and the device password as your 
        Spotify Connect credentials.

        If the Spotify Connect Directory task Zeroconf feature is disabled (e.g. `spotifyConnectDiscoveryTimeout=0`), then the
        various player functions that utilize Spotify Connect device entries will fail (e.g. PlayerTransferPlayback, etc) if
        the device does not appear in the Spotify Web API player device list.  Chromecast devices will also fail to start, as
        they are controlled via Zeroconf functionality.

        If the Spotify Connect Directory task is disabled (e.g. `spotifyConnectDirectoryEnabled=False`), then the
        various player functions that utilize Spotify Connect device entries will fail (e.g. PlayerTransferPlayback, etc)
        since Spotify Connect devices are not being tracked.  It is recommended that you disable the Directory task if
        you only wish to access methods that retrieve Spotify catalog information, as it speeds up the startup time of the
        client initialization and does not consume extra resources.

        If the `spotifyWebPlayerCookieSpdc` and `spotifyWebPlayerCookieSpkey` argument values are specified, then an
        "elevated" access token (created from the argument values) will be used for all player-control related methods.
        This will give the endpoints the same access that the Spotify Web Player has.
        """
        # validations.
        if zeroconfClient is not None and (not isinstance(zeroconfClient, Zeroconf)):
            raise SpotifyApiError(SAAppMessages.ARGUMENT_TYPE_ERROR % ("__init__", 'zeroconfClient', 'Zeroconf', type(zeroconfClient).__name__), logsi=_logsi)
        if (not isinstance(spotifyConnectDirectoryEnabled, bool)):
            spotifyConnectDirectoryEnabled = True

        # timeout value needs to be a float.
        if (spotifyConnectDiscoveryTimeout is None):
            spotifyConnectDiscoveryTimeout = 2.0
        if (not isinstance(spotifyConnectDiscoveryTimeout, int) and (not isinstance(spotifyConnectDiscoveryTimeout, float))):
            spotifyConnectDiscoveryTimeout = 2.0

        # password is required if username was specified.
        if spotifyConnectUsername is not None:
            if (spotifyConnectPassword is None) or (not isinstance(spotifyConnectPassword,str)):
                raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % ("__init__", 'spotifyConnectPassword'), logsi=_logsi)

        # verify token storage filename was specified.
        if tokenStorageFile is None:
            tokenStorageFile = SPOTIFYWEBAPIPYTHON_TOKEN_CACHE_FILE

        # initialize storage.
        self._AuthToken:SpotifyAuthToken = None
        self._AuthClient:AuthClient = None
        self._ConfigurationCache:dict = {}
        self._DefaultDeviceId:str = None
        self._HasSpotifyWebPlayerCredentials:bool = False
        self._IsDisposed:bool = False
        self._Manager:PoolManager = manager
        self._PlayerLastPlayedInfo:PlayerLastPlayedInfo = PlayerLastPlayedInfo()
        self._SpotifyConnectUsername:str = spotifyConnectUsername
        self._SpotifyConnectPassword:str = spotifyConnectPassword
        self._SpotifyConnectLoginId:str = spotifyConnectLoginId
        self._SpotifyConnectDiscoveryTimeout:float = float(spotifyConnectDiscoveryTimeout)
        self._SpotifyConnectDirectory:SpotifyConnectDirectoryTask = None
        self._SpotifyConnectDirectoryEnabled:bool = spotifyConnectDirectoryEnabled
        self._SpotifyWebPlayerCookieSpdc:str = spotifyWebPlayerCookieSpdc
        self._SpotifyWebPlayerCookieSpkey:str = spotifyWebPlayerCookieSpkey
        self._SpotifyWebPlayerToken:SpotifyWebPlayerToken = None
        self._SpotifyWebPlayerToken_RLock:threading.RLock = threading.RLock()
        self._TokenStorageDir:str = tokenStorageDir
        self._TokenStorageFile:str = tokenStorageFile
        self._TokenUpdater:Callable = tokenUpdater
        self._UserProfile:UserProfile = None
        self._ZeroconfClient = zeroconfClient
        
        # if pool manager instance is none or not a PoolManager instance, then create one.
        # we increase the maximum number of connections to keep in the pool (maxsize=) to avoid the following warnings:
        # "WARNING:urllib3.connectionpool:Connection pool is full, discarding connection: x.x.x.x. Connection pool size: 1"
        if (manager is None) or (not isinstance(manager,PoolManager)):

            # create new pool manager with specified timeouts and limits.
            timeout = Timeout(connect=float(30), read=None)
            self._Manager = PoolManager(headers={'User-Agent': 'SpotifyApiPython/1.0.0'},
                                        timeout=timeout,
                                        num_pools=10,   # number of connection pools to allocate.
                                        maxsize=30,     # maximum number of connections to keep in the pool.
                                        block=True      # limit number of connections to the device.
                                        )

        # create the zeroconf client if one was not specified.
        if zeroconfClient is None:
            _logsi.LogVerbose("Creating new Zeroconf instance for discovery")
            self._ZeroconfClient = Zeroconf()
        else:
            _logsi.LogObject(SILevel.Verbose, "Using existing Zeroconf instance for discovery", zeroconfClient)

        
    # Destructor 
    def __del__(self): 
        """
        Finalizes the instance of the class.
        """
        try:
            self.Dispose()
        except:
            # ignore exceptions since we are shutting down.
            pass
    
        
    def __enter__(self) -> 'SpotifyClient':
        # if called via a context manager (e.g. "with" statement).
        return self


    def __exit__(self, etype, value, traceback) -> None:
        # if called via a context manager (e.g. "with" statement).
        try:
            self.Dispose()
        except:
            # ignore exceptions since we are shutting down.
            pass
    

    def __getitem__(self, key:str):
        if key in self._ConfigurationCache:
            return self._ConfigurationCache[key]


    def __setitem__(self, key, value):
        if not isinstance(key, str):
            key = str(key)
        self._ConfigurationCache[key] = value


    def __iter__(self):
        return iter(self._ConfigurationCache)


    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def ConfigurationCache(self) -> dict:
        """ 
        A dictionary of cached configuration objects that have been obtained from
        the spotify web api.  Use the objects in this cache whenever it is too
        expensive or time consuming to make a real-time request from the spotify web api.

        The configuration cache is updated for selected "Get...()" methods that return
        device information.  All of the selected "Get...()" methods have a `refresh:bool`
        argument that controls where information is obtained from; if refresh=True,
        then the spotify web api is queried for real-time configuration information. If
        refresh=False, then the configuration information is pulled from the configuration
        cache dictionary; if the cache does not contain the object, then the spotify web api
        is queried for real-time configuration information.
        
        It is obviously MUCH faster to retrieve configuration objects from the cache than
        from real-time spotify web api queries.  This works very well for configuration
        objects that do not change very often (e.g. Devices, Categories, Markets, etc).
        You will still want to make real-time queries for configuration objects
        that change frequently (e.g. PlayerPlayState, PlayHistory, etc).
        
        This property is read-only, and is set when the class is instantiated.  The
        dictionary entries can be changed, but not the dictionary itself.

        Returns:
            The `_ConfigurationCache` property value.
        """
        return self._ConfigurationCache
    

    @property
    def AuthToken(self) -> SpotifyAuthToken:
        """ 
        Authorization token used to access the Spotify Web API.  
        """
        return self._AuthToken
    

    @property
    def ClientId(self) -> str:
        """
        The unique identifier of the application.
        
        Returns:
            The ClientId of the AuthClient instance if set; otherwise, null.
        """
        if self._AuthClient is not None:
            return self._AuthClient.ClientId
        return None


    @property
    def DefaultDeviceId(self):
        """
        Default device id (or name) to use for player transport methods that do not specify a device id and 
        there is no active player detected (e.g. "Office", "5d4931f9d0684b625d702eaa24137b2c1d99539c", etc).  
        
        Set this value to null to use the Spotify player active device.
        """
        return self._DefaultDeviceId

    @DefaultDeviceId.setter
    def DefaultDeviceId(self, value:str):
        """ 
        Sets the DefaultDeviceId property value.
        """
        if (value is None):
            
            self._DefaultDeviceId = value
            
        elif (isinstance(value,str)):
            
            if value.strip() == '':
                self._DefaultDeviceId = None
            else:
                self._DefaultDeviceId = value


    @property
    def HasSpotifyWebPlayerCredentials(self) -> bool:
        """ 
        Returns true if Spotify Web Player credentials have been configured for the current 
        UserProfile loginid; otherwise, False.
        """
        return self._HasSpotifyWebPlayerCredentials
    

    @property
    def SpotifyConnectDirectoryEnabled(self) -> bool:
        """ 
        Returns true if the Spotify Connect Directory is active and tracking Zeroconf
        Spotify Connect devices; otherwise, false.
        """
        return self._SpotifyConnectDirectoryEnabled
    

    @property
    def Manager(self) -> PoolManager:
        """ 
        The request PoolManager object to use for http requests to the Spotify Web API.
        
        Returns:
            The `Manager` property value.
        """
        return self._Manager
    

    @property
    def PlayerLastPlayedInfo(self) -> PlayerLastPlayedInfo:
        """
        Contains information about the content that was last playing on the Spotify Player,
        including context, item (track / episode), progress, and active device.
        
        Returns:
            A PlayerLastPlayedInfo object.
        """
        if (self._PlayerLastPlayedInfo is not None):
            return self._PlayerLastPlayedInfo
        return PlayerLastPlayedInfo()


    @property
    def SpotifyConnectDirectory(self) -> SpotifyConnectDirectoryTask:
        """ 
        Spotify Connect Directory task is used to discover Spotify Connect devices, as well
        as maintain the active device list.
        """
        return self._SpotifyConnectDirectory
    

    @property
    def SpotifyConnectLoginId(self) -> str:
        """ 
        Spotify Connect login id to login with (e.g. "31l77fd87g8h9j00k89f07jf87ge").  

        This is also known as the canonical user id value.  
        This MUST be the value that relates to the `SpotifyConnectUsername` property.  
        """
        return self._SpotifyConnectLoginId
    

    @property
    def SpotifyConnectUsername(self) -> str:
        """ 
        Spotify Connect user name used to login to a Spotify Connect device.  

        This MUST match the account name (or one of them) that was used to configure Spotify Connect 
        on a manufacturer device.               
        """
        return self._SpotifyConnectUsername
    

    @property
    def SpotifyWebPlayerCookieSpdc(self) -> str:
        """ 
        Spotify Web Player Cookie credentials `sp_dc` value used to create an elevated access token
        for accessing Spotify Web API services related to the player.
        """
        return self._SpotifyWebPlayerCookieSpdc
    

    @property
    def SpotifyWebPlayerCookieSpkey(self) -> str:
        """ 
        Spotify Web Player Cookie credentials `sp_key` value used to create an elevated access token
        for accessing Spotify Web API services related to the player.
        """
        return self._SpotifyWebPlayerCookieSpkey
    

    @property
    def TokenProfileId(self) -> str:
        """
        Profile identifier used when loading / storing an authorization token from / to disk.
        
        Returns:
            The TokenProfileId of the AuthClient instance if set; otherwise, null.
        """
        if self._AuthClient is not None:
            return self._AuthClient.TokenProfileId
        return None


    @property
    def TokenStorageDir(self) -> str:
        """ 
        The directory path that will contain the authorization token cache file.  
        """
        return self._TokenStorageDir
    

    @property
    def TokenStorageFile(self) -> str:
        """ 
        The filename and extension of the authorization token cache file.  
        """
        return self._TokenStorageFile
    

    @property
    def UserProfile(self) -> UserProfile:
        """ 
        Information about the user from their account profile.
        
        This information is only populated for authorized access types; furthermore, some 
        properties may not be populated if the appropriate scope(s) was not specified when
        the access token was created.  Please refer to the `UserProfile` model for the
        properties that require specific scope.
        """
        return self._UserProfile
    

    @property
    def Version(self) -> str:
        """ 
        The current API version identifier.
        """
        return VERSION
    

    @property
    def ZeroconfClient(self) -> Zeroconf:
        """ 
        Zeroconf client instance that will be used to discover Spotify Connect devices.
        """
        return self._ZeroconfClient
    

    def _CheckForDeviceNotFound(
        self,
        scDevice:SpotifyConnectDevice,
        deviceId:str,
        ) -> None:
        """
        Called to raise a SpotifyConnectDeviceNotFound exception when a Spotify Connect 
        device could not be found and there is no active player.
        """
        # was a device resolved?
        if (scDevice is None):

            # if deviceId could not be resolved, then it's an error.
            if (deviceId is None) or (deviceId == "*"):
                raise SpotifyConnectDeviceNotFound("There is no active Spotify player device, and a default player device was not configured.", logsi=_logsi)
            else:
                raise SpotifyConnectDeviceNotFound("Spotify Player device \"%s\" was not found in the Spotify Connect device list; verify the device is discoverable via Zeroconf on the local network." % (deviceId), logsi=_logsi)


    def _CheckForNextPageWithOffset(
        self, 
        pageObj:PageObject,
        resultItemsCount,
        limit:int,
        limitTotal:int,
        urlParms:dict,
        ) -> bool:
        """
        Modifies paging object and urlParms to point to the next page of data using
        an offset value, if one can be accessed.
        
        Returns:
            False if there are no more pages to process;
            otherwise, True to safely process the next page of results.
        """
        # anymore page results?  
        if (pageObj.Next is None) or (resultItemsCount >= limitTotal) or (pageObj.Offset >= limitTotal):
            # no - all pages were processed, or limit total reached.
            return False
        else:
            # yes - prepare to retrieve the next page of results.
            # if next page potential item count exceeds limit total, then limit to the difference.
            pageObj.Offset = pageObj.Offset + pageObj.Limit
            if (pageObj.Offset + pageObj.Limit) > limitTotal:
                pageObj.Limit = limitTotal - pageObj.Offset
                
                # the following can occur if the Spotify Web API does not return any items but has
                # the 'next' value set to point to the next page of data.  I noticed this happens
                # when the API cannot resolve a market (or country code) value (e.g. the UserProfile
                # Country property is not set and no market argument was supplied).  Regardless, we
                # will check for it here in case.
                if pageObj.Limit <= 0:
                    pageObj.Limit = limit

        # modify paging-related request parameters for next page of items.
        urlParms['limit'] = pageObj.Limit
        urlParms['offset'] = pageObj.Offset
                        
        # trace.
        _logsi.LogVerbose(TRACE_MSG_AUTOPAGING_NEXT % pageObj.PagingInfo)
    
        # indicate next page can be processed.
        return True
    

    def _CheckForNextPageWithCursor(
        self, 
        pageObj:PageObject,
        resultItemsCount,
        limit:int,
        limitTotal:int,
        urlParms:dict,
        ) -> bool:
        """
        Modifies paging object and urlParms to point to the next page of data using
        a cursor value, if one can be accessed.
        
        Returns:
            False if there are no more pages to process;
            otherwise, True to safely process the next page of results.
        """
        # anymore page results for non-cursor paging types?  
        if (pageObj.Next is None) or (resultItemsCount >= limitTotal):
            # no - all pages were processed, or limit total reached.
            return False
        
        # anymore page results for cursor paging types?  
        if (pageObj.IsCursor and pageObj.CursorAfter is None and pageObj.CursorBefore is None) \
        or (resultItemsCount >= limitTotal):
            # no - all pages were processed, or limit total reached.
            return False

        # modify paging-related request parameters for next page of items.
        urlParms['limit'] = pageObj.Limit
        if urlParms.get('after') is not None:
            urlParms['after'] = pageObj.CursorAfter
        else:
            urlParms['before'] = pageObj.CursorBefore

        # just in case spotify doesn't return what is expected, and to prevent
        # an endless loop
        if pageObj.ItemsCount == 0:
            return False
                        
        # trace.
        _logsi.LogVerbose(TRACE_MSG_AUTOPAGING_NEXT % pageObj.PagingInfo)

        # indicate next page can be processed.
        return True
    

    def _CheckResponseForErrors(
        self, 
        msg:SpotifyApiMessage, 
        response:HTTPResponse
        ) -> None:
        """
        Checks the Spotify Web API response for errors.  
        
        If no errors were found, then the request response data is converted to a JSON dictionary 
        and stored in the message request.
        
        If an error result is found, then a `SpotifyWebApiError` or `SpotifyWebApiAuthenticationError` 
        is raised to inform the user of the error.
        
        Args:
            msg (SpotifyApiMessage):
                The Api Message object that represents the request and the response.
            response (Response): 
                Spotify Web API http response object.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyWebApiAuthenticationError: 
                If the Spotify Web API the request was for a authorization service 
                and the response contains error information.               
        """
        responseData:dict = None
        responseUTF8:str = None
        contentType:str = None
        
        try:

            # trace.
            if _logsi.IsOn(SILevel.Debug):
                _logsi.LogObject(SILevel.Debug, 'SpotifyClient http response object - type="%s", module="%s"' % (type(response).__name__, type(response).__module__), response)

            # safely get the response url value.
            # for some reason, the 'url' attribute is not present sometimes if a redirect occurs on the request.
            responseUrl:str = None
            if hasattr(response, 'url'):
                responseUrl = response.url
            elif hasattr(response, '_request_url'):
                #_logsi.LogObject(SILevel.Debug, 'HTTPResponse does not contain a "url" attribute - using "_request_url" instead', response)
                responseUrl = response._request_url
            else:
                #_logsi.LogObject(SILevel.Debug, 'HTTPResponse does not contain a "url" nor "_request_url" attribute - using "geturl()" instead', response)
                try:
                    responseUrl = response.geturl()
                except Exception:
                    _logsi.LogWarning('HTTPResponse method "geturl()" could not be called - defaulting to "unknown response url"')
                    responseUrl = 'Unknown response url'
                
            # trace.
            if _logsi.IsOn(SILevel.Debug):
                _logsi.LogObject(SILevel.Debug, "SpotifyClient http response [%s-%s]: '%s' (response)" % (response.status, response.reason, responseUrl), response)
                if (response.headers):
                    _logsi.LogCollection(SILevel.Debug, "SpotifyClient http response [%s-%s]: '%s' (headers)" % (response.status, response.reason, responseUrl), response.headers.items())

            if response.data is not None:
                
                # do response headers contain a content-type value?
                # if so, we will use it to determine how to convert the response data.
                if response.headers:
                    if 'content-type' in response.headers:
                        contentType = response.headers['content-type']

                # do we have response data?
                if len(response.data) == 0:
                    
                    # some requests will not return a response, which is ok.
                    responseData = None
                    _logsi.LogVerbose("SpotifyClient http response [%s-%s]: '%s' (no data)" % (response.status, response.reason, responseUrl))

                elif (contentType is not None) and (contentType.find('json') > -1):
                    
                    # response is json.
                    # do not use the "response.json()" method to parse JSON responses, as it is unreliable!
                    data = response.data.decode('utf-8')
                    responseData = json.loads(data)
                    
                    if _logsi.IsOn(SILevel.Verbose):
                        if isinstance(responseData, dict):
                            _logsi.LogDictionary(SILevel.Verbose, "SpotifyClient http response [%s-%s]: '%s' (json dict)" % (response.status, response.reason, responseUrl), responseData)
                        elif isinstance(responseData, list):
                            _logsi.LogArray(SILevel.Verbose, "SpotifyClient http response [%s-%s]: '%s' (json array)" % (response.status, response.reason, responseUrl), responseData)
                        else:
                            _logsi.LogObject(SILevel.Verbose, "SpotifyClient http response [%s-%s]: '%s' (json object)" % (response.status, response.reason, responseUrl), responseData)
                    
                else:
                    
                    # no - treat it as utf-8 encoded data.
                    responseUTF8 = response.data.decode('utf-8')
                    _logsi.LogText(SILevel.Error, "SpotifyClient http response [%s-%s]: '%s' (utf-8)" % (response.status, response.reason, responseUrl), responseUTF8)
                    responseData = responseUTF8

        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            _logsi.LogException("SpotifyClient http response could not be converted to JSON and will be converted to utf-8.\nConversion exception returned was:\n{ex}".format(ex=str(ex)), ex, logToSystemLogger=False)

            # if json conversion failed, then convert to utf-8 response.
            if response.data is not None:
                responseUTF8 = response.data.decode('utf-8')
                _logsi.LogText(SILevel.Error, "SpotifyClient http response [%s-%s]: '%s' (utf-8)" % (response.status, response.reason, responseUrl), responseUTF8)
            
            # at this point we don't know what Spotify Web Api returned, so let's 
            # just raise a new exception with the non-JSON response data.
            raise SpotifyWebApiError(response.status, responseUTF8, msg.MethodName, response.reason, _logsi)
            
        CONST_ERROR:str = 'error'
        CONST_ERROR_DESCRIPTION:str = 'error_description'
        CONST_MESSAGE:str = 'message'
        CONST_STATUS:str = 'status'
        
        errCode:str = None
        errMessage:str = None
        
        if responseData is None:
            
            # if response is not in the 2xx range then it's an error, even
            # though no json 'error' response body was returned!  this is
            # usually due to a '405 - method not allowed' or '403-Forbidden' response.
            if response.status > 299:
                
                errCode = response.status
                errMessage = response.reason
                
                if responseUTF8 is not None:
                    errMessage = responseUTF8

                raise SpotifyWebApiError(errCode, errMessage, msg.MethodName, response.reason, _logsi)
            
        elif responseData is not None:
            
            # if response is a string (e.g. html response) and is not in the 2xx range then 
            # we will assume it's an error, even though no json 'error' response body was returned!  
            # this is usually due to a '503 Server Error' response.
            if (response.status > 299) and (isinstance(responseData, str)):

                errCode = response.status
                errMessage = response.reason
                
                if responseUTF8 is not None:
                    errMessage = responseUTF8

                raise SpotifyWebApiError(errCode, errMessage, msg.MethodName, response.reason, _logsi)
            
            # does json response contain error details?
            if CONST_ERROR in responseData:
                
                # what type of error: authorization, or regular?
                errObj = responseData[CONST_ERROR]
                if isinstance(errObj, dict):
                    
                    # errObj is a dictionary in this case.
                    if CONST_STATUS in errObj:
                        errCode = errObj[CONST_STATUS]
                    if CONST_MESSAGE in errObj:
                        errMessage = errObj[CONST_MESSAGE]
                        
                    if errCode is None:
                        errCode = response.status
                        
                    if (not msg.IgnoreResponseErrors):
                        raise SpotifyWebApiError(errCode, errMessage, msg.MethodName, response.reason, _logsi)

                elif isinstance(errObj, str):
                    
                    # errObj is a string in this case.
                    errCode = errObj
                    if CONST_ERROR_DESCRIPTION in responseData:
                        errMessage = responseData[CONST_ERROR_DESCRIPTION]

                    raise SpotifyWebApiAuthenticationError(errCode, errMessage, msg.MethodName, response.status, response.reason, _logsi)

        # no errors found - set message object response data.
        msg.ResponseData = responseData


    def _GetSpotifyWebPlayerTokenHeaderValue(
        self,
        scDevice:SpotifyConnectDevice=None,
        ) -> str:
        """
        Retrieves a SpotifyWebPlayer token header value, if Spotify Web Player cookie credentials 
        are defined.

        Args:
            scDevice (SpotifyConnectDevice):
                A resolved SpotifyConnectDevice object.

        Returns:
            A token header value that can be used in the request header authorization variable;
            otherwise, None.

        The value returned will be a `Bearer: token` string that can be used in a request header 
        authorization key for Spotify Web API endpoints that start playback on a device.

        Credentials can be specified via the class constructor, or in the Token Cache File.  

        The class constructor `spotifyWebPlayerCookieSpdc` and `spotifyWebPlayerCookieSpkey`
        arguments are the easiest way to specify the values, as it eliminates JSON formatting errors.  

        The Token Cache File is queried for a key value of "SpotifyWebPlayerCookieCredentials/Shared/YOUR_SPOTIFY_LOGIN_ID",
        which will contain the `sp_key` and `sp_dc` values of the cookie credentials.  

        The credentials are then converted into an authorization access token which is used by 
        Spotify Web API endpoints.
        """
        # are spotify web player credentials configured? if not, then don't bother!
        if (not self._HasSpotifyWebPlayerCredentials):
            return None

        # make the following thread-safe, so we don't retrieve multiple tokens.
        with self._SpotifyWebPlayerToken_RLock:

            # if token already retrieved and has not expired, then use it.
            if (self._SpotifyWebPlayerToken is not None) and (not self._SpotifyWebPlayerToken.IsExpired):
                _logsi.LogVerbose(SAAppMessages.MSG_SPOTIFY_WEB_PLAYER_TOKEN_INUSE, colorValue=SIColors.Gold)
                return self._SpotifyWebPlayerToken.HeaderValue

            # was a device argument passed?  if not, then just refresh the token.
            if (scDevice is None):

                # get spotify web player access token info from spotify web player cookie credentials.
                _logsi.LogVerbose(SAAppMessages.MSG_SPOTIFY_WEB_PLAYER_TOKEN_REFRESHED % (self._SpotifyConnectLoginId), colorValue=SIColors.Gold)
                self._SpotifyWebPlayerToken = SpotifyWebPlayerToken(
                    profileId=self._SpotifyConnectLoginId,
                    tokenStorageDir=self._TokenStorageDir,
                    tokenStorageFile=self._TokenStorageFile,
                    spotifyWebPlayerCookieSpdc=self._SpotifyWebPlayerCookieSpdc,
                    spotifyWebPlayerCookieSpkey=self._SpotifyWebPlayerCookieSpkey)

                if self._SpotifyWebPlayerToken is not None:
                    _logsi.LogVerbose(SAAppMessages.MSG_SPOTIFY_WEB_PLAYER_TOKEN_INUSE, colorValue=SIColors.Gold)
                    return self._SpotifyWebPlayerToken.HeaderValue

            else:

                # was the device resolved? if not, then don't bother!
                if (not isinstance(scDevice, SpotifyConnectDevice)):
                    return None

                # get spotify web player access token info from spotify web player cookie credentials.
                _logsi.LogVerbose(SAAppMessages.MSG_SPOTIFY_WEB_PLAYER_TOKEN_REFRESHED % (self._SpotifyConnectLoginId), colorValue=SIColors.Gold)
                self._SpotifyWebPlayerToken = SpotifyWebPlayerToken(
                    profileId=self._SpotifyConnectLoginId,
                    tokenStorageDir=self._TokenStorageDir,
                    tokenStorageFile=self._TokenStorageFile,
                    spotifyWebPlayerCookieSpdc=self._SpotifyWebPlayerCookieSpdc,
                    spotifyWebPlayerCookieSpkey=self._SpotifyWebPlayerCookieSpkey)

                if self._SpotifyWebPlayerToken is not None:
                    _logsi.LogVerbose(SAAppMessages.MSG_SPOTIFY_WEB_PLAYER_TOKEN_INUSE, colorValue=SIColors.Gold)
                    return self._SpotifyWebPlayerToken.HeaderValue

        # return result to caller.
        return None



    def _ResolveDeviceObject(
        self,
        device:str | SpotifyConnectDevice,
        activateDevice:bool=True,
        ) -> SpotifyConnectDevice:
        """
        Resolves a SpotifyConnectDevice object from a device identifier, name, or 
        SpotifyConnectDevice object argument value.  A null object will be returned
        if the `device` argument could not be resolved.

        Args:
            device (str | SpotifyConnectDevice) | None):
                The target player device identifier.
                This could be an id, name, a default device indicator (e.g. "*"), a 
                SpotifyConnectDevice object, or null to utilize the active player device.
                A device is considered resolved if a SpotifyConnectDevice object is passed
                for this argument.  
                Examples are `0d1841b0976bae2a3a310dd74c0f3df354899bc8`, `Office`, `*`, None.  
            activateDevice (bool):
                True to activate the device if necessary; otherwise, False.  
                Default is True.  

        Returns:
            A SpotifyConnectDevice object for the specified device if found; otherwise, null.

        Raises:
            SpotifyApiError: 
                If `device` could not be resolved to a valid device instance.
                If `device` was resolved, but could not be activated.
                If the method fails for any other reason.

        A device is already considered resolved if a SpotifyConnectDevice object
        is passed for the `device` argument.
        """
        scDevice:SpotifyConnectDevice = None

        # has deviceId been resolved?
        if (isinstance(device, SpotifyConnectDevice)):

            # yes - just return the device object.
            scDevice = device

        else:

            # no - ensure the specified device id / name is active (optional) and 
            # available, and return the SpotifyConnectDevice object.
            # a null object will be returned if the device id could not be found.
            scDevice = self.GetSpotifyConnectDevice(
                device, 
                refreshDeviceList=True, 
                activateDevice=activateDevice)

        return scDevice


    def _RestartSpotifyConnectDirectoryTask(self) -> None:
        """
        Restarts the Spotify Connect Directory task, which is used to 
        maintain a list of Spotify Connect devices on the local network.
        """
        # is the task running?  if so, then stop it.
        if (self._SpotifyConnectDirectory is not None):
            self.StopSpotifyConnectDirectoryTask()

        # start the task.
        self._StartSpotifyConnectDirectoryTask()


    def _StartSpotifyConnectDirectoryTask(self) -> None:
        """
        Starts the Spotify Connect Directory task, which is used to 
        maintain a list of Spotify Connect devices on the local network.
        """
        apiMethodName:str = '_StartSpotifyConnectDirectoryTask'
        
        try:
            
            # trace.
            _logsi.LogVerbose("SpotifyClient is initializing Spotify Connect Directory task")

            # reset has credentials indicator.
            self._HasSpotifyWebPlayerCredentials = False

            # if user profile is not set, then it denotes a token has not been assigned yet!
            # an authorization token MUST be assigned before we can start processing
            # Spotify Connect Directory requests!
            if (self._UserProfile is None):
                raise SpotifyApiError("Authorization token must be set and a user profile established before starting the Spotify Connect Directory task", None, logsi=_logsi)

            # loginId is required in order to activate Spotify Connect devices.
            # if not supplied, then use the value from authorization user profile.
            if (self._SpotifyConnectLoginId is None) or (len(self._SpotifyConnectLoginId.strip()) == 0):
                _logsi.LogVerbose("Spotify Connect LoginId not specified on class constructor; using Spotify UserProfile ID value \"%s\"" % (self._UserProfile.Id), colorValue=SIColors.Coral)
                self._SpotifyConnectLoginId = self._UserProfile.Id

            try:

                # were Spotify Web Player cookie credentials specified on the class constructor?
                if (self._SpotifyWebPlayerCookieSpdc is not None) and (self._SpotifyWebPlayerCookieSpkey is not None):

                    # yes - indicate we have Spotify Web Player cookie credentials.
                    self._HasSpotifyWebPlayerCredentials = True
                    _logsi.LogVerbose("Spotify Web Player cookie credentials were specified on the class constructor")

                else:

                    # no - check if the Spotify Web Player cookie credentials are defined in Token cache File.
                    # Example: SpotifyWebPlayerCookieCredentials/Shared/YOUR_SPOTIFY_LOGIN_ID
                    self._HasSpotifyWebPlayerCredentials = AuthClient.HasTokenForKey(
                        clientId=None,
                        tokenProviderId='SpotifyWebPlayerCookieCredentials',
                        tokenProfileId=self._SpotifyConnectLoginId,
                        tokenStorageDir=self._TokenStorageDir,
                        tokenStorageFile=self._TokenStorageFile,
                    )

                    if (self._HasSpotifyWebPlayerCredentials):
                        _logsi.LogVerbose("Spotify Web Player cookie credentials were specified in the Token Cache File")

                # NOTE: as of 2025/05/12, Spotify removed access to Spotify Web Player Credentials functionality;
                # the `self._HasSpotifyWebPlayerCredentials = False` flag is set here to automatically disable the functionality.
                # I left the code that checks this flag in place elsewhere in case credentials are re-enabled in the future.

                # disable Spotify Web Player Cookie Credentials functionality.
                _logsi.LogVerbose("Spotify Web Player cookie credentials are no longer supported by Spotify as of 2025/05/12!", colorValue=SIColors.Red)
                self._HasSpotifyWebPlayerCredentials = False

            except Exception as ex:

                # could not detect player credentials; assume none.
                self._HasSpotifyWebPlayerCredentials = False

                # ignore exceptions, as transfer will still work.
                pass

            # trace.
            _logsi.LogVerbose("Spotify Connect LoginId \"%s\" HasSpotifyWebPlayerCredentials flag: %s" % (self._SpotifyConnectLoginId, self._HasSpotifyWebPlayerCredentials), colorValue=SIColors.Coral)

            # create new Spotify Connect Directory instance.
            self._SpotifyConnectDirectory = SpotifyConnectDirectoryTask(self, self._ZeroconfClient, self._SpotifyConnectDiscoveryTimeout)
            self._SpotifyConnectDirectory.daemon = True

            # if user profile is a public access user, then there is no user-id associated
            # with the account.  in this case, we will not start the Spotify Connect Directory
            # task since the user cannot access anything related to Spotify Connect.
            if (self._UserProfile.Id is None) or (self._UserProfile.Id == 'unknown'):
                _logsi.LogVerbose("Spotify Connect Directory task will not be started due to public access user token", colorValue=SIColors.Coral)
                return

            # is Spotify Connect Directory task enabled?
            if (not self._SpotifyConnectDirectoryEnabled):
                _logsi.LogVerbose("Spotify Connect Directory task will not be started due to disabled status at initialization", colorValue=SIColors.Coral)
                return

            # is Spotify Connect Directory task Zeroconf browsers enabled?
            if (self._SpotifyConnectDiscoveryTimeout == 0):
                _logsi.LogVerbose("Spotify Connect Zeroconf discovery is disabled; only Spotify Web API player devices will be recognized", colorValue=SIColors.Coral)

            # start the task.
            _logsi.LogVerbose("SpotifyClient is starting Spotify Connect Directory task")
            self._SpotifyConnectDirectory.start()

            # wait for task to fully initialize; when set, this indicates that
            # all zeroconf update threads are active and actively processing
            # Spotify Connect devices on the local network.  
            self._SpotifyConnectDirectory.WaitForInitComplete.wait()

            # trace.
            _logsi.LogVerbose("Spotify Connect Directory task was started and initialized successfully")

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)


    def StopSpotifyConnectDirectoryTask(
        self,
        timeout:float=3.0,
        ) -> None:
        """
        Stops the Spotify Connect Directory task.

        Args:
            timeout (float):
                Time to wait (in seconds) for the task to stop.
        """
        apiMethodName:str = 'StopSpotifyConnectDirectoryTask'
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            _logsi.LogMethodParmList(SILevel.Verbose, "Stopping Spotify Connect Directory task", apiMethodParms)

            # ensure the object exists.
            if (self._SpotifyConnectDirectory is not None):

                # is the task alive?
                if (self._SpotifyConnectDirectory.is_alive()):

                    # yes - inform task we want it to stop.
                    self._SpotifyConnectDirectory.IsStopRequested = True

                    # wait for task to stop.
                    _logsi.LogVerbose("Waiting for Spotify Connect Directory task to stop")
                    self._SpotifyConnectDirectory.join(timeout)

            # trace.
            _logsi.LogVerbose("Spotify Connect Directory task was stopped")

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:

            # release resources.
            self._SpotifyConnectDirectory = None

            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def _ValidateMarket(
        self, 
        market:str,
        forceReturnValue:bool=False,
        ) -> str:
        """
        Validates that a market (aka country code) value has either been supplied, or exists
        in the UserProfile.Country value and returns a value of 'US' if not supplied; otherwise,
        the market aregument value is returned.

        Args:
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
            forceReturnValue (bool):
                Forces a value to be returned, even if one was not supplied in the `market` argument.
                If True, the user profile country value will be returned if `market` argument is None;
                otherwise, the specified market value is returned if it's not Empty String / not None;
                otherwise, a default value of "US" will be returned.

        Some Spotify Web API calls require a `market` value to be specified on the call.
        For example, the GetTrack call will not return `linked_from` attributes if the
        `market` value is not specified on the web request querystring!
        
        If a market argument was not specified and the user profile does not have a country code
        set, then it causes the Spotify Web API search to return odd results.  For example, the
        items collection will return no items, but the `total` and `next` values are populated
        like there are more results.  It's almost like it found the results, but it won't return
        the actual items due to market / country restrictions or something.
        """
        # if we are forcing a return value and a null or empty string was supplied, then
        # return the user profile country value if one was set.
        if forceReturnValue:
            if (market is None) or (len(market.strip()) == 0):
                if (self.UserProfile.Country is not None):
                    return self.UserProfile.Country

        # if a non-null and non-empty string was supplied then assume it's a valid market.
        # we will let the Spotify Web API tell us if it's not a valid code.
        if (market is not None and len(market.strip()) > 0):
            return market

        # if user profile country value was set then just return the market value as-is, since
        # the user profile country code will override it anyway.
        if (self.UserProfile.Country is not None):
            return market

        # otherwise, defult the value.
        _logsi.LogVerbose("A market value was not supplied for the request, and the user profile did not contain a country code value (e.g. public access token is in effect).  Defaulting value to '%s'." % SPOTIFY_DEFAULT_MARKET)
        return SPOTIFY_DEFAULT_MARKET


    def Dispose(self) -> None:
        """
        Releases all resources of this instance.

        This method stops the Spotify Connect Directory task, and ensures
        that any event wirings are removed.
        """
        apiMethodName:str = 'Dispose'

        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            _logsi.LogMethodParmList(SILevel.Verbose, "Disposing of SpotifyClient instance", apiMethodParms)

            # are we already disposed? if so, then don't do it again!
            if (self._IsDisposed == True):
                _logsi.LogVerbose("SpotifyClient instance is already disposed")
                return
            else:
                # indicate we are disposed (or in the process thereof).
                self._IsDisposed = True

            # shut down the directory task.
            try:
                self.StopSpotifyConnectDirectoryTask()
            except Exception as ex:
                pass  # ignore exceptions as they have already been logged.

            # trace.
            _logsi.LogVerbose("Disposal of SpotifyClient instance completed successfully")

        except Exception as ex:
            
            # log unhandled exception.
            _logsi.LogException(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex)

            # ignore exceptions as we are disposing!

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def MakeRequest(
        self, 
        method:str, 
        msg:SpotifyApiMessage
        ) -> int:
        """
        Performs a generic Spotify Web API request.
        
        Args:
            method (str): 
                The preferred HTTP method (e.g. "GET", "POST", etc).
            msg (SpotifyApiMessage): 
                The api message object that contains input parameters and the
                output response.
                
        Returns:
            The status code (integer) or allowed methods (list).

        Raises:
            SpotifyWebApiError: 
                If an error occurs while requesting content.
                
        A 400 status code is immediately returned for the following scenarios:  
        - The method argument is not supplied.  
        - The msg argument is not supplied.  

        Per Spotify Developer Docs, here are the possible status codes:  
        - 200 OK - The request has succeeded. The client can read the result of the request in the body and the headers of the response.  
        - 201 Created - The request has been fulfilled and resulted in a new resource being created.  
        - 202 Accepted - The request has been accepted for processing, but the processing has not been completed.  
        - 204 No Content - The request has succeeded but returns no message body.  
        - 304 Not Modified. See Conditional requests.  
        - 400 Bad Request - The request could not be understood by the server due to malformed syntax. The message body will contain more information; see Response Schema.  
        - 401 Unauthorized - The request requires user authentication or, if the request included authorization credentials, authorization has been refused for those credentials.  
        - 403 Forbidden - The server understood the request, but is refusing to fulfill it.  
        - 404 Not Found - The requested resource could not be found. This error can be due to a temporary or permanent condition.  
        - 429 Too Many Requests - Rate limiting has been applied.  
        - 500 Internal Server Error. You should never receive this error because our clever coders catch them all ... but if you are unlucky enough to get one, please report it to us through a comment at the bottom of this page.  
        - 502 Bad Gateway - The server was acting as a gateway or proxy and received an invalid response from the upstream server.  
        - 503 Service Unavailable - The server is currently unable to handle the request due to a temporary condition which will be alleviated after some delay. You can choose to resend the request again.  
        - 504 Gateway Timeout - The server is currently unable to handle the request due to a temporary condition which will be alleviated after some delay. You can choose to resend the request again.  
        """
        apiMethodName:str = 'MakeRequest'
        apiMethodParms:SIMethodParmListContext = None
        response:HTTPResponse = None
        
        try:
            
            # trace.
            _logsi.EnterMethod(SILevel.Debug, apiMethodName)
            
            # validation.
            if method is None or msg is None or (not isinstance(msg,SpotifyApiMessage)):
                _logsi.LogVerbose("msg argument was not a valid SpotifyApiMessage instance")
                return 400

            # trace.
            apiMethodParms = SIMethodParmListContext(apiMethodName)
            apiMethodParms.AppendKeyValue("method", method)
            apiMethodParms.AppendKeyValue("msg.Uri", msg.Uri)
            apiMethodParms.AppendKeyValue("msg.UrlParameters", msg.UrlParameters)
            apiMethodParms.AppendKeyValue("msg.RequestData", msg.RequestData)
            apiMethodParms.AppendKeyValue("msg.RequestJson", msg.RequestJson)
            _logsi.LogMethodParmList(SILevel.Verbose, "Making HTTPS request to the Spotify Web API", apiMethodParms)
                
            # formulate the request url.
            url:str = None
            uri:str = msg.Uri
            if (uri == self.SpotifyApiTokenUrl) \
            or (uri == self.SpotifyApiAuthorizeUrl) \
            or (uri.startswith('https:')) \
            or (uri.startswith('http:')):
                url = uri
            else:
                url = f'{self.SpotifyWebApiUrlBase}{uri}'

            # is the authorization token expired?
            if self._AuthToken is not None and self._AuthToken.IsExpired:

                # refresh / renew the token.  
                if self._AuthToken.RefreshToken is None:
                    _logsi.LogVerbose("OAuth2 authorization token has expired; token will be renewed")
                    oauth2token:dict = self._AuthClient.FetchToken()
                    self._AuthToken = SpotifyAuthToken(self._AuthToken.AuthorizationType, self._AuthToken.ProfileId, root=oauth2token)
                else:
                    _logsi.LogVerbose("OAuth2 authorization token has expired, or is about to; token will be refreshed")
                    oauth2token:dict = self._AuthClient.RefreshToken()
                    self._AuthToken = SpotifyAuthToken(self._AuthToken.AuthorizationType, self._AuthToken.ProfileId, root=oauth2token)

                _logsi.LogObject(SILevel.Verbose, 'Authorization token was successfully renewed', self._AuthToken, excludeNonPublic=True)
                
                # if message contains an authorization header, then it needs to be updated with the new access token.
                if self._AuthToken.HeaderKey in msg.RequestHeaders:
                    _logsi.LogVerbose('Updating request authorization header value with the renewed token value')
                    msg.RequestHeaders[self._AuthToken.HeaderKey] = self._AuthToken.HeaderValue
                
            # trace.
            if (msg.HasRequestHeaders):
                # msg.RequestHeaders["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.178 Spotify/1.2.62.580 Safari/537.36"
                # msg.RequestHeaders["User-Agent"] = "Spotify/8.9.76 iOS/18.1 (iPhone17,1)"
                # msg.RequestHeaders["Authority"] = "spclient.wg.spotify.com"
                # msg.RequestHeaders["Content-Type"] = "text/plain;charset=UTF-8"
                _logsi.LogCollection(SILevel.Verbose, "SpotifyClient http request: '%s' (headers)" % (url), msg.RequestHeaders.items())

            # *** IMPORTANT ***
            # for HA versions prior to 2025.03:
            # in the logic below, ensure that ALL urllib3.request method calls conform to version 1.26.18.
            # urllib3 version 2.0 is not supported!  see internal developer notes for more details.

            # request retry loop for failed requests that are temporary in nature (504 Gateway Timeout, etc).
            loopTotalDelay:float = 0
            LOOP_DELAY:float = 0.200
            LOOP_TIMEOUT:float = 1.000
            while True:

                # call the appropriate poolmanager request method.
                if msg.HasUrlParameters:
                
                    # add querystring parameters to url; if url already has a partial parm
                    # string (e.g. has a '?xxx=...') then use the append separator (e.g. '...&xxx=...').
                    urlQS:str = urlencode(msg.UrlParameters)
                    urlParmSep:str = '?'
                    if (url.find('?') > 0):
                        urlParmSep = '&'
                    url = url + urlParmSep + urlQS
                
                    _logsi.LogDictionary(SILevel.Verbose, "SpotifyClient http request: '%s' (with urlparms)" % (url), msg.UrlParameters, prettyPrint=True)
                    response = self._Manager.request_encode_url(method, url, headers=msg.RequestHeaders)
                
                elif msg.HasRequestData:

                    if msg.IsRequestDataEncoded:

                        _logsi.LogText(SILevel.Verbose, "SpotifyClient http request: '%s' (with body encoded)" % (url), msg.RequestData)
                        response = self._Manager.request(method, url, body=msg.RequestData, headers=msg.RequestHeaders)
                   
                    else:

                        _logsi.LogDictionary(SILevel.Verbose, "SpotifyClient http request: '%s' (with body)" % (url), msg.RequestData, prettyPrint=True)
                        response = self._Manager.request_encode_body(method, url, fields=msg.RequestData, headers=msg.RequestHeaders, encode_multipart=False)
                                    
                elif msg.HasRequestJson:

                    _logsi.LogDictionary(SILevel.Verbose, "SpotifyClient http request: '%s' (with json body)" % (url), msg.RequestJson, prettyPrint=True)

                    # add content-type=json header and convert the dictionary to json format.
                    if not ("content-type" in map(str.lower, msg.RequestHeaders.keys())):
                        #headers = HTTPHeaderDict(headers)
                        msg.RequestHeaders["Content-Type"] = "application/json"
                    reqBody:str = json.dumps(msg.RequestJson, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
                    _logsi.LogBinary(SILevel.Debug, "SpotifyClient http request JSON body", reqBody)
                    response = self._Manager.request(method, url, body=reqBody, headers=msg.RequestHeaders)
                
                else:

                    _logsi.LogDictionary(SILevel.Verbose, "SpotifyClient http request: '%s' (no body)" % (url), msg.RequestData, prettyPrint=True)
                    response = self._Manager.request(method, url, headers=msg.RequestHeaders)

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
                if (response.status == 504):

                    # only retry so many times before we give up;
                    if (loopTotalDelay >= LOOP_TIMEOUT):
                        raise SpotifyApiError(SAAppMessages.MSG_SPOTIFY_WEB_API_RETRY_TIMEOUT % (loopTotalDelay), None, logsi=_logsi)

                    # trace.
                    _logsi.LogVerbose(SAAppMessages.MSG_SPOTIFY_WEB_API_RETRY_RESPONSE_STATUS % (response.status, response.reason), colorValue=SIColors.Red)

                    # wait just a bit between requests.
                    _logsi.LogVerbose(SAAppMessages.MSG_SPOTIFY_WEB_API_RETRY_REQUEST_DELAY % (LOOP_DELAY))
                    time.sleep(LOOP_DELAY)
                    loopTotalDelay = loopTotalDelay + LOOP_DELAY

                else:

                    # otherwise, break out of retry loop and process response.
                    break

            # process based upon response status code; some requests will not return response data.
            # I know this could have been simplified, but I broke it down into possible return code ranges.
            if response.status >= 200 and response.status <= 299:
                msg.ResponseData = self._CheckResponseForErrors(msg, response)
                    
            elif response.status >= 300 and response.status <= 399:
                msg.ResponseData = self._CheckResponseForErrors(msg, response)
                    
            elif response.status >= 400 and response.status <= 499:
                msg.ResponseData = self._CheckResponseForErrors(msg, response)
                    
            elif response.status >= 500 and response.status <= 599:
                msg.ResponseData = self._CheckResponseForErrors(msg, response)

            else:
                msg.ResponseData = self._CheckResponseForErrors(msg, response)

            # if no exception was thrown by the response check, then return the status code.
            return response.status
        
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
            
            # close the response (if needed).
            if response is not None:
                if response.closed == False:
                    response.close()

            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def AddPlayerQueueItems(
        self, 
        uris:str,
        deviceId:str=None,
        verifyDeviceId:bool=True,
        delay:float=0.15,
        ) -> None:
        """
        Add one or more items to the end of the user's current playback queue. 
        
        This method requires the `user-modify-playback-state` scope.

        Args:
            uris (str):
                A list of Spotify track or episode URIs to add to the queue; can be track or episode URIs.  
                All URIs must be of the same type - you cannot mix and match tracks and episodes!  
                Example: [`spotify:track:6zd8T1PBe9JFHmuVnurdRp` ,`spotify:track:1kWUud3vY5ij5r62zxpTRy`].  
                It can also be specified as a comma-delimited string.  
                Example: `spotify:track:6zd8T1PBe9JFHmuVnurdRp,spotify:track:1kWUud3vY5ij5r62zxpTRy`.  
                An unlimited number of items can be added in one request, but the more items the longer it
                will take.
            deviceId (str | SpotifyConnectDevice) | None):
                The target player device identifier.
                This could be an id, name, a default device indicator (e.g. "*"), a 
                SpotifyConnectDevice object, or null to utilize the active player device.
                A device is considered resolved if a SpotifyConnectDevice object is passed
                for this argument.  An exception will be raised if the argument value could 
                not be resolved or activated.
                Examples are `0d1841b0976bae2a3a310dd74c0f3df354899bc8`, `Office`, `*`, None.  
            verifyDeviceId (bool):
                DEPRECATED - no longer used, but left here to maintain compatibility.
            delay (float):
                Time delay (in seconds) to wait AFTER issuing the add request.  This delay will give the 
                Spotify web api time to process the queue change before another command is issued.  
                Default is 0.15; value range is 0 - 10.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        This API only works for users who have Spotify Premium. 
        
        The order of execution is not guaranteed when you use this API with other Player API endpoints.

        For Sonos devices, items are added to the end of the device local queue.
        For non-Sonos devices, items are added to the end of the user's current playback queue. 
        
        The Spotify Web API endpoint is called to add each item individually.  
        The Spotify Web API does not currently support adding more than 1 item to the queue at a time.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/AddPlayerQueueItems.py
        ```
        </details>
        """
        apiMethodName:str = 'AddPlayerQueueItems'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("uris", uris)
            apiMethodParms.AppendKeyValue("deviceId", deviceId)
            apiMethodParms.AppendKeyValue("verifyDeviceId (DEPRECATED)", verifyDeviceId)
            apiMethodParms.AppendKeyValue("delay", delay)
            _logsi.LogMethodParmList(SILevel.Verbose, "Add items to playback queue", apiMethodParms)
            
            # validations.
            delay = validateDelay(delay, 0.15, 10)

            # build a list of all item uri's.
            # remove any leading / trailing spaces in case user put a space between the items.
            arrUris:list[str] = None
            if isinstance(uris, list):
                arrUris = uris
            else:
                arrUris = uris.split(',')
                for idx in range(0, len(arrUris)):
                    arrUris[idx] = arrUris[idx].strip()
                
            # resolve the device object from the device id.
            scDevice:SpotifyConnectDevice = self._ResolveDeviceObject(deviceId, False)

            # are spotify web player credentials configured? if so, then we will use them to create
            # an elevated authorization access token for the Spotify Web API endpoint call.
            accessTokenHeaderValue:str = self._GetSpotifyWebPlayerTokenHeaderValue(scDevice)

            # is this an active Sonos device?
            # Sonos device can still be active, even if there is no active device in Spotify playstate.
            if (scDevice is not None) and (scDevice.IsSonos) and (accessTokenHeaderValue is None):

                # trace.
                _logsi.LogVerbose("Items will be added to Sonos local queue for device: %s" % (scDevice.Title))

                # get the Sonos Controller player instance.
                sonosPlayer:SoCo = self.SpotifyConnectDirectory.GetSonosPlayer(scDevice)

                # add all track items to the Sonos local queue.
                sharelink = ShareLinkPlugin(sonosPlayer)
                for idx in range(0, len(arrUris)):

                    # add track to the Sonos local queue.
                    uri = arrUris[idx].strip()
                    _logsi.LogVerbose("Issuing command to Sonos device \"%s\": ADD_SHARE_LINK_TO_QUEUE (uri=%s)" % (scDevice.Name, uri))
                    sharelink.add_share_link_to_queue(uri)

            else:

                # was the deviceId resolved? 
                # if not, then raise an exception as the Spotify Web API request will fail anyway.
                self._CheckForDeviceNotFound(scDevice, deviceId)

                # trace.
                _logsi.LogVerbose("Items will be added to playback queue for device: %s" % (scDevice.Title))
                
                # process all uri's.
                for idx in range(0, len(arrUris)):
                
                    # build spotify web api request parameters.
                    urlParms:dict = \
                    {
                        'uri': arrUris[idx]
                    }
                    if (scDevice is not None):
                        urlParms['device_id'] = (scDevice.DeviceIdActivated or scDevice.Id)

                    # execute spotify web api request.
                    msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/player/queue')
                    msg.RequestHeaders[self.AuthToken.HeaderKey] = accessTokenHeaderValue or self.AuthToken.HeaderValue
                    msg.UrlParameters = urlParms
                    self.MakeRequest('POST', msg)

                    # give spotify web api time to process the change.
                    if delay > 0:
                        _logsi.LogVerbose(TRACE_MSG_DELAY_DEVICE % delay)
                        time.sleep(delay)

            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def AddPlaylistCoverImage(
        self, 
        playlistId:str, 
        imagePath:str
        ) -> None:
        """
        Replace the image used to represent a specific playlist.
        
        This method requires the `ugc-image-upload`, `playlist-modify-public` 
        and `playlist-modify-private` scope.
        
        Args:
            playlistId (str):  
                The Spotify ID of the playlist.  
                Example: `5v5ETK9WFXAnGQ3MRubKuE`
            imagePath (str):
                The fully-qualified path of the image to be uploaded.  
                The image must be in JPEG format, and cannot exceed 256KB in Base64 encoded size.  
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/AddPlaylistCoverImage.py
        ```
        </details>
        """
        apiMethodName:str = 'AddPlaylistCoverImage'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("playlistId", playlistId)
            apiMethodParms.AppendKeyValue("imagePath", imagePath)
            _logsi.LogMethodParmList(SILevel.Verbose, "Add playlist cover image", apiMethodParms)
                
            fData:BytesIO = BytesIO()
            
            # read all bytes from the file in 8192 byte chunks, and writes
            # them to an internal buffer.
            with open(imagePath, 'rb') as reader:
                
                buffertmp = bytes(0x2000)

                while True:
                    buffertmp = reader.read(len(buffertmp))
                    if (fData.tell() > 262144):
                        raise ValueError('file is too large to upload; must be less than 256kb')
                    elif (len(buffertmp) > 0):
                        fData.write(buffertmp)
                    else:
                        break
                    
            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/playlists/{playlist_id}/images'.format(playlist_id=playlistId))
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.RequestHeaders['Content-Type'] = 'image/jpeg'
            msg.RequestData = base64.b64encode(fData.getvalue()).decode('utf-8') 
            msg.IsRequestDataEncoded = True
            self.MakeRequest('PUT', msg)

            # process results.
            # no results to process - this is pass or fail.
            return
        
        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def AddPlaylistItems(
        self, 
        playlistId:str, 
        uris:str=None,
        position:int=None,
        ) -> str:
        """
        Add one or more items to a user's playlist.
        
        This method requires the `playlist-modify-public` and `playlist-modify-private` scope.
        
        Args:
        
            playlistId (str):  
                The Spotify ID of the playlist.
                Example: `5AC9ZXA7nJ7oGWO911FuDG`
            uris (str):  
                A comma-separated list of Spotify URIs to add; can be track or episode URIs.  
                Example: `spotify:track:4iV5W9uYEdYUVa79Axb7Rh,spotify:episode:26c0zVyOv1lzfYpBXdh1zC`.  
                A maximum of 100 items can be specified in one request.
                If null, the currently playing context uri value is used.
            position (int):  
                The position to insert the items, a zero-based index.  
                For example, to insert the items in the first position: position=0;  
                to insert the items in the third position: position=2.  
                If omitted, the items will be appended to the playlist.  
                Items are added in the order they are listed in the `uris` argument.
                
        Returns:
            A snapshot ID for the updated playlist.
            
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/AddPlaylistItems.py
        ```
        </details>
        """
        apiMethodName:str = 'AddPlaylistItems'
        apiMethodParms:SIMethodParmListContext = None
        result:str = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("playlistId", playlistId)
            apiMethodParms.AppendKeyValue("uris", uris)
            apiMethodParms.AppendKeyValue("position", position)
            _logsi.LogMethodParmList(SILevel.Verbose, "Add items to a user's playlist", apiMethodParms)
                
            # if uris not specified, then return currently playing uri value.
            if (uris is None) or (len(uris.strip()) == 0):
                uris = self.GetPlayerNowPlayingUri(None)
                if uris is None:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'uris'), logsi=_logsi)
                    
            # build a list of all item uri's.
            # remove any leading / trailing spaces in case user put a space between the items.
            arrUris:list[str] = uris.split(',')
            for idx in range(0, len(arrUris)):
                arrUris[idx] = arrUris[idx].strip()

            # build spotify web api request parameters.
            reqData:dict = \
            {
                'uris': arrUris
            }
            if position is not None:
                reqData['position'] = position
                
            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/playlists/{playlist_id}/tracks'.format(playlist_id=playlistId))
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.RequestJson = reqData
            self.MakeRequest('POST', msg)

            # process results.
            result = msg.ResponseData.get('snapshot_id','unknown')
        
            # trace.
            _logsi.LogString(SILevel.Verbose, TRACE_METHOD_RESULT % apiMethodName, result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def ChangePlaylistDetails(
        self, 
        playlistId:str, 
        name:str=None,
        description:str=None,
        public:bool=None,
        collaborative:bool=None,
        imagePath:str=None
        ) -> None:
        """
        Change a playlist's details (name, description, and public / private state).  
        
        This method requires the `playlist-modify-public` and `playlist-modify-private` scope.
        
        Args:
        
            playlistId (str):  
                The Spotify ID of the playlist.
                Example: `5AC9ZXA7nJ7oGWO911FuDG`
            name (str):
                The updated name for the playlist, for example "My New Playlist Title"
                This name does not need to be unique; a user may have several playlists with 
                the same name.
            description (str):
                The updated playlist description, as displayed in Spotify Clients and in the Web API.
            public (bool):
                If true, the playlist will be public; if false, it will be private.  
            collaborative (bool):
                If true, the playlist will become collaborative and other users will be able to modify 
                the playlist in their Spotify client.  
                Note: You can only set collaborative to true on non-public playlists.
            imagePath (str):
                A fully-qualified path of an image to display for the playlist.
                The image must be in JPEG format, and cannot exceed 256KB in Base64 encoded size.  

        The user must own the playlist.
        
        The `public` argument will be set to False if the `collaborative` argument is True.
        
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        Setting the `public` argument to true will publish the playlist on the user's profile,
        which means it will appear under `public playlists`. This will also make the playlist 
        visible in search results. Note that the `public` argument does not refer to access control, 
        so anyone with the link to the playlist can access it unless it's made private.
        
        A playlist can also be made collaborative by setting the `collaborative` argument to true. 
        This means that anyone with the link can add to or remove a track from it.
                
        If the `imagePath` argument is specified, the `AddPlaylistCoverImage` method is called to 
        upload the image after the playlist details are updated.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/ChangePlaylistDetails.py
        ```
        </details>
        """
        apiMethodName:str = 'ChangePlaylistDetails'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("playlistId", playlistId)
            apiMethodParms.AppendKeyValue("name", name)
            apiMethodParms.AppendKeyValue("description", description)
            apiMethodParms.AppendKeyValue("public", public)
            apiMethodParms.AppendKeyValue("collaborative", collaborative)
            apiMethodParms.AppendKeyValue("imagePath", imagePath)
            _logsi.LogMethodParmList(SILevel.Verbose, "Change a playlist details", apiMethodParms)
                
            # if collaborative is True, then force public to false as Spotify requires it.
            if collaborative:
                public = False

            # build spotify web api request parameters.
            reqData:dict = {}
            if name is not None:
                reqData['name'] = '%s' % name
            if description is not None:
                reqData['description'] = '%s' % description
            if public is not None:
                reqData['public'] = public
            if collaborative is not None:
                reqData['collaborative'] = collaborative
                
            # validations.
            if len(reqData) == 0:
                raise ValueError('no details were provided to change.')
            
            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/playlists/{playlist_id}'.format(playlist_id=playlistId))
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.RequestJson = reqData
            self.MakeRequest('PUT', msg)

            # was a playlist image path specified?  if so, then assign the image.
            if imagePath is not None:
                try:
                    self.AddPlaylistCoverImage(playlistId, imagePath)
                except Exception as ex:
                    pass   # ignore exceptions, as they are already logged.

            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def CheckAlbumFavorites(
        self, 
        ids:str=None,
        ) -> dict:
        """
        Check if one or more albums is already saved in the current Spotify user's 
        'Your Library'.
        
        This method requires the `user-library-read` scope.

        Args:
            ids (str):  
                A comma-separated list of the Spotify IDs for the albums.  
                Maximum: 20 IDs.  
                Example: `6vc9OTcyd3hyzabCmsdnwE,2noRn2Aes5aoNVsU6iWThc`
                If null, the currently playing album uri id value is used.
                
        Returns:
            A dictionary of the ids, along with a boolean status for each that indicates 
            if the album is saved (True) in the users 'Your Library' or not (False).
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/CheckAlbumFavorites.py
        ```
        </details>
        """
        apiMethodName:str = 'CheckAlbumFavorites'
        apiMethodParms:SIMethodParmListContext = None
        result:dict = {}
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            _logsi.LogMethodParmList(SILevel.Verbose, "Check if one or more albums are saved in a user's favorites", apiMethodParms)
                
            # if ids not specified, then return currently playing album id value.
            if (ids is None) or (len(ids.strip()) == 0):
                uri = self.GetPlayerNowPlayingAlbumUri()
                if uri is not None:
                    ids = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'ids'), logsi=_logsi)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'ids': ids
            }

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/albums/contains')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)
            
            # build list of all input album id's.
            arrIds:list[str] = ids.split(',')

            # process results.
            flags:list[bool] = msg.ResponseData
            flagPtr:int = 0
            for strId in arrIds:
                if strId not in result:
                    result[strId] = flags[flagPtr]
                    flagPtr = flagPtr + 1
        
            # trace.
            _logsi.LogDictionary(SILevel.Verbose, TRACE_METHOD_RESULT % apiMethodName, result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def CheckArtistsFollowing(
        self, 
        ids:str=None,
        ) -> dict:
        """
        Check to see if the current user is following one or more artists.
        
        This method requires the `user-follow-read` scope.
        
        Args:
            ids (str):  
                A comma-separated list of Spotify artist ID's to check.  
                Maximum: 50 ID's.  
                Example: `2CIMQHirSU0MQqyYHq0eOx,1IQ2e1buppatiN1bxUVkrk`  
                If null, the currently playing artist uri id value is used.
                
        Returns:
            A dictionary of the IDs, along with a boolean status for each that indicates 
            if the user follows the ID (True) or not (False).
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/CheckArtistsFollowing.py
        ```
        </details>
        """
        apiMethodName:str = 'CheckArtistsFollowing'
        apiMethodParms:SIMethodParmListContext = None
        result:dict = {}
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            _logsi.LogMethodParmList(SILevel.Verbose, "Check if user is following one or more artists", apiMethodParms)
                
            # remove any leading / trailing spaces in case user put a space between the items.
            if ids is not None:
                ids = ids.replace(' ','')
                
            # if ids not specified, then return currently playing artist id value.
            if (ids is None) or (len(ids.strip()) == 0):
                uri = self.GetPlayerNowPlayingArtistUri()
                if uri is not None:
                    ids = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'ids'), logsi=_logsi)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'type': SpotifyMediaTypes.ARTIST.value,
                'ids': ids
            }

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/following/contains')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)
            
            # build list of all input id's.
            arrIds:list[str] = ids.split(',')

            # process results.               
            flags:list[bool] = msg.ResponseData
            flagPtr:int = 0
            for strId in arrIds:
                if strId not in result:
                    result[strId] = flags[flagPtr]
                    flagPtr = flagPtr + 1

            # trace.
            _logsi.LogDictionary(SILevel.Verbose, TRACE_METHOD_RESULT % apiMethodName, result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def CheckAudiobookFavorites(
        self, 
        ids:str=None,
        ) -> dict:
        """
        Check if one or more audiobooks is already saved in the current Spotify user's 
        'Your Library'.
        
        This method requires the `user-library-read` scope.

        Args:
            ids (str):  
                A comma-separated list of the Spotify IDs for the audiobooks.  
                Maximum: 50 IDs.  
                Example: `74aydHJKgYz3AIq3jjBSv1,4nfQ1hBJWjD0Jq9sK3YRW8,3PFyizE2tGCSRLusl2Qizf`
                If null, the currently playing audiobook uri id value is used.
                
        Returns:
            A dictionary of the ids, along with a boolean status for each that indicates 
            if the audiobook is saved (True) in the users 'Your Library' or not (False).
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/CheckAudiobookFavorites.py
        ```
        </details>
        """
        apiMethodName:str = 'CheckAudiobookFavorites'
        apiMethodParms:SIMethodParmListContext = None
        result:dict = {}
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            _logsi.LogMethodParmList(SILevel.Verbose, "Check if one or more audiobooks are saved in a user's favorites", apiMethodParms)
                
            # if ids not specified, then return currently playing id value.
            if (ids is None) or (len(ids.strip()) == 0):
                uri = self.GetPlayerNowPlayingAudiobookUri()
                if uri is not None:
                    ids = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'ids'), logsi=_logsi)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'ids': ids
            }

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/audiobooks/contains')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)
            
            # build list of all input album id's.
            arrIds:list[str] = ids.split(',')

            # process results.
            flags:list[bool] = msg.ResponseData
            flagPtr:int = 0
            for strId in arrIds:
                if strId not in result:
                    result[strId] = flags[flagPtr]
                    flagPtr = flagPtr + 1
        
            # trace.
            _logsi.LogDictionary(SILevel.Verbose, TRACE_METHOD_RESULT % apiMethodName, result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def CheckEpisodeFavorites(
        self, 
        ids:str=None,
        ) -> dict:
        """
        Check if one or more episodes is already saved in the current Spotify user's 
        'Your Library'.
        
        This method requires the `user-library-read` scope.

        Args:
            ids (str):  
                A comma-separated list of the Spotify IDs for the episodes.  
                Maximum: 50 IDs.  
                Example: `1kWUud3vY5ij5r62zxpTRy,2takcwOaAZWiXQijPHIx7B`
                If null, the currently playing episode uri id value is used.
                
        Returns:
            A dictionary of the ids, along with a boolean status for each that indicates 
            if the episode is saved (True) in the users 'Your Library' or not (False).
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/CheckEpisodeFavorites.py
        ```
        </details>
        """
        apiMethodName:str = 'CheckEpisodeFavorites'
        apiMethodParms:SIMethodParmListContext = None
        result:dict = {}
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            _logsi.LogMethodParmList(SILevel.Verbose, "Check if one or more episodes are saved in a user's favorites", apiMethodParms)
                
            # if ids not specified, then return currently playing id value.
            if (ids is None) or (len(ids.strip()) == 0):
                uri = self.GetPlayerNowPlayingUri(SpotifyMediaTypes.EPISODE.value)
                if uri is not None:
                    ids = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'ids'), logsi=_logsi)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'ids': ids
            }

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/episodes/contains')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)
            
            # build list of all input album id's.
            arrIds:list[str] = ids.split(',')

            # process results.
            flags:list[bool] = msg.ResponseData
            flagPtr:int = 0
            for strId in arrIds:
                if strId not in result:
                    result[strId] = flags[flagPtr]
                    flagPtr = flagPtr + 1
        
            # trace.
            _logsi.LogDictionary(SILevel.Verbose, TRACE_METHOD_RESULT % apiMethodName, result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def CheckPlaylistFollowers(
        self, 
        playlistId:str,
        userIds:str=None,
        ) -> dict:
        """
        Check to see if the current user is following a specified playlist.
        
        Args:
            playlistId (str):  
                The Spotify ID of the playlist.  
                Example: `3cEYpjA9oz9GiPac4AsH4n`
            userIds (str):  
                DEPRECATED - A single item list containing current user's Spotify Username; Maximum of 1 id.
                A comma-separated list of Spotify User ID's to check.  
                Maximum: 5 ID's.  
                Example: `1kWUud3vY5ij5r62zxpTRy,2takcwOaAZWiXQijPHIx7B`  
                
        Returns:
            Array of boolean, containing a single boolean status that indicates 
            if the user follows the playlist (True) or not (False).
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.
                
        As of (at least) 2024/10/07, Spotify has deprecated the userId's argument; 
        only current user can be tested.  Any other id's specified on this argument will 
        generate a `400 Bad Request` error.
                

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/CheckPlaylistFollowers.py
        ```
        </details>
        """
        apiMethodName:str = 'CheckPlaylistFollowers'
        apiMethodParms:SIMethodParmListContext = None
        result:dict = {}
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("playlistId", playlistId)
            apiMethodParms.AppendKeyValue("userIds (DEPRECATED)", userIds)
            _logsi.LogMethodParmList(SILevel.Verbose, "Check to see if users are following a playlist", apiMethodParms)

            # validations.
            if (userIds is None):
                userIds = self.UserProfile.Id
                
            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'ids': userIds
            }

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/playlists/{playlist_id}/followers/contains'.format(playlist_id=playlistId))
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)
            
            # build list of all input id's.
            arrIds:list[str] = userIds.split(',')

            # process results.
            flags:list[bool] = msg.ResponseData
            flagPtr:int = 0
            for strId in arrIds:
                if strId not in result:
                    result[strId] = flags[flagPtr]
                    flagPtr = flagPtr + 1
        
            # trace.
            _logsi.LogDictionary(SILevel.Verbose, TRACE_METHOD_RESULT % apiMethodName, result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def CheckShowFavorites(
        self, 
        ids:str=None,
        ) -> dict:
        """
        Check if one or more shows is already saved in the current Spotify user's 
        'Your Library'.
        
        This method requires the `user-library-read` scope.

        Args:
            ids (str):  
                A comma-separated list of the Spotify IDs for the shows.  
                Maximum: 50 IDs.  
                Example: `1kWUud3vY5ij5r62zxpTRy,2takcwOaAZWiXQijPHIx7B`
                If null, the currently playing show uri id value is used.
                
        Returns:
            A dictionary of the ids, along with a boolean status for each that indicates 
            if the show is saved (True) in the users 'Your Library' or not (False).
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/CheckShowFavorites.py
        ```
        </details>
        """
        apiMethodName:str = 'CheckShowFavorites'
        apiMethodParms:SIMethodParmListContext = None
        result:dict = {}
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            _logsi.LogMethodParmList(SILevel.Verbose, "Check if one or more shows are saved in a user's favorites", apiMethodParms)
                
            # if ids not specified, then return currently playing id value.
            if (ids is None) or (len(ids.strip()) == 0):
                uri = self.GetPlayerNowPlayingShowUri()
                if uri is not None:
                    ids = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'ids'), logsi=_logsi)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'ids': ids
            }

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/shows/contains')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)
            
            # build list of all input album id's.
            arrIds:list[str] = ids.split(',')

            # process results.
            flags:list[bool] = msg.ResponseData
            flagPtr:int = 0
            for strId in arrIds:
                if strId not in result:
                    result[strId] = flags[flagPtr]
                    flagPtr = flagPtr + 1
        
            # trace.
            _logsi.LogDictionary(SILevel.Verbose, TRACE_METHOD_RESULT % apiMethodName, result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def CheckTrackFavorites(
        self, 
        ids:str=None,
        ) -> dict:
        """
        Check if one or more tracks is already saved in the current Spotify user's 
        'Your Library'.
        
        This method requires the `user-library-read` scope.

        Args:
            ids (str):  
                A comma-separated list of the Spotify IDs for the tracks.  
                Maximum: 50 IDs.  
                Example: `1kWUud3vY5ij5r62zxpTRy,2takcwOaAZWiXQijPHIx7B`
                If null, the currently playing track uri id value is used.
                
        Returns:
            A dictionary of the ids, along with a boolean status for each that indicates 
            if the track is saved (True) in the users 'Your Library' or not (False).
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/CheckTrackFavorites.py
        ```
        </details>
        """
        apiMethodName:str = 'CheckTrackFavorites'
        apiMethodParms:SIMethodParmListContext = None
        result:dict = {}
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            _logsi.LogMethodParmList(SILevel.Verbose, "Check if one or more tracks are saved in a user's favorites", apiMethodParms)
                
            # if ids not specified, then return currently playing id value.
            if (ids is None) or (len(ids.strip()) == 0):
                uri = self.GetPlayerNowPlayingUri(SpotifyMediaTypes.TRACK.value)
                if uri is not None:
                    ids = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'ids'), logsi=_logsi)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'ids': ids
            }

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/tracks/contains')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)
            
            # build list of all input album id's.
            arrIds:list[str] = ids.split(',')

            # process results.
            flags:list[bool] = msg.ResponseData
            flagPtr:int = 0
            for strId in arrIds:
                if strId not in result:
                    result[strId] = flags[flagPtr]
                    flagPtr = flagPtr + 1
        
            # trace.
            _logsi.LogDictionary(SILevel.Verbose, TRACE_METHOD_RESULT % apiMethodName, result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def CheckUsersFollowing(
        self, 
        ids:str,
        ) -> dict:
        """
        Check to see if the current user is following one or more users.
        
        This method requires the `user-follow-read` scope.
        
        Args:
            ids (str):  
                A comma-separated list of Spotify user ID's to check.  
                Maximum: 50 ID's.  
                Example: `smedjan,smedjan123`  
                
        Returns:
            A dictionary of the IDs, along with a boolean status for each that indicates 
            if the user follows the ID (True) or not (False).
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/CheckUsersFollowing.py
        ```
        </details>
        """
        apiMethodName:str = 'CheckUsersFollowing'
        apiMethodParms:SIMethodParmListContext = None
        result:dict = {}
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            _logsi.LogMethodParmList(SILevel.Verbose, "Check if user is following one or more users", apiMethodParms)
                
            # remove any leading / trailing spaces in case user put a space between the items.
            if ids is not None:
                ids = ids.replace(' ','')
                
            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'type': 'user',
                'ids': ids
            }

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/following/contains')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)
            
            # build list of all input id's.
            arrIds:list[str] = ids.split(',')

            # process results.
            flags:list[bool] = msg.ResponseData
            flagPtr:int = 0
            for strId in arrIds:
                if strId not in result:
                    result[strId] = flags[flagPtr]
                    flagPtr = flagPtr + 1
        
            # trace.
            _logsi.LogDictionary(SILevel.Verbose, TRACE_METHOD_RESULT % apiMethodName, result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def ClearConfigurationCache(self) -> None:
        """
        Removes (clears) all items from the configuration cache.
        """
        apiMethodName:str = 'ClearConfigurationCache'
        
        try:
            
            # trace.
            _logsi.EnterMethod(SILevel.Debug, apiMethodName)
            _logsi.LogVerbose("Clearing the configuration cache")
                
            # clear the cache.
            self._ConfigurationCache.clear()
                
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def ClearPlaylistItems(
        self, 
        playlistId:str
        ) -> str:
        """
        Removes (clears) all items from a user's playlist.
        
        This method requires the `playlist-modify-public` and `playlist-modify-private` scope.
        
        Args:
        
            playlistId (str):  
                The Spotify ID of the playlist.
                Example: `5AC9ZXA7nJ7oGWO911FuDG`
                
        Returns:
            A snapshot ID for the updated playlist.
            
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/ClearPlaylistItems.py
        ```
        </details>
        """
        apiMethodName:str = 'ClearPlaylistItems'
        apiMethodParms:SIMethodParmListContext = None
        result:str = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("playlistId", playlistId)
            _logsi.LogMethodParmList(SILevel.Verbose, "Clear (remove) all items from a user's playlist", apiMethodParms)
                
            # build spotify web api request parameters.
            reqData:dict = \
            {
                'uris': []
            }
                
            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/playlists/{playlist_id}/tracks'.format(playlist_id=playlistId))
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.RequestJson = reqData
            self.MakeRequest('PUT', msg)

            # process results.
            result = msg.ResponseData.get('snapshot_id','unknown')
        
            # trace.
            _logsi.LogString(SILevel.Verbose, TRACE_METHOD_RESULT % apiMethodName, result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def CreatePlaylist(
        self, 
        userId:str, 
        name:str=None,
        description:str=None,
        public:bool=True,
        collaborative:bool=False,
        imagePath:str=None
        ) -> Playlist:
        """
        Create an empty playlist for a Spotify user.  
        
        This method requires the `playlist-modify-public` and `playlist-modify-private` scope.
        
        Args:
        
            userId (str):  
                The user's Spotify user ID.
                Example: `32k99y2kg5lnn3mxhtmd2bpdkjfu`
            name (str):
                The name for the new playlist, for example "My Playlist".  
                This name does not need to be unique; a user may have several playlists with 
                the same name.
            description (str):
                The playlist description, as displayed in Spotify Clients and in the Web API.
            public (bool):
                If true, the playlist will be public; if false, it will be private.  
                To be able to create private playlists, the user must have granted the 
                `playlist-modify-private` scope.  
                Defaults to true. 
            collaborative (bool):
                If true, the playlist will be collaborative.  
                Note: to create a collaborative playlist you must also set public to false. 
                To create collaborative playlists you must have granted `playlist-modify-private`
                and `playlist-modify-public` scope.  
                Defaults to false.
            imagePath (str):
                A fully-qualified path of an image to display for the playlist.
                The image must be in JPEG format, and cannot exceed 256KB in Base64 encoded size.  

        The playlist will be empty until you add tracks. 
        
        Setting the `public` argument to true will publish the playlist on the user's profile,
        which means it will appear under `public playlists`. This will also make the playlist 
        visible in search results. Note that the `public` argument does not refer to access control, 
        so anyone with the link to the playlist can access it unless it's made private.
        
        A playlist can also be made collaborative by setting the `collaborative` argument to true. 
        This means that anyone with the link can add to or remove a track from it.
        
        Each user is generally limited to a maximum of 11,000 playlists.
        
        If the `imagePath` argument is specified, the `AddPlaylistCoverImage` method is called to 
        upload the image after the playlist is created.

        Returns:
            A `Playlist` object that contains the playlist details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/CreatePlaylist.py
        ```
        </details>
        """
        apiMethodName:str = 'CreatePlaylist'
        apiMethodParms:SIMethodParmListContext = None
        result:Playlist = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("userId", userId)
            apiMethodParms.AppendKeyValue("name", name)
            apiMethodParms.AppendKeyValue("description", description)
            apiMethodParms.AppendKeyValue("public", public)
            apiMethodParms.AppendKeyValue("collaborative", collaborative)
            apiMethodParms.AppendKeyValue("imagePath", imagePath)
            _logsi.LogMethodParmList(SILevel.Verbose, "Create an empty playlist for a user", apiMethodParms)

            # validations.
            if (public is None):
                public = True
            if (collaborative is None):
                collaborative = False

            # if userId is not supplied, then use profile value.
            if userId is None or len(userId.strip()) == 0:
                userId = self.UserProfile.Id
                
            # if collaborative is True, then force public to false as Spotify requires it.
            if collaborative:
                public = False

            # build spotify web api request parameters.
            reqData:dict = \
            {
                'name': '%s' % name,
                'description': '%s' % description,
                'public': public,
                'collaborative': collaborative,
            }
            
            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/users/{user_id}/playlists'.format(user_id=userId))
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.RequestJson = reqData
            self.MakeRequest('POST', msg)

            # process results.
            result = Playlist(root=msg.ResponseData)

            # was a playlist image path specified?  if so, then assign the image.
            if imagePath is not None:
                try:
                    self.AddPlaylistCoverImage(result.Id, imagePath)
                except Exception as ex:
                    pass   # ignore exceptions, as they are already logged.
        
            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def FollowArtists(
        self, 
        ids:str=None,
        ) -> None:
        """
        Add the current user as a follower of one or more artists.

        This method requires the `user-follow-modify` scope.
        
        Args:
            ids (str):  
                A comma-separated list of the Spotify artist IDs.  
                A maximum of 50 IDs can be sent in one request.
                Example: `2CIMQHirSU0MQqyYHq0eOx,1IQ2e1buppatiN1bxUVkrk`
                If null, the currently playing track artist uri id value is used.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.
                
        No exception is raised if an artist is already followed.
                
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/FollowArtists.py
        ```
        </details>
        """
        apiMethodName:str = 'FollowArtists'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            _logsi.LogMethodParmList(SILevel.Verbose, "Add the current user as a follower of one or more artists", apiMethodParms)
                                   
            # if ids not specified, then return currently playing artist id value.
            if (ids is None) or (len(ids.strip()) == 0):
                uri = self.GetPlayerNowPlayingArtistUri()
                if uri is not None:
                    ids = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'ids'), logsi=_logsi)

            # build a list of all item id's.
            # remove any leading / trailing spaces in case user put a space between the items.
            arrIds:list[str] = ids.split(',')
            for idx in range(0, len(arrIds)):
                arrIds[idx] = arrIds[idx].strip()
                
            # build spotify web api request parameters.
            reqData:dict = \
            {
                'ids': arrIds
            }

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/following?type=artist')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.RequestJson = reqData
            self.MakeRequest('PUT', msg)
            
            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def FollowPlaylist(
        self, 
        playlistId:str=None,
        public:bool=True
        ) -> None:
        """
        Add the current user as a follower of a playlist.

        This method requires the `playlist-modify-public` and `playlist-modify-private` scope.
        
        Args:
            playlistId (str):  
                The Spotify ID of the playlist.  
                Example: `3cEYpjA9oz9GiPac4AsH4n`
                If null, the currently playing playlist uri id value is used.
            public (bool):
                If true the playlist will be included in user's public playlists, if false it 
                will remain private.  
                Default is True. 
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.
                
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/FollowPlaylist.py
        ```
        </details>
        """
        apiMethodName:str = 'FollowPlaylist'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("playlistId", playlistId)
            apiMethodParms.AppendKeyValue("public", public)
            _logsi.LogMethodParmList(SILevel.Verbose, "Add the current user as a follower of a playlist", apiMethodParms)
            
            # validations.
            if (public is None):
                public = True
                
            # if playlistId not specified, then return currently playing playlist id value.
            if (playlistId is None) or (len(playlistId.strip()) == 0):
                uri = self.GetPlayerNowPlayingPlaylistUri()
                if uri is not None:
                    playlistId = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'playlistId'), logsi=_logsi)

            # build spotify web api request parameters.
            reqData:dict = {}
            if public is not None:
                reqData['public'] = public

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/playlists/{playlist_id}/followers'.format(playlist_id=playlistId))
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.RequestJson = reqData
            self.MakeRequest('PUT', msg)
            
            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def FollowUsers(
        self, 
        ids:str,
        ) -> None:
        """
        Add the current user as a follower of one or more users.

        This method requires the `user-follow-modify` scope.
        
        Args:
            ids (str):  
                A comma-separated list of the Spotify user IDs.  
                A maximum of 50 IDs can be sent in one request.
                Example: `smedjan`
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.
                
        No exception is raised if a user is already followed.
                
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/FollowUsers.py
        ```
        </details>
        """
        apiMethodName:str = 'FollowUsers'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            _logsi.LogMethodParmList(SILevel.Verbose, "Add the current user as a follower of one or more users", apiMethodParms)
                
            # build a list of all item id's.
            # remove any leading / trailing spaces in case user put a space between the items.
            arrIds:list[str] = ids.split(',')
            for idx in range(0, len(arrIds)):
                arrIds[idx] = arrIds[idx].strip()
                
            # build spotify web api request parameters.
            reqData:dict = \
            {
                'ids': arrIds
            }

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/following?type=user')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.RequestJson = reqData
            self.MakeRequest('PUT', msg)
            
            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetAlbum(
        self, 
        albumId:str=None, 
        market:str=None,
        ) -> Album:
        """
        Get Spotify catalog information for a single album.
        
        Args:
            albumId (str):  
                The Spotify ID of the album.  
                Example: `6vc9OTcyd3hyzabCmsdnwE`
                If null, the currently playing album uri id value is used; a Spotify Free or Premium account 
                is required to correctly read the currently playing context.
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
                
        Returns:
            An `Album` object that contains the album details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetAlbum.py
        ```
          <summary>Sample Code - NowPlaying</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetAlbum_NowPlaying.py
        ```
        </details>
        """
        apiMethodName:str = 'GetAlbum'
        apiMethodParms:SIMethodParmListContext = None
        result:Album = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("albumId", albumId)
            apiMethodParms.AppendKeyValue("market", market)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get Spotify catalog information for a single album", apiMethodParms)
                
            # ensure we have a market value, in order to return track relinking (e.g. `linked_from`) data.
            market = self._ValidateMarket(market, forceReturnValue=True)

            # if albumId not specified, then return currently playing album id value.
            if (albumId is None) or (len(albumId.strip()) == 0):
                uri = self.GetPlayerNowPlayingAlbumUri()
                if uri is not None:
                    albumId = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'albumId'), logsi=_logsi)

            # build spotify web api request parameters.
            urlParms:dict = {}
            if market is not None:
                urlParms['market'] = market

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/albums/{id}'.format(id=albumId))
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)

            # process results.
            result = Album(root=msg.ResponseData)
        
            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetAlbumFavorites(
        self, 
        limit:int=20, 
        offset:int=0,
        market:str=None,
        limitTotal:int=None,
        sortResult:bool=True,
        ) -> AlbumPageSaved:
        """
        Get a list of the albums saved in the current Spotify user's 'Your Library'.
        
        This method requires the `user-library-read` scope.

        Args:
            limit (int):
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            offset (int):
                The page index offset of the first item to return.  
                Use with limit to get the next set of items.  
                Default: 0 (the first item).  
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
            sortResult (bool):
                True to sort the items by name; otherwise, False to leave the items in the same order they 
                were returned in by the Spotify Web API.  
                Default: True
                
        Returns:
            An `AlbumPageSaved` object that contains saved album information.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetAlbumFavorites.py
        ```
        </details>
        <details>
          <summary>Sample Code - Auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetAlbumFavorites_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'GetAlbumFavorites'
        apiMethodParms:SIMethodParmListContext = None
        result:AlbumPageSaved = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("offset", offset)
            apiMethodParms.AppendKeyValue("market", market)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            apiMethodParms.AppendKeyValue("sortResult", sortResult)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get a list of the user's album favorites", apiMethodParms)
                
            # validations.
            if limit is None: 
                limit = 20
            if offset is None: 
                offset = 0
            if not isinstance(limitTotal, int):
                limitTotal = 0
            if sortResult is None: 
                sortResult = True
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = AlbumPageSaved()

            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'limit': limit,
                'offset': offset,
            }
            if market is not None:
                urlParms['market'] = market

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/albums')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                pageObj = AlbumPageSaved(root=msg.ResponseData)
            
                # trace.
                _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:AlbumSaved
                    for item in pageObj.Items:
                        # sometimes spotify api returns items with no information; discard these!
                        if (item.Album is not None) and (item.Album.Uri is not None):
                            result.Items.append(item)
                            result.Limit = result.ItemsCount
                            if result.ItemsCount >= limitTotal:
                                break
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithOffset(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break
                    
            # update result object with final paging details.
            result.Total = pageObj.Total
            result.DateLastRefreshed = datetime.utcnow().timestamp()
            
            # sort result items.
            if (len(result.Items) > 0):
                if (sortResult is True):
                    result.Items.sort(key=lambda x: (x.Album.Name or "").lower(), reverse=False)
                else:
                    result.Items.sort(key=lambda x: (x.AddedAt or "").lower(), reverse=True)

            # trace.
            _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE + result.PagingInfo) % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetAlbumNewReleases(
        self, 
        limit:int=20, 
        offset:int=0,
        country:str=None,
        limitTotal:int=None,
        sortResult:bool=True,
        ) -> AlbumPageSimplified:
        """
        Get a list of new album releases featured in Spotify (shown, for example, on a 
        Spotify player's "Browse" tab).
        
        Args:
            limit (int):
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            offset (int):
                The page index offset of the first item to return.  
                Use with limit to get the next set of items.  
                Default: 0 (the first item).  
            country (str):
                A country in the form of an ISO 3166-1 alpha-2 country code.  
                Provide this parameter if you want the list of returned items to be relevant to a
                particular country. If omitted, the returned items will be relevant to all countries.  
                Example: `SE`
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
            sortResult (bool):
                True to sort the items by name; otherwise, False to leave the items in the same order they 
                were returned in by the Spotify Web API.  
                Default: True
                
        Returns:
            An `AlbumPageSimplified` object that contains simplified album information.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetAlbumNewReleases.py
        ```
        </details>
        <details>
          <summary>Sample Code - Auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetAlbumNewReleases_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'GetAlbumNewReleases'
        apiMethodParms:SIMethodParmListContext = None
        result:AlbumPageSimplified = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("offset", offset)
            apiMethodParms.AppendKeyValue("country", country)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            apiMethodParms.AppendKeyValue("sortResult", sortResult)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get a list of new album releases", apiMethodParms)
                
            # validations.
            if limit is None: 
                limit = 20
            if offset is None: 
                offset = 0
            if not isinstance(limitTotal, int):
                limitTotal = 0
            if sortResult is None: 
                sortResult = True
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = AlbumPageSimplified()

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'limit': limit,
                'offset': offset,
            }
            if country is not None:
                urlParms['country'] = country

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/browse/new-releases')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                item:dict = msg.ResponseData.get('albums', None)
                if item is not None:
                    pageObj = AlbumPageSimplified(root=item)
            
                    # trace.
                    _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:AlbumSimplified
                    for item in pageObj.Items:
                        result.Items.append(item)
                        result.Limit = result.ItemsCount
                        if result.ItemsCount >= limitTotal:
                            break
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithOffset(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break
                    
            # update result object with final paging details.
            result.Total = pageObj.Total
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # sort result items.
            if (len(result.Items) > 0):
                if (sortResult is True):
                    result.Items.sort(key=lambda x: (x.Name or "").lower(), reverse=False)

            # trace.
            _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE + result.PagingInfo) % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetAlbums(
        self, 
        ids:str, 
        market:str=None,
        ) -> list[Album]:
        """
        Get Spotify catalog information for multiple albums.
        
        Args:
            ids (str):  
                A comma-separated list of the Spotify IDs for the albums.  
                Maximum: 20 IDs.  
                Example: `6vc9OTcyd3hyzabCmsdnwE,2noRn2Aes5aoNVsU6iWThc`
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
                
        Returns:
            A list of `Album` objects that contain the album details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetAlbums.py
        ```
        </details>
        """
        apiMethodName:str = 'GetAlbums'
        apiMethodParms:SIMethodParmListContext = None
        result:list[Album] = []
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            apiMethodParms.AppendKeyValue("market", market)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get Spotify catalog information for multiple albums", apiMethodParms)
                
            # ensure we have a market value, in order to return track relinking (e.g. `linked_from`) data.
            market = self._ValidateMarket(market, forceReturnValue=True)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'ids': ids,
            }
            if market is not None:
                urlParms['market'] = market

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/albums')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)

            # process results.
            items = msg.ResponseData.get('albums',None)
            if items is not None:
                for item in items:
                    result.append(Album(root=item))
        
            # trace.
            _logsi.LogArray(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, 'list[Album]'), result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetAlbumTracks(
        self, 
        albumId:str=None, 
        limit:int=20, 
        offset:int=0,
        market:str=None,
        limitTotal:int=None
        ) -> TrackPageSimplified:
        """
        Get Spotify catalog information about an album's tracks.  
        
        Optional parameters can be used to limit the number of tracks returned.
        
        Args:
            albumId (str):  
                The Spotify ID of the album.  
                Example: `6vc9OTcyd3hyzabCmsdnwE`
                If null, the currently playing album uri id value is used; a Spotify Free or Premium account 
                is required to correctly read the currently playing context.
            limit (int):  
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            offset (int):  
                The index of the first item to return; use with limit to get the next set of items.  
                Default: 0 (the first item).  
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
                
        Returns:
            A `TrackPageSimplified` object that contains simplified track information for the albumId.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetAlbumTracks.py
        ```
        </details>
        <details>
          <summary>Sample Code - Auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetAlbumTracks_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'GetAlbumTracks'
        apiMethodParms:SIMethodParmListContext = None
        result:TrackPageSimplified = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("albumId", albumId)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("offset", offset)
            apiMethodParms.AppendKeyValue("market", market)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get Spotify catalog information about an album's tracks", apiMethodParms)
                
            # validations.
            if limit is None: 
                limit = 20
            if offset is None: 
                offset = 0
            if not isinstance(limitTotal, int):
                limitTotal = 0
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = TrackPageSimplified()

            # ensure we have a market value, in order to return track relinking (e.g. `linked_from`) data.
            market = self._ValidateMarket(market, forceReturnValue=True)

            # if albumId not specified, then return currently playing album id value.
            if (albumId is None) or (len(albumId.strip()) == 0):
                uri = self.GetPlayerNowPlayingAlbumUri()
                if uri is not None:
                    albumId = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'albumId'), logsi=_logsi)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'limit': limit,
                'offset': offset,
            }
            if market is not None:
                urlParms['market'] = market

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/albums/{id}/tracks'.format(id=albumId))
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                pageObj = TrackPageSimplified(root=msg.ResponseData)

                # trace.
                _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:TrackSimplified
                    for item in pageObj.Items:
                        result.Items.append(item)
                        result.Limit = result.ItemsCount
                        if result.ItemsCount >= limitTotal:
                            break
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithOffset(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break

            # update result object with final paging details.
            result.Total = pageObj.Total
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # do not sort items, as they are in playable order.

            # trace.
            _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE + result.PagingInfo) % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetArtist(
        self, 
        artistId:str=None, 
        ) -> Artist:
        """
        Get Spotify catalog information for a single artist identified by their unique Spotify ID.
        
        Args:
            artistId (str):  
                The Spotify ID of the artist.  
                Example: `6APm8EjxOHSYM5B4i3vT3q`
                If null, the currently playing artist uri id value is used; a Spotify Free or Premium account 
                is required to correctly read the currently playing context.
                
        Returns:
            An `Artist` object that contains the artist details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetArtist.py
        ```
          <summary>Sample Code - NowPlaying</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetArtist_NowPlaying.py
        ```
        </details>
        """
        apiMethodName:str = 'GetArtist'
        apiMethodParms:SIMethodParmListContext = None
        result:Artist = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("artistId", artistId)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get Spotify catalog information for a single artist", apiMethodParms)
                
            # if artistId not specified, then return currently playing artist id value.
            if (artistId is None) or (len(artistId.strip()) == 0):
                uri = self.GetPlayerNowPlayingArtistUri()
                if uri is not None:
                    artistId = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'artistId'), logsi=_logsi)

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/artists/{id}'.format(id=artistId))
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            self.MakeRequest('GET', msg)

            # process results.
            result = Artist(root=msg.ResponseData)
        
            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetArtistAlbums(
        self, 
        artistId:str=None, 
        include_groups:str='album', 
        limit:int=20, 
        offset:int=0,
        market:str=None,
        limitTotal:int=None,
        sortResult:bool=True,
        ) -> AlbumPageSimplified:
        """
        Get Spotify catalog information about an artist's albums.
        
        Args:
            artistId (str):  
                The Spotify ID of the artist.  
                Example: `6APm8EjxOHSYM5B4i3vT3q`
                If null, the currently playing artist uri id value is used; a Spotify Free or Premium account 
                is required to correctly read the currently playing context.
            include_groups (str):  
                A comma-separated list of keywords that will be used to filter the response.  
                If not supplied, all album types will be returned.  
                Valid values are: `album`, `single`, `appears_on`, `compilation`  
                Example: `single,appears_on`
            limit (int):  
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            offset (int):  
                The index of the first item to return; use with limit to get the next set of items.  
                Default: 0 (the first item).  
            market (str):  
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that is 
                available in that market will be returned.
                If a valid user access token is specified in the request header, the country associated with 
                the user account will take priority over this parameter.
                Note: If neither market or user country are provided, the content is considered unavailable for the client.
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
            sortResult (bool):
                True to sort the items by name; otherwise, False to leave the items in the same order they 
                were returned in by the Spotify Web API.  
                Default: True
                
        Returns:
            An `AlbumPageSimplified` object of matching results.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetArtistAlbums.py
        ```
        </details>
        <details>
          <summary>Sample Code - auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetArtistAlbums_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'GetArtistAlbums'
        apiMethodParms:SIMethodParmListContext = None
        result:AlbumPageSimplified = None
        
        try:

            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("artistId", artistId)
            apiMethodParms.AppendKeyValue("include_groups", include_groups)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("offset", offset)
            apiMethodParms.AppendKeyValue("market", market)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            apiMethodParms.AppendKeyValue("sortResult", sortResult)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get Spotify catalog information about an artist's albums", apiMethodParms)
                
            # validations.
            if limit is None: 
                limit = 20
            if offset is None: 
                offset = 0
            if not isinstance(limitTotal, int):
                limitTotal = 0
            if sortResult is None: 
                sortResult = True
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = AlbumPageSimplified()

            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market)

            # if artistId not specified, then return currently playing artist id value.
            if (artistId is None) or (len(artistId.strip()) == 0):
                uri = self.GetPlayerNowPlayingArtistUri()
                if uri is not None:
                    artistId = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'artistId'), logsi=_logsi)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'include_groups': include_groups, 
                'limit': limit,
                'offset': offset,
            }
            if market is not None:
                urlParms['market'] = market

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/artists/{id}/albums'.format(id=artistId))
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                pageObj = AlbumPageSimplified(root=msg.ResponseData)

                # trace.
                _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:AlbumSimplified
                    for item in pageObj.Items:
                        result.Items.append(item)
                        result.Limit = result.ItemsCount
                        if result.ItemsCount >= limitTotal:
                            break
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithOffset(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break

            # update result object with final paging details.
            result.Total = pageObj.Total
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # sort result items.
            if (len(result.Items) > 0):
                if (sortResult is True):
                    result.Items.sort(key=lambda x: (x.Name or "").lower(), reverse=False)

            # trace.
            _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE + result.PagingInfo) % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)
        

    def GetArtistInfo(
        self, 
        artistId:str=None, 
        ) -> ArtistInfo:
        """
        Get artist about information from the Spotify Artist Biography page for the
        specified Spotify artist ID.
        
        Args:
            artistId (str):  
                The Spotify ID of the artist.  
                Example: `6APm8EjxOHSYM5B4i3vT3q`
                If null, the currently playing artist uri id value is used; a Spotify Free or Premium account 
                is required to correctly read the currently playing context.
                
        Returns:
            An `ArtistInfo` object that contains the artist info details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetArtistInfo.py
        ```
        </details>
        """
        apiMethodName:str = 'GetArtistInfo'
        apiMethodParms:SIMethodParmListContext = None
        result:ArtistInfo = None
        
        ABOUT_MONTHLY_LISTENERS:str = ' monthly listeners'
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("artistId", artistId)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get Spotify catalog information for a single artist", apiMethodParms)
                
            # if artistId not specified, then return currently playing artist id value.
            if (artistId is None) or (len(artistId.strip()) == 0):
                uri = self.GetPlayerNowPlayingArtistUri()
                if uri is not None:
                    artistId = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'artistId'), logsi=_logsi)

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/artists/{id}'.format(id=artistId))
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            self.MakeRequest('GET', msg)

            # process results.
            artist = Artist(root=msg.ResponseData)
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, type(artist).__name__), artist, excludeNonPublic=True)
        
            # create base result.
            result = ArtistInfo(artist.Id, artist.Name, artist.Type, artist.Uri, artist.ImageUrl)
            
            # does artist have a bio information url?  if not then we are done.
            if (artist.Href is None) or (len(artist.Href.strip()) == 0):
                _logsi.LogVerbose("No html returned for artist details page: '%s'" % (artist.ExternalUrls.Spotify))
                return result

            # was a Spotify external url specified for the artist?  if not then we are done.
            if artist.ExternalUrls is None or artist.ExternalUrls.Spotify is None:
                _logsi.LogVerbose("Spotify ExternalUrl not present for artist details page")
                return result
            
            try:
                
                # retrieve artist details page.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, artist.ExternalUrls.Spotify)
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                self.MakeRequest('GET', msg)
                
                # log html response.
                #_logsi.LogHtml(SILevel.Verbose, "GetArtistInfo response HTML", msg.ResponseData)
                _logsi.LogSource(SILevel.Verbose, "GetArtistInfo response Text", msg.ResponseData, SISourceId.Html)
                
                # if no response data then we are done.
                if not msg.HasResponseData:
                    _logsi.LogVerbose("No html returned for artist details page: '%s'" % (artist.ExternalUrls.Spotify))
                    return result
                
                # find the starting <html> tag.
                # ElementTree fromstring method will fail if initial tag is "<!doctype html>".
                html:str = msg.ResponseData
                if html is None:
                    return result
                if not html.startswith('<html'):
                    idx:int = html.find('<html')
                    if idx == -1:
                        _logsi.LogVerbose("<html> tag could not be found for artist details page: '%s'" % (artist.ExternalUrls.Spotify))
                        return result
                    html = html[idx:]
                    _logsi.LogSource(SILevel.Verbose, "GetArtistInfo response Text (starting from '<html')", html, SISourceId.Html)
                    
                # log formatted html response.
                _logsi.LogXml(SILevel.Verbose, "GetArtistInfo response Text (formatted)", html, prettyPrint=True)
                
                # load html element tree so we can parse it.
                doc:Element = fromstring(html)
                _logsi.LogObject(SILevel.Verbose, "doc Element object", doc)
                               
                attrXPath:str = None
                elm:Element = None
                elmChild:Element = None
                innerText:str = None

                # about information - image (button / bio page):
                attrXPath = './/button[@type="button"]/descendant-or-self::img'
                _logsi.LogVerbose("Element search 'image button': '%s'" % attrXPath)
                attrElements:list[Element] = doc.xpath(attrXPath)
                for elm in attrElements:
                    _logsi.LogObject(SILevel.Verbose, "Element match: '%s'" % attrXPath, elm)
                    attrValue:str = elm.get('src', None)
                    if attrValue is not None:
                        result.ImageUrl = attrValue
                        break

                # about information - image (entity-id):
                # use the internal `_ImageUrl` attribute value to check, as the `ImageUrl` property
                # will return the `ImageUrlDefault` if `_ImageUrl` attribute was not set.
                # <img data-testid="artist-entity-image" src="https://i.scdn.co/image/ab6761610000517446196125b56397cd4e0d9c4b" />
                if result._ImageUrl is None:
                    attrXPath = './/attribute::data-testid[contains(., "artist-entity-image")]/../@src'
                    _logsi.LogVerbose("Element search 'image entity': '%s'" % attrXPath)
                    elmChild = doc.xpath(attrXPath)
                    if elmChild is not None:
                        _logsi.LogVerbose("Element match: '%s'" % elmChild[0])
                        result.ImageUrl = elmChild[0]
                
                # about information - monthly listeners:
                # <div data-testid="monthly-listeners-label">2,707,252 monthly listeners</div>
                attrXPath = './/attribute::data-testid[contains(., "monthly-listeners-label")]/../text()'
                _logsi.LogVerbose("Element search 'monthly listeners': '%s'" % attrXPath)
                elmChild = doc.xpath(attrXPath)
                if elmChild is not None:
                    _logsi.LogVerbose("Element match: '%s'" % elmChild[0])
                    attrValue = elmChild[0].replace(ABOUT_MONTHLY_LISTENERS,'')
                    attrValue = attrValue.replace(',','')
                    attrValue = attrValue.strip()
                    if attrValue.isnumeric:
                        result.MonthlyListeners = int(attrValue)

                # about information - bio:
                # <div data-testid="expandable-description">
                #    <div>
                #       <div>
                #          <span>xxxxx is a contemporary music band ...</span>
                #       </div>
                #    </div>
                # </div>                
                attrXPath = './/attribute::data-testid[contains(., "expandable-description")]/..'
                _logsi.LogVerbose("Element search 'bio': '%s'" % attrXPath)
                attrElements:list[Element] = doc.xpath(attrXPath)
                for elm in attrElements:
                    innerText = _xmlGetInnerText(elm)
                    _logsi.LogObject(SILevel.Verbose, "Element match: '%s' (innerText=%s)" % (attrXPath, innerText), elm)
                
                    # replace "see more" suffix with spotify link.
                    SEE_MORE:str = "see more"
                    if (innerText) and (innerText.endswith(SEE_MORE)):
                        innerText = innerText.removesuffix(SEE_MORE)
                        innerText += "<a href=\"%s\" target=\"_blank\">%s</a>" % (artist.ExternalUrls.Spotify, SEE_MORE)

                    result.Bio = innerText
                    
                    # remove various html attributes from sub-elements.
                    for elmDIV in elm.findall(".//*[@class]"):
                        del elmDIV.attrib["class"]
                    for elmDIV in elm.findall(".//*[@data-testid]"):
                        del elmDIV.attrib["data-testid"]
                    for elmDIV in elm.findall(".//*[@data-encore-id]"):
                        del elmDIV.attrib["data-encore-id"]
                    for elmDIV in elm.findall(".//*[@draggable]"):
                        del elmDIV.attrib["draggable"]
                        
                    # modify anchor link relative references in sub-elements.
                    # also force all links to open in a new window / tab.    
                    for elmDIV in elm.findall(".//a[@href]"):
                        value:str = elmDIV.attrib["href"]
                        if (value.startswith("/")):
                            value = SPOTIFY_ONLINE_LINK_PREFIX + value
                            elmDIV.attrib["href"] = value
                        elmDIV.attrib["target"] = "_blank"

                    # drop the parent DIV element(s), convert to html, and update result property.
                    xml_string = etree.tostring(elm[0], pretty_print=True, encoding="utf-8")
                    xml_decoded:str = xml_string.decode("utf-8")
                    xml_decoded = xml_decoded.replace("\n","<br/>")             # add <br> tags in place of newlines
                    if xml_decoded.startswith("<div><br/>  <div><br/>    "):    # trim leading and trailing line breaks
                        xml_decoded = xml_decoded.removeprefix("<div><br/>  <div><br/>    ")
                        xml_decoded = xml_decoded.removesuffix("  </div><br/></div><br/>")
                        xml_decoded = xml_decoded.removesuffix("<br/>")
                    elif xml_decoded.startswith("<div><div>"):                  # trim leading and trailing line breaks
                        xml_decoded = xml_decoded.removeprefix("<div><div>")
                        xml_decoded = xml_decoded.removesuffix("</div></div><br/>")
                    # replace see more button link
                    xml_decoded = xml_decoded.replace("\u2026","")              # replace unicode elipses (3 dots) character
                    xml_decoded = xml_decoded.replace('<button><span> <!-- -->see more</span></button>', ' <a href="' + artist.ExternalUrls.Spotify + '" target="_blank">see more</a>')
                    
                    # xml_decoded = xml_decoded.replace("<div><br/>  ","<div>")   # trim leading line breaks
                    # if xml_decoded.endswith("  </div><br/></div><br/>"):        # trim trailing line breaks
                    #     xml_decoded = xml_decoded.removesuffix("  </div><br/></div><br/>")
                    #     xml_decoded += "</div></div>"
                    result.BioHtml = xml_decoded
                    _logsi.LogHtml(SILevel.Verbose, "GetArtistInfo result BioHtml", result.BioHtml)
                    break
                
                # about information - on tour dates:
                # <h2>On tour</h2>
                # <div><ul><li>
                #   <a draggable="false" class="kZAjDLOBaUEUgIh0u_ar" href="/concert/35nHWo11uitgmm5XSkd8CU">
                #     <time class="jqymLdIlkUVKl8shJfKZ" dateTime="2024-11-09T19:00-05:00">
                #       <div class="encore-text encore-text-marginal-bold diaCgR2BgDJgHboSPS1S" data-encore-id="text">Nov</div>
                #       <div class="encore-text encore-text-title-small RjfBbWVLuXMzwFtTXDL0" data-encore-id="text">9</div>
                #     </time>
                #     <div class="ymKJ1kNm06pnfmgmATrg">
                #       <div class="encore-text encore-text-body-medium-bold encore-internal-color-text-base UmCMpZhcC2lll241N1NU" data-encore-id="text">Danny Gokey with Mac Powell and Seph Schlueter</div>
                #       <p class="encore-text encore-text-body-small bk3jsOor2S1AwKPihqwM" data-encore-id="text">
                #           <time class="cR3tL5CgXmgwfJDDKQ2A">Sat, Nov 9</time>Hobart Arena, Troy</p>
                #     </div>
                #   </a>
                # </li></ul></div>

                attrXPath = './/h2[text()="On tour"]/following-sibling::*/descendant-or-self::a'
                _logsi.LogVerbose("Element search 'On tour': '%s'" % attrXPath)
                attrElements:list[Element] = doc.xpath(attrXPath)
                for elm in attrElements:
                    event:ArtistInfoTourEvent = ArtistInfoTourEvent() 
                    
                    # process event more info link.
                    attrValue = elm.attrib["href"]
                    if (attrValue):
                        event.Href = SPOTIFY_ONLINE_LINK_PREFIX + attrValue
                    
                    # process event datetime.
                    for elmDT in elm.findall(".//*[@dateTime]"):
                        attrValue = elmDT.attrib["dateTime"]
                        idx:int = attrValue.rfind('-')
                        try:
                            if (idx > 15):                  # drop ending timezone suffix (e.g. "-06:00")
                                event.EventDateTime = datetime.fromisoformat(attrValue[:idx])
                            elif (attrValue.endswith("Z")): # drop ending "Z" suffix
                                event.EventDateTime = datetime.fromisoformat(attrValue.removesuffix("Z"))
                        except Exception as ex:
                            _logsi.LogException("Element value '%s' (%s) could not be parsed to a datetime object" % (elmDT, attrValue), ex, logToSystemLogger=False)
                            event.EventDateTime = None
                        break

                    # process event venue.
                    # we will remove the <time> element, leaving only the innerText of the <p> element.
                    for elmPT in elm.findall(".//p/time"):
                        #xml_string_before = etree.tostring(elm, pretty_print=True, encoding="utf-8")
                        elmPT.text = ""                         # remove <time> text value
                        #xml_string_after = etree.tostring(elm, pretty_print=True, encoding="utf-8")
                        break
                    for elmP in elm.findall(".//p"):
                        event.VenueName = _xmlGetInnerText(elmP)
                        break
                    
                    # process event title.
                    for elmDIV in elm.findall(".//div/div"):
                        event.Title = _xmlGetInnerText(elmDIV)
                        break
                    
                    # append event info to events collection.
                    result.TourEvents.append(event)
                    _logsi.LogObject(SILevel.Verbose, '%s: "%s" (%s)' % (type(event).__name__, event.Title, event.EventDateTime), event, excludeNonPublic=True)

                # about information - links.
                result.AboutUrlFacebook = self._GetArtistInfoAboutLink(doc,"Facebook")
                result.AboutUrlInstagram = self._GetArtistInfoAboutLink(doc,"Instagram")
                result.AboutUrlTwitter = self._GetArtistInfoAboutLink(doc,"Twitter")
                result.AboutUrlWikipedia = self._GetArtistInfoAboutLink(doc,"Wikipedia")
            
            except Exception as ex:
                
                # trace parsing exceptions.
                _logsi.LogException(str(ex), ex, logToSystemLogger=False)
                
            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def _GetArtistInfoAboutLink(
        self, 
        doc:Element,
        linkTitle:str, 
        ) -> str:
        """
        Searches artist about page for the specified link title and returns the HREF 
        attribute value if found; otherwise, null is returned.
        """
        result:str = None 
        
        # about information - link.
        # <a href="https://facebook.com/mercyme">
        #     <div>Facebook</div>
        # </a>
        attrXPath:str = './/div[text()="%s"]/parent::a' % linkTitle
        _logsi.LogVerbose("Element search '%s link': '%s'" % (linkTitle, attrXPath))
        attrElements:list[Element] = doc.xpath(attrXPath)
        for elm in attrElements:
            _logsi.LogObject(SILevel.Verbose, "Element match: '%s'" % attrXPath, elm)
            attrValue:str = elm.get('href', None)
            if attrValue is not None:
                result = attrValue
                break
            
        return result
                

    def GetArtistRelatedArtists(
        self, 
        artistId:str=None, 
        sortResult:bool=True,
        ) -> list[Artist]:
        """
        <span class="deprecated">
            DEPRECATED - api endpoint no longer supported by Spotify as of 2024/11/27 for unauthorized Spotify Developer Applications.
            The api endpoint IS still supported by Spotify for authorized Spotify Developer Applications.
            More information about the deprecated functionality can be found on the 
            <a href="https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api" target="_blank">Spotify Developer Forum Blog</a>
            page.
        </span>       
        
        Get Spotify catalog information about artists similar to a given artist.  
        Similarity is based on analysis of the Spotify community's listening history.
        
        Args:
            artistId (str):  
                The Spotify ID of the artist.  
                Example: `6APm8EjxOHSYM5B4i3vT3q`
                If null, the currently playing artist uri id value is used; a Spotify Free or Premium account 
                is required to correctly read the currently playing context.
            sortResult (bool):
                True to sort the items by name; otherwise, False to leave the items in the same order they 
                were returned in by the Spotify Web API.  
                Default: True
                
        Returns:
            A list of `Artist` objects that contain the artist details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetArtistRelatedArtists.py
        ```
        </details>
        """
        apiMethodName:str = 'GetArtistRelatedArtists'
        apiMethodParms:SIMethodParmListContext = None
        result:list[Artist] = []
        
        try:

            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("artistId", artistId)
            apiMethodParms.AppendKeyValue("sortResult", sortResult)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get Spotify catalog information about artists similar to a given artist", apiMethodParms)
            
            # are spotify web player credentials configured? if so, then we will use them to create
            # an elevated authorization access token for the Spotify Web API endpoint call.
            accessTokenHeaderValue:str = self._GetSpotifyWebPlayerTokenHeaderValue()

            # if spotify web player credentials not configured then we are done; the Spotify Web API
            # endpoint is no longer supported by unauthorized Spotify Developer Applications as of 2024/11/27.
            if (accessTokenHeaderValue is None):
                raise SpotifyApiError(SAAppMessages.MSG_SPOTIFY_DEPRECATED_ENDPOINT % apiMethodName)

            # validations.
            if sortResult is None: 
                sortResult = True

            # if artistId not specified, then return currently playing artist id value.
            if (artistId is None) or (len(artistId.strip()) == 0):
                uri = self.GetPlayerNowPlayingArtistUri()
                if uri is not None:
                    artistId = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'artistId'), logsi=_logsi)

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/artists/{id}/related-artists'.format(id=artistId))
            msg.RequestHeaders[self.AuthToken.HeaderKey] = accessTokenHeaderValue or self.AuthToken.HeaderValue
            self.MakeRequest('GET', msg)

            # process results.
            items = msg.ResponseData.get('artists',None)
            if items is not None:
                for item in items:
                    result.append(Artist(root=item))
        
            # sort result items.
            if (len(result) > 0):
                if (sortResult is True):
                    result.sort(key=lambda x: (x.Name or "").lower(), reverse=False)
        
            # trace.
            _logsi.LogArray(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, 'list[Artist]'), result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetArtists(
        self, 
        ids:list[str], 
        ) -> list[Artist]:
        """
        Get Spotify catalog information for several artists based on their Spotify IDs.
        
        Args:
            ids (list[str]):  
                A comma-separated list of the Spotify IDs for the artists.  
                Maximum: 50 IDs.  
                Example: `2CIMQHirSU0MQqyYHq0eOx,1vCWHaC5f2uS3yhpwWbIA6`
                
        Returns:
            A list of `Artist` objects that contain the artist details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetArtists.py
        ```
        </details>
        """
        apiMethodName:str = 'GetArtists'
        apiMethodParms:SIMethodParmListContext = None
        result:list[Artist] = []
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get Spotify catalog information for multiple artists", apiMethodParms)
                
            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'ids': ids
            }

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/artists')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)

            # process results.
            items = msg.ResponseData.get('artists',None)
            if items is not None:
                for item in items:
                    result.append(Artist(root=item))
        
            # trace.
            _logsi.LogArray(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, 'list[Artist]'), result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetArtistsFollowed(
        self, 
        after:str=None,
        limit:int=20, 
        limitTotal:int=None,
        sortResult:bool=True,
        ) -> ArtistPage:
        """
        Get the current user's followed artists.
        
        Args:
            after (str):
                The last artist ID retrieved from the previous request, or null for
                the first request.  
                Example: `6APm8EjxOHSYM5B4i3vT3q`  
            limit (int):
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
            sortResult (bool):
                True to sort the items by name; otherwise, False to leave the items in the same order they 
                were returned in by the Spotify Web API.  
                Default: True
                
        Returns:
            An `ArtistPage` object of matching results.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetArtistsFollowed.py
        ```
        </details>
        <details>
          <summary>Sample Code - Auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetArtistsFollowed_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'GetArtistsFollowed'
        apiMethodParms:SIMethodParmListContext = None
        result:ArtistPage = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("after", after)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            apiMethodParms.AppendKeyValue("sortResult", sortResult)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get the current user's followed artists", apiMethodParms)
                
            # validations.
            if limit is None: 
                limit = 20
            if not isinstance(limitTotal, int):
                limitTotal = 0
            if sortResult is None: 
                sortResult = True
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = ArtistPage()

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'type': SpotifyMediaTypes.ARTIST.value,
                'limit': limit,
            }
            if after is not None:
                urlParms['after'] = after

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/following')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                item:dict = msg.ResponseData.get('artists',{})
                if item is not None:
                    pageObj = ArtistPage(root=item)
                    
                    # trace.
                    _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:Artist
                    for item in pageObj.Items:
                        result.Items.append(item)
                        result.Limit = result.ItemsCount
                        if result.ItemsCount >= limitTotal:
                            break
                        
                    # force an AFTER cursor key to be present in the url parameters so that the
                    # paging logic can modify it correctly, as the AFTER key may not have been present
                    # on the initial request.
                    if 'after' not in urlParms.keys():
                        urlParms['after'] = 'after_value'
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithCursor(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break
                    
            # update result object with final paging details.
            result.Total = pageObj.Total
            result.CursorAfter = pageObj.CursorAfter
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # sort result items.
            if (len(result.Items) > 0):
                if (sortResult is True):
                    result.Items.sort(key=lambda x: (x.Name or "").lower(), reverse=False)
        
            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetArtistTopTracks(
        self, 
        artistId:str=None, 
        market:str=None, 
        sortResult:bool=True,
        ) -> list[Track]:
        """
        Get Spotify catalog information about an artist's top tracks by country.
        
        Args:
            artistId (str):  
                The Spotify ID of the artist.  
                Example: `6APm8EjxOHSYM5B4i3vT3q`
                If null, the currently playing artist uri id value is used; a Spotify Free or Premium account 
                is required to correctly read the currently playing context.
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
            sortResult (bool):
                True to sort the items by name; otherwise, False to leave the items in the same order they 
                were returned in by the Spotify Web API.  
                Default: True
                
        Returns:
            A list of `Track` objects that contain the track details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetArtistTopTracks.py
        ```
        </details>
        """
        apiMethodName:str = 'GetArtistTopTracks'
        apiMethodParms:SIMethodParmListContext = None
        result:list[Artist] = []
        
        try:

            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("artistId", artistId)
            apiMethodParms.AppendKeyValue("market", market)
            apiMethodParms.AppendKeyValue("sortResult", sortResult)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get Spotify catalog information about an artist's top tracks", apiMethodParms)
                
            # validations.
            if sortResult is None: 
                sortResult = True
            
            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market)

            # if artistId not specified, then return currently playing artist id value.
            if (artistId is None) or (len(artistId.strip()) == 0):
                uri = self.GetPlayerNowPlayingArtistUri()
                if uri is not None:
                    artistId = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'artistId'), logsi=_logsi)

            # build spotify web api request parameters.
            urlParms:dict = {}
            if market is not None:
                urlParms['market'] = market

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/artists/{id}/top-tracks'.format(id=artistId))
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)

            # process results.
            items = msg.ResponseData.get('tracks',None)
            if items is not None:
                for item in items:
                    result.append(Track(root=item))
        
            # sort result items.
            if (len(result) > 0):
                if (sortResult is True):
                    result.sort(key=lambda x: (x.Name or "").lower(), reverse=False)
        
            # trace.
            _logsi.LogArray(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, 'list[Track]'), result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetAudiobook(
        self, 
        audiobookId:str=None, 
        market:str=None,
        ) -> Audiobook:
        """
        Get Spotify catalog information for a single audiobook.  
        
        Audiobooks are only available within the US, UK, Canada, Ireland, New Zealand and Australia markets.
        
        Args:
            audiobookId (str):  
                The Spotify ID for the audiobook.
                Example: `74aydHJKgYz3AIq3jjBSv1`
                If null, the currently playing audiobook uri id value is used; a Spotify Free or Premium account 
                is required to correctly read the currently playing context.
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
                
        Returns:
            A `Audiobook` object that contain the audiobook details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        Important policy notes:  
        - Spotify content may not be downloaded.  
        - Keep visual content in its original form.  
        - Ensure content attribution.  
        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetAudiobook.py
        ```
          <summary>Sample Code - NowPlaying</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetAudiobook_NowPlaying.py
        ```
        </details>
        """
        apiMethodName:str = 'GetAudiobook'
        apiMethodParms:SIMethodParmListContext = None
        result:Audiobook = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("audiobookId", audiobookId)
            apiMethodParms.AppendKeyValue("market", market)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get Spotify catalog information for a single audiobook", apiMethodParms)
                
            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market)

            # if audiobookId not specified, then return currently playing audiobook id value.
            if (audiobookId is None) or (len(audiobookId.strip()) == 0):
                uri = self.GetPlayerNowPlayingAudiobookUri()
                if uri is not None:
                    audiobookId = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'audiobookId'), logsi=_logsi)

            # build spotify web api request parameters.
            urlParms:dict = {}
            if market is not None:
                urlParms['market'] = market

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/audiobooks/{id}'.format(id=audiobookId))
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)

            # process results.
            result = Audiobook(root=msg.ResponseData)
        
            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetAudiobookChapters(
        self, 
        audiobookId:str=None, 
        limit:int=20, 
        offset:int=0,
        market:str=None,
        limitTotal:int=None
        ) -> ChapterPageSimplified:
        """
        Get Spotify catalog information about an audiobook's chapters.
        
        Optional parameters can be used to limit the number of chapters returned.
        
        Args:
            audiobookId (str):  
                The Spotify ID for the audiobook.
                Example: `74aydHJKgYz3AIq3jjBSv1`
                If null, the currently playing audiobook uri id value is used; a Spotify Free or Premium account 
                is required to correctly read the currently playing context.
            limit (int):  
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            offset (int):  
                The index of the first item to return; use with limit to get the next set of items.  
                Default: 0 (the first item).  
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
                
        Returns:
            A `ChapterPageSimplified` object that contains simplified chapter information for the audiobook Id.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetAudiobookChapters.py
        ```
        </details>
        <details>
          <summary>Sample Code - Auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetAudiobookChapters_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'GetAudiobookChapters'
        apiMethodParms:SIMethodParmListContext = None
        result:ChapterPageSimplified = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("audiobookId", audiobookId)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("offset", offset)
            apiMethodParms.AppendKeyValue("market", market)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get Spotify catalog information about an audiobook's chapters", apiMethodParms)
                
            # validations.
            if limit is None: 
                limit = 20
            if offset is None: 
                offset = 0
            if not isinstance(limitTotal, int):
                limitTotal = 0
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = ChapterPageSimplified()

            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market)

            # if audiobookId not specified, then return currently playing audiobook id value.
            if (audiobookId is None) or (len(audiobookId.strip()) == 0):
                uri = self.GetPlayerNowPlayingAudiobookUri()
                if uri is not None:
                    audiobookId = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'audiobookId'), logsi=_logsi)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'limit': limit,
                'offset': offset,
            }
            if market is not None:
                urlParms['market'] = market

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/audiobooks/{id}/chapters'.format(id=audiobookId))
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                pageObj = ChapterPageSimplified(root=msg.ResponseData)

                # trace.
                _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:ChapterSimplified
                    for item in pageObj.Items:
                        result.Items.append(item)
                        result.Limit = result.ItemsCount
                        if result.ItemsCount >= limitTotal:
                            break
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithOffset(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break

            # update result object with final paging details.
            result.Total = pageObj.Total
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # no sorting, as chapters are in playable order.

            # trace.
            _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE + result.PagingInfo) % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetAudiobookFavorites(
        self, 
        limit:int=20, 
        offset:int=0,
        limitTotal:int=None,
        sortResult:bool=True,
        ) -> AudiobookPageSimplified:
        """
        Get a list of the audiobooks saved in the current Spotify user's 'Your Library'.
        
        This method requires the `user-library-read` scope.

        Args:
            limit (int):
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            offset (int):
                The page index offset of the first item to return.  
                Use with limit to get the next set of items.  
                Default: 0 (the first item).  
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
            sortResult (bool):
                True to sort the items by name; otherwise, False to leave the items in the same order they 
                were returned in by the Spotify Web API.  
                Default: True
                
        Returns:
            An `AudiobookPageSimplified` object that contains saved audiobook information.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetAudiobookFavorites.py
        ```
        </details>
        <details>
          <summary>Sample Code - Auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetAudiobookFavorites_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'GetAudiobookFavorites'
        apiMethodParms:SIMethodParmListContext = None
        result:AudiobookPageSimplified = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("offset", offset)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            apiMethodParms.AppendKeyValue("sortResult", sortResult)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get a list of the users audiobook favorites", apiMethodParms)
                
            # validations.
            if limit is None: 
                limit = 20
            if offset is None: 
                offset = 0
            if not isinstance(limitTotal, int):
                limitTotal = 0
            if sortResult is None: 
                sortResult = True
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = AudiobookPageSimplified()

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'limit': limit,
                'offset': offset,
            }

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/audiobooks')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                pageObj = AudiobookPageSimplified(root=msg.ResponseData)
            
                # trace.
                _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:AudiobookSimplified
                    for item in pageObj.Items:
                        result.Items.append(item)
                        result.Limit = result.ItemsCount
                        if result.ItemsCount >= limitTotal:
                            break
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithOffset(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break

            # update result object with final paging details.
            result.Total = pageObj.Total
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # sort result items.
            if (len(result.Items) > 0):
                if (sortResult is True):
                    result.Items.sort(key=lambda x: (x.Name or "").lower(), reverse=False)

            # trace.
            _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE + result.PagingInfo) % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetAudiobooks(
        self, 
        ids:str, 
        market:str=None,
        ) -> list[AudiobookSimplified]:
        """
        Get Spotify catalog information for several audiobooks based on their Spotify IDs.
        
        Args:
            ids (str):  
                A comma-separated list of the Spotify IDs for the audiobooks.  
                Maximum: 50 IDs.  
                Example: `74aydHJKgYz3AIq3jjBSv1,2kbbNqAvJZxwGyCukHoTLA`
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
                
        Returns:
            A list of `AudiobookSimplified` objects that contain the audiobook details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        Important policy notes:  
        - Spotify content may not be downloaded.  
        - Keep visual content in its original form.  
        - Ensure content attribution.  
        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetAudiobooks.py
        ```
        </details>
        """
        apiMethodName:str = 'GetAudiobooks'
        apiMethodParms:SIMethodParmListContext = None
        result:list[AudiobookSimplified] = []
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            apiMethodParms.AppendKeyValue("market", market)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get Spotify catalog information for multiple audiobooks", apiMethodParms)
                
            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'ids': ids,
            }
            if market is not None:
                urlParms['market'] = market

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/audiobooks')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)

            # process results.
            items = msg.ResponseData.get('audiobooks',None)
            if items is not None:
                for item in items:
                    result.append(AudiobookSimplified(root=item))
        
            # trace.
            _logsi.LogArray(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, 'list[AudiobookSimplified]'), result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetBrowseCategory(
        self, 
        categoryId:str, 
        country:str=None, 
        locale:str=None,
        refresh:bool=True,
        ) -> Playlist:
        """
        Get a single category used to tag items in Spotify.
        
        Args:
            categoryId (str):  
                The Spotify category ID of the category.  
                Note that some category id's are common names (e.g. `toplists` = `Top Lists`), while others are
                unique identifiers (e.g. `0JQ5DAqbMKFDXXwE9BDJAr` = `Rock`).  
                Example: `toplists`
            country (str):
                A country: an ISO 3166-1 alpha-2 country code.  
                Provide this parameter if you want the list of returned items to be relevant to a 
                particular country. If omitted, the returned items will be relevant to all countries.  
                Example: `SE`
            locale (str):
                The desired language, consisting of a lowercase ISO 639-1 language code and an uppercase 
                ISO 3166-1 alpha-2 country code, joined by an underscore.  
                For example: `es_MX`, meaning "Spanish (Mexico)".  
                Provide this parameter if you want the results returned in a particular language (where available).  
                Note: if locale is not supplied, or if the specified language is not available, all strings will 
                be returned in the Spotify default language (American English). The locale parameter, combined with 
                the country parameter, may give odd results if not carefully matched. For example country=`SE` and
                locale=`de_DE` will return a list of categories relevant to Sweden but as German language strings.  
                Example: `sv_SE`  
            refresh (bool):
                True (default) to return real-time information from the spotify web api; otherwise, False to
                to return a cached value IF a call has been made to the `GetBrowseCategorys` method (which
                creates a caches list of `Category` objects).
        
        Returns:
            A `Category` object that contains the category details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        The `ConfigurationCache` is updated with the results of this method.  Use the
        `refresh` argument (with False value) to retrieve the cached value and avoid
        the spotify web api request.  This results in better performance.
                        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetBrowseCategory.py
        ```
        </details>
        """
        apiMethodName:str = 'GetBrowseCategory'
        apiMethodParms:SIMethodParmListContext = None
        result:Category = None
        cacheDesc:str = CACHE_SOURCE_CURRENT
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("categoryId", categoryId)
            apiMethodParms.AppendKeyValue("country", country)
            apiMethodParms.AppendKeyValue("locale", locale)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get a single category used to tag items in Spotify", apiMethodParms)
                
            # validations.
            if (refresh is None):
                refresh = True
                
            # can we use a cached value?
            cacheKey:str = "GetBrowseCategorys"
            if (not refresh) and (cacheKey in self._ConfigurationCache):
                
                # search the category cache by id.
                category:Category
                for category in self._ConfigurationCache[cacheKey]:
                    if category.Id == categoryId:
                        result = category
                        cacheDesc = CACHE_SOURCE_CACHED
                        break
                    
            # did we find a cached value?
            if result is None:

                # build spotify web api request parameters.
                urlParms:dict = {}
                if country is not None:
                    urlParms['country'] = '%s' % str(country)
                if locale is not None:
                    urlParms['locale'] = '%s' % str(locale)
            
                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/browse/categories/{category_id}'.format(category_id=categoryId))
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                result = Category(root=msg.ResponseData)
        
            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE_CACHED % (apiMethodName, type(result).__name__, cacheDesc), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetBrowseCategorys(
        self, 
        limit:int=20,
        offset:int=0,
        country:str=None,
        locale:str=None,
        limitTotal:int=None,
        sortResult:bool=True,
        ) -> CategoryPage:
        """
        Get categories used to tag items in Spotify.
        
        Args:
            limit (int):
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            offset (int):
                The page index offset of the first item to return.  
                Use with limit to get the next set of items.  
                Default: 0 (the first item).  
            country (str):
                A country: an ISO 3166-1 alpha-2 country code.  
                Provide this parameter if you want the list of returned items to be relevant to a 
                particular country. If omitted, the returned items will be relevant to all countries.  
                Example: `SE`
            locale (str):
                The desired language, consisting of a lowercase ISO 639-1 language code and an uppercase 
                ISO 3166-1 alpha-2 country code, joined by an underscore.  
                For example: `es_MX`, meaning "Spanish (Mexico)".  
                Provide this parameter if you want the results returned in a particular language (where available).  
                Note: if locale is not supplied, or if the specified language is not available, all strings will 
                be returned in the Spotify default language (American English). The locale parameter, combined with 
                the country parameter, may give odd results if not carefully matched. For example country=`SE` and
                locale=`de_DE` will return a list of categories relevant to Sweden but as German language strings.  
                Example: `sv_SE`  
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
            sortResult (bool):
                True to sort the items by name; otherwise, False to leave the items in the same order they 
                were returned in by the Spotify Web API.  
                Default: True
                
        Returns:
            A `CategoryPage` object that contains a page of category details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetBrowseCategorys.py
        ```
        </details>
        <details>
          <summary>Sample Code - Auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetBrowseCategorys_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'GetBrowseCategorys'
        apiMethodParms:SIMethodParmListContext = None
        result:CategoryPage = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("offset", offset)
            apiMethodParms.AppendKeyValue("country", country)
            apiMethodParms.AppendKeyValue("locale", locale)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            apiMethodParms.AppendKeyValue("sortResult", sortResult)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get a page of categories used to tag items in Spotify", apiMethodParms)
                
            # validations.
            if limit is None: 
                limit = 20
            if offset is None: 
                offset = 0
            if not isinstance(limitTotal, int):
                limitTotal = 0
            if sortResult is None: 
                sortResult = True
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = CategoryPage()

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'limit': limit,
                'offset': offset,
            }
            if country is not None:
                urlParms['country'] = str(country)
            if locale is not None:
                urlParms['locale'] = str(locale)

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/browse/categories')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                item:dict = msg.ResponseData.get('categories',None)
                if item is not None:
                    pageObj = CategoryPage(root=item)
            
                    # trace.
                    _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:Category
                    for item in pageObj.Items:
                        result.Items.append(item)
                        result.Limit = result.ItemsCount
                        if result.ItemsCount >= limitTotal:
                            break
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithOffset(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break

            # update result object with final paging details.
            result.Total = pageObj.Total
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # sort result items.
            if (len(result.Items) > 0):
                if (sortResult is True):
                    result.Items.sort(key=lambda x: (x.Name or "").lower(), reverse=False)
        
            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetBrowseCategorysList(
        self, 
        country:str=None,
        locale:str=None,
        refresh:bool=True,
        ) -> list[Category]:
        """
        Get a sorted list of ALL categories used to tag items in Spotify.
        
        Args:
            country (str):
                A country: an ISO 3166-1 alpha-2 country code.  
                Provide this parameter if you want the list of returned items to be relevant to a 
                particular country. If omitted, the returned items will be relevant to all countries.  
                Example: `SE`
            locale (str):
                The desired language, consisting of a lowercase ISO 639-1 language code and an uppercase 
                ISO 3166-1 alpha-2 country code, joined by an underscore.  
                For example: `es_MX`, meaning "Spanish (Mexico)".  
                Provide this parameter if you want the results returned in a particular language (where available).  
                Note: if locale is not supplied, or if the specified language is not available, all strings will 
                be returned in the Spotify default language (American English). The locale parameter, combined with 
                the country parameter, may give odd results if not carefully matched. For example country=`SE` and
                locale=`de_DE` will return a list of categories relevant to Sweden but as German language strings.  
                Example: `sv_SE`  
            refresh (bool):
                True to return real-time information from the spotify web api and
                update the cache; otherwise, False to just return the cached value.  
                Default is True.
                
        Returns:
            A `list[Category]` object that contains the list category details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        The `ConfigurationCache` is updated with the results of this method.  Use the
        `refresh` argument (with False value) to retrieve the cached value and avoid
        the spotify web api request.  This results in better performance.
                        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetBrowseCategorysList.py
        ```
        </details>
        """
        apiMethodName:str = 'GetBrowseCategorysList'
        apiMethodParms:SIMethodParmListContext = None
        result:list[Category] = []
        cacheDesc:str = CACHE_SOURCE_CURRENT
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("country", country)
            apiMethodParms.AppendKeyValue("locale", locale)
            apiMethodParms.AppendKeyValue("refresh", refresh)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get a sorted list of ALL browse categories", apiMethodParms)
                
            # validations.
            if (refresh is None):
                refresh = True
                
            # can we use the cached value?
            if (not refresh) and (apiMethodName in self._ConfigurationCache):
                
                result = self._ConfigurationCache[apiMethodName]
                cacheDesc = CACHE_SOURCE_CACHED
                
            else:
                
                # get all categories (return list is already sorted).
                pageObj:CategoryPage = self.GetBrowseCategorys(country=country, locale=locale, limitTotal=1000)

                # add category details to return list.
                category:Category
                for category in pageObj.Items:
                    result.append(category)
                                    
                # update cache.
                self._ConfigurationCache[apiMethodName] = result

            # trace.
            _logsi.LogArray(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE_CACHED % (apiMethodName, type(result).__name__, cacheDesc), result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetCategoryPlaylists(
        self, 
        categoryId:str,
        limit:int=20, 
        offset:int=0,
        country:str=None,
        limitTotal:int=None,
        sortResult:bool=True,
        ) -> Tuple[PlaylistPageSimplified, str]:
        """
        <span class="deprecated">
            DEPRECATED - api endpoint no longer supported by Spotify as of 2024/11/27 for unauthorized Spotify Developer Applications.
            The api endpoint IS still supported by Spotify for authorized Spotify Developer Applications.
            More information about the deprecated functionality can be found on the 
            <a href="https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api" target="_blank">Spotify Developer Forum Blog</a>
            page.
        </span>       
        
        Get a list of Spotify playlists tagged with a particular category.
        
        Args:
            categoryId (str):
                The Spotify category ID for the category.  
                Example: `dinner`
            limit (int):
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            offset (int):
                The page index offset of the first item to return.  
                Use with limit to get the next set of items.  
                Default: 0 (the first item).  
            country (str):
                A country: an ISO 3166-1 alpha-2 country code.  
                Provide this parameter if you want the list of returned items to be relevant to a 
                particular country. If omitted, the returned items will be relevant to all countries.  
                Example: `SE`
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
            sortResult (bool):
                True to sort the items by name; otherwise, False to leave the items in the same order they 
                were returned in by the Spotify Web API.  
                Default: True
                
        Returns:
            A tuple of 2 objects:  
            - `PlaylistPageSimplified` object that contains playlist information.  
            - string that describes what was returned (e.g. 'Popular Playlists').
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.
                
        The following are special undocumented category ID's that I have found:  
        - 0JQ5DAt0tbjZptfcdMSKl3: Made For You  

        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetCategoryPlaylists.py
        ```
        </details>
        <details>
          <summary>Sample Code - Auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetCategoryPlaylists_AutoPaging.py
        ```
        </details>
        <details>
          <summary>Sample Code - Made For You Playlists</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetCategoryPlaylists_MadeForYou.py
        ```
        </details>
        """
        apiMethodName:str = 'GetCategoryPlaylists'
        apiMethodParms:SIMethodParmListContext = None
        result:PlaylistPageSimplified = None
        resultMessage:str = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("categoryId", categoryId)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("offset", offset)
            apiMethodParms.AppendKeyValue("country", country)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            apiMethodParms.AppendKeyValue("sortResult", sortResult)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get a list of Spotify playlists tagged with a particular category", apiMethodParms)
                
            # are spotify web player credentials configured? if so, then we will use them to create
            # an elevated authorization access token for the Spotify Web API endpoint call.
            accessTokenHeaderValue:str = self._GetSpotifyWebPlayerTokenHeaderValue()

            # if spotify web player credentials not configured then we are done; the Spotify Web API
            # endpoint is no longer supported by unauthorized Spotify Developer Applications as of 2024/11/27.
            if (accessTokenHeaderValue is None):
                raise SpotifyApiError(SAAppMessages.MSG_SPOTIFY_DEPRECATED_ENDPOINT % apiMethodName)

            # validations.
            if limit is None: 
                limit = 20
            if offset is None: 
                offset = 0
            if not isinstance(limitTotal, int):
                limitTotal = 0
            if sortResult is None: 
                sortResult = True
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = PlaylistPageSimplified()

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'category_id': categoryId,
                'limit': limit,
                'offset': offset,
            }
            if country is not None:
                urlParms['country'] = str(country)

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/browse/categories/{category_id}/playlists'.format(category_id=categoryId))
                msg.RequestHeaders[self.AuthToken.HeaderKey] = accessTokenHeaderValue or self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                resultMessage = msg.ResponseData.get('message','unknown')
                item = msg.ResponseData.get('playlists',None)
                if item is not None:
                    pageObj = PlaylistPageSimplified(root=item)
            
                    # trace.
                    _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:PlaylistSimplified
                    for item in pageObj.Items:
                        # for some reason, Spotify returns duplicates so we have to check before we add.
                        if not result.ContainsId(item.Id):
                            result.Items.append(item)
                            result.Limit = result.ItemsCount
                            if result.ItemsCount >= limitTotal:
                                break
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithOffset(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break

            # update result object with final paging details.
            result.Total = pageObj.Total
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # sort result items.
            if (len(result.Items) > 0):
                if (sortResult is True):
                    result.Items.sort(key=lambda x: (x.Name or "").lower(), reverse=False)

            # trace.
            _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE + result.PagingInfo) % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result, resultMessage

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetChapter(
        self, 
        chapterId:str=None, 
        market:str=None,
        ignoreResponseErrors:bool=False,
        ) -> Chapter:
        """
        Get Spotify catalog information for a single audiobook chapter identified by its unique Spotify ID.
        
        This method requires the `user-read-playback-position` scope.
        
        Args:
            chapterId (str):  
                The Spotify ID for the chapter.
                Example: `0D5wENdkdwbqlrHoaJ9g29`
                If null, the currently playing chapter uri id value is used; a Spotify Free or Premium account 
                is required to correctly read the currently playing context.
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
            ignoreResponseErrors (bool):
                True to ignore any request response errors that occur; otherwise, an exception will be thrown
                if a response error is detected (default).
                
        Returns:
            An `Chapter` object that contain the chapter details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        Important policy notes:  
        - Spotify content may not be downloaded.  
        - Keep visual content in its original form.  
        - Ensure content attribution.  
        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetChapter.py
        ```
        </details>
        """
        apiMethodName:str = 'GetChapter'
        apiMethodParms:SIMethodParmListContext = None
        result:Chapter = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("chapterId", chapterId)
            apiMethodParms.AppendKeyValue("market", market)
            apiMethodParms.AppendKeyValue("ignoreResponseErrors", ignoreResponseErrors)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get Spotify catalog information for a single audiobook chapter", apiMethodParms)
                
            # validations.
            if (ignoreResponseErrors is None):
                ignoreResponseErrors = False
                
            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market)

            # if ids not specified, then return currently playing id value.
            if (chapterId is None) or (len(chapterId.strip()) == 0):
                uri = self.GetPlayerNowPlayingUri(SpotifyMediaTypes.EPISODE.value)
                if uri is not None:
                    chapterId = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'chapterId'), logsi=_logsi)

            # build spotify web api request parameters.
            urlParms:dict = {}
            if market is not None:
                urlParms['market'] = market

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/chapters/{id}'.format(id=chapterId))
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            msg.IgnoreResponseErrors = ignoreResponseErrors
            self.MakeRequest('GET', msg)

            # process results.
            result = Chapter(root=msg.ResponseData)
        
            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetChapters(
        self, 
        ids:str, 
        market:str=None,
        ) -> list[Chapter]:
        """
        Get Spotify catalog information for several chapters based on their Spotify IDs.
        
        Args:
            ids (str):  
                A comma-separated list of the Spotify IDs for the chapters.  
                Maximum: 50 IDs.  
                Example: `5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ`
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
                
        Returns:
            A list of `Chapter` objects that contain the chapter details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        Important policy notes:  
        - Spotify content may not be downloaded.  
        - Keep visual content in its original form.  
        - Ensure content attribution.  
        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetChapters.py
        ```
        </details>
        """
        apiMethodName:str = 'GetChapters'
        apiMethodParms:SIMethodParmListContext = None
        result:list[Chapter] = []
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            apiMethodParms.AppendKeyValue("market", market)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get Spotify catalog information for multiple chapters", apiMethodParms)
                
            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'ids': ids,
            }
            if market is not None:
                urlParms['market'] = market

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/chapters')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)

            # process results.
            items = msg.ResponseData.get('chapters',None)
            if items is not None:
                for item in items:
                    result.append(Chapter(root=item))
        
            # trace.
            _logsi.LogArray(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, 'list[Chapter]'), result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetCoverImageFile(
        self,
        imageUrl:Union[str,list],
        outputPath:str,
        desiredWidth:int=None,
        ) -> None:
        """
        Gets the contents of an image url and transfers the contents to the local file system.

        Args:
            imageUrl (str | list[ImageObject]):
                The cover image to retrieve - can be one of the following:
                - a url string that points to the exact cover image to transfer.  
                - a list of `ImageObject` items that contain the cover art for the media in 
                  various sizes, usually widest first.
            outputPath (str):
                Fully-qualified path to store the downloaded image to.  
            desiredWidth (int):
                A desired resolution width to return (if found); if not found, then the
                highest resolution is returned.  
                This argument is ignored if the `images` argument is not an `ImageObject` list.

        The output path supports the replacement of the following keyword parameters:
        - `{dotfileextn}` - a "." followed by the file extension based on response content 
          type (for known types: JPG,PNG,APNG,BMP,GIF).  
        - `{imagewidth}` - the resolved width value, if `imageUrl` argument is of type list[ImageObject].

        The Spotify Web API normally returns a list of `ImageObject` items in its various
        endpoints.  The highest resolution image is usually the first list item, but the
        order is not guarenteed (e.g. `GetShowFavorites`).

        This method should only be used to download images for playlists that contain 
        public domain images.  It should not be used to download copyright protected images, 
        as that would violate the Spotify Web API Terms of Service.
        """
        apiMethodName:str = 'GetCoverImageFile'
        apiMethodParms:SIMethodParmListContext = None
        response:HTTPResponse = None
        url:str = None
        imageWidth:int = 0

        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("imageUrl", imageUrl)
            apiMethodParms.AppendKeyValue("outputPath", outputPath)
            apiMethodParms.AppendKeyValue("desiredWidth", desiredWidth)
            _logsi.LogMethodParmList(SILevel.Verbose, "Downloading cover image url content", apiMethodParms)

            # validations.
            if (imageUrl is None):
                raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'imageUrl'), logsi=_logsi)
            if (outputPath is None):
                raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'outputPath'), logsi=_logsi)

            # was an image list specified?
            if (isinstance(imageUrl, list)):

                # return the highest resolution order image from a list of `ImageObject` items.
                # this will return None if images argument was none or empty.
                url = ImageObject.GetImageHighestResolution(imageUrl, desiredWidth)
                imageWidth = ImageObject.GetImageHighestResolutionWidth(imageUrl, desiredWidth)
                if (url) is None:
                    _logsi.LogVerbose("List of ImageObjects was not specified, or was empty")
                    return
                imageUrl = url

            # download content from the selected image url.
            _logsi.LogVerbose("Downloading cover image url (width=%s): \"%s\"" % (desiredWidth, imageUrl))
            response = self._Manager.request("GET", imageUrl)

            # trace.
            if _logsi.IsOn(SILevel.Debug):
                _logsi.LogObject(SILevel.Debug, "SpotifyClient http response [%s-%s]: '%s' (response)" % (response.status, response.reason, imageUrl), response)
                if (response.headers):
                    _logsi.LogCollection(SILevel.Debug, "SpotifyClient http response [%s-%s]: '%s' (headers)" % (response.status, response.reason, imageUrl), response.headers.items())

            # do response headers contain a content-type value?
            # if so, then set file extension based on content type.
            contentType:str = None
            outputFileExtn:str = ".jpg"
            if response.headers:
                if 'content-type' in response.headers:
                    contentType = response.headers['content-type'] + ""
                    if (contentType.find("image/jpeg") != -1):
                        outputFileExtn = ".jpg"
                    elif (contentType.find("image/bmp") != -1):
                        outputFileExtn = ".bmp"
                    elif (contentType.find("image/png") != -1):
                        outputFileExtn = ".png"
                    elif (contentType.find("image/apng") != -1):
                        outputFileExtn = ".apng"
                    elif (contentType.find("image/gif") != -1):
                        outputFileExtn = ".gif"
                    else:
                        outputFileExtn = ".jpg"

            # do we have response data?
            if len(response.data) == 0:
                    
                # some requests will not return a response, which is ok.
                _logsi.LogVerbose("SpotifyClient http response [%s-%s]: '%s' (no data)" % (response.status, response.reason, imageUrl))

            else:
                    
                # override file extension based on content type (if desired).
                outputPath = outputPath.replace("{dotfileextn}", outputFileExtn)
                outputPath = outputPath.replace("{imagewidth}", str(imageWidth))

                # write data to output file.
                f = open(outputPath,'wb') 
                f.write(response.data) 
                f.close() 

                # response is raw image data.
                _logsi.LogJpegFile(SILevel.Verbose, "SpotifyClient http response [%s-%s]: '%s' (imagefile)" % (response.status, response.reason, imageUrl), outputPath)

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # close the response (if needed).
            if response is not None:
                if response.closed == False:
                    response.close()

            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)
   

    def GetDevicePlaybackState(
        self, 
        deviceId:str|SpotifyConnectDevice|None=None,
        ) -> PlayerPlayState:
        """
        Get information about the current playback state, including track or episode, and progress. 
        If the Spotify Web API reports nothing as playing, then the device-specific playback state
        is returned (if one exists).  

        This method requires the `user-read-playback-state` scope.
        
        This is not part of the Spotify Web API specification.
       
        Args:
            deviceId (str | SpotifyConnectDevice) | None):
                The target player device identifier.
                This could be an id, name, a default device indicator (e.g. "*"), a 
                SpotifyConnectDevice object, or null to utilize the active player device.
                A device is considered resolved if a SpotifyConnectDevice object is passed
                for this argument.  An exception will be raised if the argument value could 
                not be resolved.
                Examples are `0d1841b0976bae2a3a310dd74c0f3df354899bc8`, `Office`, `*`, None.  
                
        Returns:
            A `PlayerPlayState` object that contains player state details as well as
            currently playing content.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetDevicePlaybackState.py
        ```
        </details>
        """
        apiMethodName:str = 'GetDevicePlaybackState'
        apiMethodParms:SIMethodParmListContext = None
        result:PlayerPlayState = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("deviceId", deviceId)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get the current Spotify playback state, with device fallback", apiMethodParms)

            # resolve the device object; no need to activate it for what we want here.
            # this will also set the currently active device in the devices cache, as well as
            # add the playstate to the configuration cache.
            scDevice:SpotifyConnectDevice = self._ResolveDeviceObject(deviceId, activateDevice=False)

            # get cached Spotify Web API playerstate (_ResolveDeviceObject method just refreshed it).
            result = self.GetPlayerPlaybackState(refresh=False)

            # did Spotify return a playstate?
            if (result.IsEmpty):

                # no; we will now check for a device-specific playstate.

                # is this a Sonos device?
                if (scDevice is not None) and (scDevice.IsSonos):

                    # get Sonos playback state via Sonos Controller instance.
                    playerStateSonos:PlayerPlayState = self.GetPlayerPlaybackStateSonos(scDevice)

                    # return the device playstate.
                    _logsi.LogVerbose("Sonos device %s playstate will be returned" % (scDevice.Title))
                    result = playerStateSonos

                    # did Sonos Controller instance return a playstate?
                    # if so, then update the player last played info if something is playing.
                    if (not result.IsEmpty):
                        if (result._IsPlaying) and (result._Item is not None):
                            self._PlayerLastPlayedInfo = PlayerLastPlayedInfo(result)
                            _logsi.LogObject(SILevel.Verbose, "Updated internal PlayerLastPlayedInfo (for Sonos): %s" % self._PlayerLastPlayedInfo.Summary, self._PlayerLastPlayedInfo, excludeNonPublic=True)

            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetEpisode(
        self, 
        episodeId:str=None, 
        market:str=None,
        ) -> Episode:
        """
        Get Spotify catalog information for a single episode identified by its unique Spotify ID.
        
        This method requires the `user-read-playback-position` scope.
        
        Args:
            episodeId (str):  
                The Spotify ID for the episode.
                Example: `26c0zVyOv1lzfYpBXdh1zC`
                If null, the currently playing episode uri id value is used; a Spotify Free or Premium account 
                is required to correctly read the currently playing context.
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
                
        Returns:
            An `Episode` object that contain the episode details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        Important policy notes:  
        - Spotify content may not be downloaded.  
        - Keep visual content in its original form.  
        - Ensure content attribution.  
        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetEpisode.py
        ```
        </details>
        """
        apiMethodName:str = 'GetEpisode'
        apiMethodParms:SIMethodParmListContext = None
        result:Episode = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("episodeId", episodeId)
            apiMethodParms.AppendKeyValue("market", market)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get Spotify catalog information for a single episode", apiMethodParms)
                
            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market)

            # if ids not specified, then return currently playing id value.
            if (episodeId is None) or (len(episodeId.strip()) == 0):
                uri = self.GetPlayerNowPlayingUri(SpotifyMediaTypes.EPISODE.value)
                if uri is not None:
                    episodeId = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'episodeId'), logsi=_logsi)

            # build spotify web api request parameters.
            urlParms:dict = {}
            if market is not None:
                urlParms['market'] = market

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/episodes/{id}'.format(id=episodeId))
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)

            # process results.
            result = Episode(root=msg.ResponseData)
        
            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetEpisodeFavorites(
        self, 
        limit:int=20, 
        offset:int=0,
        limitTotal:int=None,
        sortResult:bool=True,
        ) -> EpisodePageSaved:
        """
        Get a list of the episodes saved in the current Spotify user's 'Your Library'.
        
        This method requires the `user-library-read` scope.

        Args:
            limit (int):
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            offset (int):
                The page index offset of the first item to return.  
                Use with limit to get the next set of items.  
                Default: 0 (the first item).  
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
            sortResult (bool):
                True to sort the items by name; otherwise, False to leave the items in the same order they 
                were returned in by the Spotify Web API.  
                Default: True
                
        Returns:
            An `EpisodePageSaved` object that contains saved episode information.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetEpisodeFavorites.py
        ```
        </details>
        <details>
          <summary>Sample Code - Auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetEpisodeFavorites_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'GetEpisodeFavorites'
        apiMethodParms:SIMethodParmListContext = None
        result:EpisodePageSaved = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("offset", offset)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            apiMethodParms.AppendKeyValue("sortResult", sortResult)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get a list of the users episode favorites", apiMethodParms)
                
            # validations.
            if limit is None: 
                limit = 20
            if offset is None: 
                offset = 0
            if not isinstance(limitTotal, int):
                limitTotal = 0
            if sortResult is None: 
                sortResult = True
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = EpisodePageSaved()

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'limit': limit,
                'offset': offset,
            }

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/episodes')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                pageObj = EpisodePageSaved(root=msg.ResponseData)
            
                # trace.
                _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:EpisodeSaved
                    for item in pageObj.Items:
                        # sometimes spotify api returns items with no information; discard these!
                        if (item.Episode is not None) and (item.Episode.Uri is not None):
                            result.Items.append(item)
                            result.Limit = result.ItemsCount
                            if result.ItemsCount >= limitTotal:
                                break
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithOffset(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break

            # update result object with final paging details.
            result.Total = pageObj.Total
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # sort result items.
            if (len(result.Items) > 0):
                if (sortResult is True):
                    result.Items.sort(key=lambda x: (x.Episode.Name or "").lower(), reverse=False)
                else:
                    result.Items.sort(key=lambda x: (x.AddedAt or "").lower(), reverse=True)
            
            # trace.
            _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE + result.PagingInfo) % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetEpisodes(
        self, 
        ids:str, 
        market:str=None,
        ) -> list[Episode]:
        """
        Get Spotify catalog information for several episodes based on their Spotify IDs.
        
        Args:
            ids (str):  
                A comma-separated list of the Spotify IDs for the episodes.  
                Maximum: 50 IDs.  
                Example: `5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ`
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
                
        Returns:
            A list of `Episode` objects that contain the episode details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        Important policy notes:  
        - Spotify content may not be downloaded.  
        - Keep visual content in its original form.  
        - Ensure content attribution.  
        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetEpisodes.py
        ```
        </details>
        """
        apiMethodName:str = 'GetEpisodes'
        apiMethodParms:SIMethodParmListContext = None
        result:list[Episode] = []
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            apiMethodParms.AppendKeyValue("market", market)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get Spotify catalog information for multiple episodes", apiMethodParms)
                
            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'ids': ids,
            }
            if market is not None:
                urlParms['market'] = market

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/episodes')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)

            # process results.
            items = msg.ResponseData.get('episodes',None)
            if items is not None:
                for item in items:
                    result.append(Episode(root=item))
        
            # trace.
            _logsi.LogArray(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, 'list[Episode]'), result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetFeaturedPlaylists(
        self, 
        limit:int=20, 
        offset:int=0,
        country:str=None,
        locale:str=None,
        timestamp:str=None,
        limitTotal:int=None,
        sortResult:bool=True,
        ) -> Tuple[PlaylistPageSimplified, str]:
        """
        <span class="deprecated">
            DEPRECATED - api endpoint no longer supported by Spotify as of 2024/11/27 for unauthorized Spotify Developer Applications.
            The api endpoint IS still supported by Spotify for authorized Spotify Developer Applications.
            More information about the deprecated functionality can be found on the 
            <a href="https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api" target="_blank">Spotify Developer Forum Blog</a>
            page.
        </span>       
        
        Get a list of Spotify featured playlists (shown, for example, on a Spotify player's 'Browse' tab).
        
        Args:
            limit (int):
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            offset (int):
                The page index offset of the first item to return.  
                Use with limit to get the next set of items.  
                Default: 0 (the first item).  
            country (str):
                A country: an ISO 3166-1 alpha-2 country code.  
                Provide this parameter if you want the list of returned items to be relevant to a 
                particular country. If omitted, the returned items will be relevant to all countries.  
                Example: `SE`
            locale (str):
                The desired language, consisting of a lowercase ISO 639-1 language code and an uppercase 
                ISO 3166-1 alpha-2 country code, joined by an underscore.  
                For example: `es_MX`, meaning "Spanish (Mexico)".  
                Provide this parameter if you want the results returned in a particular language (where available).  
                Note: if locale is not supplied, or if the specified language is not available, all strings will 
                be returned in the Spotify default language (American English). The locale parameter, combined with 
                the country parameter, may give odd results if not carefully matched. For example country=`SE` and
                locale=`de_DE` will return a list of categories relevant to Sweden but as German language strings.  
                Example: `sv_SE`
            timestamp (str):
                A timestamp in ISO 8601 format: yyyy-MM-ddTHH:mm:ss.  
                Use this parameter to specify the user's local time to get results tailored for that specific date 
                and time in the day. If not provided, the response defaults to the current UTC time. 
                Example: `2023-10-23T09:00:00` for a user whose local time is 9AM. 
                If there were no featured playlists (or there is no data) at the specified time, the response will 
                revert to the current UTC time.
                Example: `2023-10-23T09:00:00`
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
            sortResult (bool):
                True to sort the items by name; otherwise, False to leave the items in the same order they 
                were returned in by the Spotify Web API.  
                Default: True
                
        Returns:
            A tuple of 2 objects:  
            - `PlaylistPageSimplified` object that contains playlist information.  
            - string that describes what was returned (e.g. 'Popular Playlists').
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetFeaturedPlaylists.py
        ```
        </details>
        <details>
          <summary>Sample Code - Auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetFeaturedPlaylists_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'GetFeaturedPlaylists'
        apiMethodParms:SIMethodParmListContext = None
        result:PlaylistPageSimplified = None
        resultMessage:str = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("offset", offset)
            apiMethodParms.AppendKeyValue("country", country)
            apiMethodParms.AppendKeyValue("locale", locale)
            apiMethodParms.AppendKeyValue("timestamp", timestamp)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            apiMethodParms.AppendKeyValue("sortResult", sortResult)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get a list of Spotify featured playlists", apiMethodParms)
                
            # are spotify web player credentials configured? if so, then we will use them to create
            # an elevated authorization access token for the Spotify Web API endpoint call.
            accessTokenHeaderValue:str = self._GetSpotifyWebPlayerTokenHeaderValue()

            # if spotify web player credentials not configured then we are done; the Spotify Web API
            # endpoint is no longer supported by unauthorized Spotify Developer Applications as of 2024/11/27.
            if (accessTokenHeaderValue is None):
                raise SpotifyApiError(SAAppMessages.MSG_SPOTIFY_DEPRECATED_ENDPOINT % apiMethodName)

            # validations.
            if limit is None: 
                limit = 20
            if offset is None: 
                offset = 0
            if not isinstance(limitTotal, int):
                limitTotal = 0
            if sortResult is None: 
                sortResult = True
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = PlaylistPageSimplified()

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'limit': limit,
                'offset': offset,
            }
            if country is not None:
                urlParms['country'] = country
            if locale is not None:
                urlParms['locale'] = locale
            if timestamp is not None:
                urlParms['timestamp'] = timestamp

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/browse/featured-playlists')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = accessTokenHeaderValue or self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                resultMessage = msg.ResponseData.get('message','unknown')
                item = msg.ResponseData.get('playlists',None)
                if item is not None:
                    pageObj = PlaylistPageSimplified(root=item)
            
                    # trace.
                    _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:PlaylistSimplified
                    for item in pageObj.Items:
                        result.Items.append(item)
                        result.Limit = result.ItemsCount
                        if result.ItemsCount >= limitTotal:
                            break
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithOffset(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break

            # update result object with final paging details.
            result.Total = pageObj.Total
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # sort result items.
            if (len(result.Items) > 0):
                if (sortResult is True):
                    result.Items.sort(key=lambda x: (x.Name or "").lower(), reverse=False)

            # trace.
            _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE + result.PagingInfo) % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result, resultMessage

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetGenres(
        self,
        refresh:bool=True
        ) -> list[str]:
        """
        <span class="deprecated">
            DEPRECATED - api endpoint no longer supported by Spotify as of 2024/11/27 for unauthorized Spotify Developer Applications.
            The api endpoint IS still supported by Spotify for authorized Spotify Developer Applications.
            More information about the deprecated functionality can be found on the 
            <a href="https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api" target="_blank">Spotify Developer Forum Blog</a>
            page.
        </span>       
        
        Get a sorted list of available genres seed parameter values.
        
        Args:
            refresh (bool):
                True to return real-time information from the spotify web api and
                update the cache; otherwise, False to just return the cached value.
        
        Returns:
            A sorted list of genre strings.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        The `ConfigurationCache` is updated with the results of this method.  Use the
        `refresh` argument (with False value) to retrieve the cached value and avoid
        the spotify web api request.  This results in better performance.
                        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetGenres.py
        ```
        </details>
        """
        apiMethodName:str = 'GetGenres'
        result:list[str] = None
        cacheDesc:str = CACHE_SOURCE_CURRENT
        
        try:
            
            # trace.
            _logsi.EnterMethod(SILevel.Debug, apiMethodName)
            _logsi.LogVerbose("Get a sorted list of available genres")
                
            # are spotify web player credentials configured? if so, then we will use them to create
            # an elevated authorization access token for the Spotify Web API endpoint call.
            accessTokenHeaderValue:str = self._GetSpotifyWebPlayerTokenHeaderValue()

            # if spotify web player credentials not configured then we are done; the Spotify Web API
            # endpoint is no longer supported by unauthorized Spotify Developer Applications as of 2024/11/27.
            if (accessTokenHeaderValue is None):
                raise SpotifyApiError(SAAppMessages.MSG_SPOTIFY_DEPRECATED_ENDPOINT % apiMethodName)

            # validations.
            if (refresh is None):
                refresh = True
                
            # can we use the cached value?
            if (not refresh) and (apiMethodName in self._ConfigurationCache):
                
                result = self._ConfigurationCache[apiMethodName]
                cacheDesc = CACHE_SOURCE_CACHED
                
            else:
                
                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/recommendations/available-genre-seeds')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = accessTokenHeaderValue or self.AuthToken.HeaderValue
                self.MakeRequest('GET', msg)

                # process results.
                result:list[str] = msg.ResponseData.get('genres',None)
                if result is not None:
                    result.sort()
        
                # update cache.
                self._ConfigurationCache[apiMethodName] = result

            # trace.
            _logsi.LogArray(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE_CACHED % (apiMethodName, type(result).__name__, cacheDesc), result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    @staticmethod
    def GetIdFromUri(
        uri:str, 
        ) -> str:
        """
        Get the id portion from a Spotify uri value.
        
        Args:
            uri (str):  
                The Spotify URI value.
                Example: `spotify:track:5v5ETK9WFXAnGQ3MRubKuE`
                
        Returns:
            A string containing the id value.
            
        No exceptions are raised with this method.
        """
        result:str = None
        
        try:
            
            # validations.
            if uri is None or len(uri.strip()) == 0:
                return result

            # get Id from uri value.
            colonCnt:int = uri.count(':')
            if colonCnt == 2:
                idx:int = uri.rfind(':')
                if idx > -1:
                    result = uri[idx+1:]

            return result

        except Exception:
            
            return None


    def GetImageVibrantColors(
        self, 
        imageSource:str=None, 
        colorCount:int=64, 
        colorQuality:int=5, 
        ) -> ImageVibrantColors:
        """
        Extracts vibrant color palette RGB values from the specified image source.  
        
        Args:
            imageSource (str):  
                The image source to extract color palette information from.  If the prefix of the 
                value is `http:` or `https:`, then the image is downloaded from the url.  
                This can also point to a filename on the local file system.  
                If null, the currently playing Spotify track image url is used.  
                Example: `http://mydomain/image1.jpg`  
                Example: `c:/image1.jpg`  
            colorCount (int):  
                The number of colors in the initial palette from which swatches will be generated.  
                Default is 64.
            colorQuality (int):  
                Controls the processing time and quality of the palette generation.  
                A lower value (e.g. 1) results in higher quality but takes more processing time, 
                while a higher value (e.g. 5) is faster but may result in a lower-quality palette.   
                Default is 5.
                
        Returns:
            A `ImageVibrantColors` object that contains extracted color information.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetImageVibrantColors.py
        ```
        </details>
        """
        apiMethodName:str = 'GetImageVibrantColors'
        apiMethodParms:SIMethodParmListContext = None
        result:ImageVibrantColors = {}
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("imageSource", imageSource)
            apiMethodParms.AppendKeyValue("colorCount", colorCount)
            apiMethodParms.AppendKeyValue("colorQuality", colorQuality)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get vibrant colors from an image url", apiMethodParms)
                
            # validations.
            if (not isinstance(colorCount,int)):
                colorCount = 64
            if (not isinstance(colorQuality,int)):
                colorQuality = 5

            # if image source not specified, then return currently playing track image url value.
            if (imageSource is None):
                nowPlaying:PlayerPlayState = self.GetPlayerNowPlaying(additionalTypes=SpotifyMediaTypes.EPISODE.value)
                if nowPlaying is not None:
                    if nowPlaying.CurrentlyPlayingType in [SpotifyMediaTypes.TRACK.value,SpotifyMediaTypes.EPISODE.value]:
                        trackItem:Track = nowPlaying.Item
                        if (trackItem is not None):
                            imageSource = trackItem.ImageUrl
            if (imageSource is None):
                raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'imageSource'), logsi=_logsi)

            # was a string value specified?
            if (isinstance(imageSource, str)):
                
                imageSourceTmp = imageSource.lower()
                
                # was a url specified? 
                if (imageSourceTmp.startswith("http:") or imageSourceTmp.startswith("https:")):
                    
                    # get image data from the url.
                    response:HTTPResponse = self._Manager.request("GET", imageSource)
                    if (response.status != 200):
                        raise SpotifyApiError("Image URL could not be accessed (%s - %s): \"%s\"" % (response.status, response.reason, imageSource), logsi=_logsi)
                    imageSource = response.data

            # prepare to extract vibrant colors from the image source.
            vibrant = Vibrant(color_count=colorCount, quality=colorQuality)

            # extract the color palette; this returns a Palette containing vibrant, muted, 
            # dark vibrant, dark muted, light vibrant, and light muted colors.
            palette:Palette = vibrant.get_palette(imageSource)
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, type(palette).__name__), palette, excludeNonPublic=True)
        
            # process results.
            result = ImageVibrantColors(root=palette)

            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetMarkets(
        self, 
        refresh:bool=True
        ) -> list[str]:
        """
        Get the list of markets (country codes) where Spotify is available.

        Args:
            refresh (bool):
                True to return real-time information from the spotify web api and
                update the cache; otherwise, False to just return the cached value.
        
        Returns:
            A sorted list of market identifier strings.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        The `ConfigurationCache` is updated with the results of this method.  Use the
        `refresh` argument (with False value) to retrieve the cached value and avoid
        the spotify web api request.  This results in better performance.
                        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetMarkets.py
        ```
        </details>
        """
        apiMethodName:str = 'GetMarkets'
        result:list[str] = None
        cacheDesc:str = CACHE_SOURCE_CURRENT
        
        try:
            
            # trace.
            _logsi.EnterMethod(SILevel.Debug, apiMethodName)
            _logsi.LogVerbose("Get a sorted list of available markets (country codes)")
            
            # validations.
            if (refresh is None):
                refresh = True
                
            # can we use the cached value?
            if (not refresh) and (apiMethodName in self._ConfigurationCache):
                
                result = self._ConfigurationCache[apiMethodName]
                cacheDesc = CACHE_SOURCE_CACHED
                
            else:
                
                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/markets')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                self.MakeRequest('GET', msg)

                # process results.
                result:list[str] = msg.ResponseData.get('markets',None)
                if result is not None:
                    result.sort()
        
                # update cache.
                self._ConfigurationCache[apiMethodName] = result

            # trace.
            _logsi.LogArray(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE_CACHED % (apiMethodName, type(result).__name__, cacheDesc), result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetPlayerDevice(
        self, 
        deviceId:str, 
        refresh:bool=True
        ) -> Device:
        """
        Get information about a user's available Spotify Connect player device. 
        
        This method requires the `user-read-playback-state` scope.

        Args:
            deviceId (str):
                The device id or name to retrieve.
            refresh (bool):
                True (default) to resolve the device real-time from the spotify web api 
                device list; otherwise, False to use the cached device list to resolve the
                device.
                
        Returns:
            A `Device` object if found; otherwise, null.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        The `ConfigurationCache` is updated with the results of this method.  Use the
        `refresh` argument (with False value) to retrieve the cached value and avoid
        the spotify web api request.  This results in better performance.
                        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetPlayerDevice.py
        ```
        </details>
        """
        apiMethodName:str = 'GetPlayerDevice'
        apiMethodParms:SIMethodParmListContext = None
        result:Device = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("deviceId", deviceId)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get user's available Spotify Connect player device", apiMethodParms)
            
            # validations.
            if (refresh is None):
                refresh = True
            if deviceId is None:
                return None
            deviceId = deviceId.lower()  # prepare for compare

            # get ALL devices, as there is no spotify web api endpoint
            # to retrieve a specific device.
            devices:list[Device] = self.GetPlayerDevices(refresh=refresh)
            
            # loop through the results looking for the specified device id.
            item:Device
            for item in devices:
                if item.Id is not None:
                    if deviceId == item.Id.lower():
                        result = item
                        break
                
            # if no match by id, then try to match by device name.
            if result is None:
                for item in devices:
                    if item.Name is not None:
                        if deviceId == item.Name.lower():
                            result = item
                            break
                
            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, 'Device'), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def PlayerConvertDeviceNameToId(
        self, 
        value:str, 
        refresh:bool=False
        ) -> str:
        """
        Converts a Spotify Connect player device name to it's equivalent id value if
        the value is a device name.  If the value is a device id, then the value is 
        returned as-is.
        
        This method requires the `user-read-playback-state` scope.

        Args:
            value (str):
                The device id or name value to check.
            refresh (bool):
                True to resolve the device real-time from the spotify web api device list; 
                otherwise, False (default) to use the cached device list to resolve the device.
                
        Returns:
            One of the following:  
            - if value is a device id, then the value is returned as-is; no device list 
              lookup is performed, and the value is assumed to be a valid device id.  
            - if value is not a device id, then it is assumed to be a name; a device list
              lookup is performed to retrieve it's device id.  if found, then the id is
              returned; otherwise, the value is returned as-is with the understanding that
              subsequent operations will fail since it's not in the device list.  
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        The id for the first match found on the device name will be returned if multiple devices 
        are found in the Spotify Connect player device list that have the same name (with different 
        id's).  Care should be taken to make device names unique if using device names for
        methods that require a device id or name.
        
        If the `refresh` argument is specified, then the `ConfigurationCache` is updated with 
        the latest Spotify Connect player device list.  Use the `refresh` argument (with False 
        value) to retrieve the cached value and avoid the spotify web api request.  This results 
        in better performance.
                        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/PlayerConvertDeviceNameToId.py
        ```
        </details>
        """
        apiMethodName:str = 'PlayerConvertDeviceNameToId'
        apiMethodParms:SIMethodParmListContext = None

        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("value", value)
            apiMethodParms.AppendKeyValue("refresh", refresh)
            _logsi.LogMethodParmList(SILevel.Verbose, "Checking Spotify Connect Player device for name", apiMethodParms)

            # validations.
            if (refresh is None):
                refresh = False

            try:

                # resolve the device id from the specified device value.
                # an exception will be raised if the device could not be resolved!
                scDevice = self._SpotifyConnectDirectory.GetDevice(value, refreshDynamicDevices=refresh)
                return scDevice.Id
            
            except Exception:
            
                # if a name could not be found in the Spotify Connect Player devices then just 
                # return the value as-is.
                _logsi.LogVerbose("Device name '%s' could not be found in the Spotify Connect Device list; subsequent actions will probably fail using this device name" % value)
                return value

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetPlayerDevices(
        self, 
        refresh:bool=True,
        sortResult:bool=True,
        ) -> list[Device]:
        """
        Get information about a user's available Spotify Connect player devices. 
        
        Some device models are not supported and will not be listed in the API response.
        
        This method requires the `user-read-playback-state` scope.

        Args:
            refresh (bool):
                True (default) to return real-time information from the spotify web api and
                update the cache; otherwise, False to just return the cached value.
            sortResult (bool):
                True to sort the items by name; otherwise, False to leave the items in the same order they 
                were returned in by the Spotify Web API.  
                Default: True
        
        Returns:
            A list of `Device` objects that contain the device details, sorted by name.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        Note that this method will only return the devices for which the current user
        context has control of, or other available devices that do not have an active
        user context assigned.  Use the `GetSpotifyConnectDevices` method to retrieve
        a complete list of devices that are available to all users.
                
        The `ConfigurationCache` is updated with the results of this method.  Use the
        `refresh` argument (with False value) to retrieve the cached value and avoid
        the spotify web api request.  This results in better performance.
                        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetPlayerDevices.py
        ```
        </details>
        """
        apiMethodName:str = 'GetPlayerDevices'
        apiMethodParms:SIMethodParmListContext = None
        result:list[Device] = []
        cacheDesc:str = CACHE_SOURCE_CURRENT
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("refresh", refresh)
            apiMethodParms.AppendKeyValue("sortResult", sortResult)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get user's available Spotify Connect player devices", apiMethodParms)

            # validations.
            if (refresh is None):
                refresh = True
            if sortResult is None: 
                sortResult = True

            # can we use the cached value?
            if (not refresh) and (apiMethodName in self._ConfigurationCache):
                
                result = self._ConfigurationCache[apiMethodName]
                cacheDesc = CACHE_SOURCE_CACHED
                
            else:
                
                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/player/devices')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                self.MakeRequest('GET', msg)

                # process results.
                items = msg.ResponseData.get('devices',None)
                if items is not None:
                    for item in items:
                        result.append(Device(root=item))

                # sort items on Name property, ascending order.
                if (len(result) > 0) and (sortResult is True):
                    result.sort(key=lambda x: (x.Name or "").lower(), reverse=False)
       
                # update cache.
                self._ConfigurationCache[apiMethodName] = result

            # trace.
            _logsi.LogArray(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE_CACHED % (apiMethodName, 'list[Device]', cacheDesc), result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetPlayerNowPlaying(
        self, 
        market:str=None, 
        additionalTypes:str=None
        ) -> PlayerPlayState:
        """
        Get the object currently being played on the user's Spotify account.
        
        This method requires the `user-read-currently-playing` scope.
        
        Args:
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
            additionalTypes (str):
                A comma-separated list of item types that your client supports besides the default track type.  
                Valid types are: `track` and `episode`.  
                Specify `episode` to get podcast track information.  
                Note: This parameter was introduced to allow existing clients to maintain their current behaviour 
                and might be deprecated in the future. In addition to providing this parameter, make sure that your client 
                properly handles cases of new types in the future by checking against the type field of each object.
                
        Returns:
            A `PlayerPlayState` object that contains player state details as well as
            currently playing content.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetPlayerNowPlaying.py
        ```
        </details>
        """
        apiMethodName:str = 'GetPlayerNowPlaying'
        apiMethodParms:SIMethodParmListContext = None
        result:PlayerPlayState = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("market", market)
            apiMethodParms.AppendKeyValue("additionalTypes", additionalTypes)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get the object currently being played on the user's Spotify account", apiMethodParms)
                
            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market, forceReturnValue=True)

            # a spotify free or premium level membership is required to get the nowplaying info.
            if (not self.UserProfile.IsProductPremium) and (not self.UserProfile.IsProductFree):
                raise SpotifyApiError(SAAppMessages.MSG_SPOTIFY_ACCOUNT_REQUIRED_FOR_NOWPLAYING, logsi=_logsi)

            # build spotify web api request parameters.
            urlParms:dict = {}
            if market is not None:
                urlParms['market'] = market
            if additionalTypes is not None:
                urlParms['additional_types'] = additionalTypes

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/player/currently-playing')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)

            # process results.
            result = PlayerPlayState(root=msg.ResponseData)
            
            # is this an episode?  if so, then determine the item type (e.g. podcast or audiobook).
            if (result is not None):
                if (result.Item is not None):
                    result.ItemType = SpotifyClient.GetTypeFromUri(result.Item.Uri)
                    if (result.CurrentlyPlayingType == SpotifyMediaTypes.EPISODE.value):
                        uriId:str = SpotifyClient.GetIdFromUri(result.Item.Uri)
                        if (self.IsChapterEpisode(uriId)):
                            result.ItemType = 'audiobook'
                        else:
                            result.ItemType = 'podcast'
        
            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetPlayerNowPlayingAlbumUri(self) -> str:
        """
        Returns the album uri value of the currently playing media if something is
        playing; otherwise, null is returned.
        
        Raises:
            SpotifyApiError: 
                If current user does not have a Spotify free or premium level account.  
                If nowplaying context does not contain an album reference.  
        """
        result:str = None

        # get nowplaying status.
        nowPlaying:PlayerPlayState = self.GetPlayerNowPlaying(additionalTypes=SpotifyMediaTypes.TRACK.value)
        
        # is a track playing?  if so, return the album uri value.
        if nowPlaying is not None:
            if nowPlaying.CurrentlyPlayingType in [SpotifyMediaTypes.TRACK.value]:
                trackItem:Track = nowPlaying.Item
                if (trackItem is not None) and (trackItem.Album is not None):
                    result = trackItem.Album.Uri
            else:
                raise SpotifyApiError("Currently playing item does not contain an Album reference", logsi=_logsi)
                
        return result
    

    def GetPlayerNowPlayingArtistUri(self) -> str:
        """
        Returns the artist uri value of the currently playing media if something is
        playing; otherwise, null is returned.
        
        Raises:
            SpotifyApiError: 
                If current user does not have a Spotify free or premium level account.  
                If nowplaying context does not contain an artist reference.  
        """
        result:str = None
        
        # get nowplaying status.
        nowPlaying:PlayerPlayState = self.GetPlayerNowPlaying()
        
        # is a track playing?  if so, return the artist uri value.
        if nowPlaying is not None:
            if nowPlaying.CurrentlyPlayingType in [SpotifyMediaTypes.TRACK.value]:
                trackItem:Track = nowPlaying.Item
                if (trackItem is not None) and (len(trackItem.Artists) > 0):
                    result = trackItem.Artists[0].Uri
            else:
                raise SpotifyApiError("Currently playing item does not contain an Artist reference", logsi=_logsi)
                
        return result
    

    def GetPlayerNowPlayingAudiobookUri(
        self,
        market:str=None,
        ignoreResponseErrors:bool=False,
        ) -> str:
        """
        Returns the audiobook uri value of the currently playing media if something is
        playing; otherwise, null is returned.
        
        Args:
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
            ignoreResponseErrors (bool):
                True to ignore any request response errors that occur; otherwise, an exception will be thrown
                if a response error is detected (default).
                
        Raises:
            SpotifyApiError: 
                If current user does not have a Spotify free or premium level account.  
                If nowplaying context is not a audiobook chapter.  
        """
        result:str = None
        
        # validations.
        if (ignoreResponseErrors is None):
            ignoreResponseErrors = False
                
        # get nowplaying status.
        nowPlaying:PlayerPlayState = self.GetPlayerNowPlaying(market, additionalTypes=SpotifyMediaTypes.EPISODE.value)
        
        # is an chapter playing?  if so, return the parent show uri value.
        if nowPlaying is not None:
            if nowPlaying.CurrentlyPlayingType in [SpotifyMediaTypes.EPISODE.value]:
                playingItem:Chapter = nowPlaying.Item
                if (playingItem is not None):
                    chapter:Chapter = self.GetChapter(playingItem.Id, market, ignoreResponseErrors)
                    if (chapter.Audiobook is not None):
                        result = chapter.Audiobook.Uri
            else:
                if (not ignoreResponseErrors):
                    raise SpotifyApiError("Currently playing item is not a Audiobook Chapter", logsi=_logsi)
                
        return result
    

    def GetPlayerNowPlayingPlaylistUri(self) -> str:
        """
        Returns the playlist uri value of the currently playing media if something is
        playing; otherwise, null is returned.
        
        Raises:
            SpotifyApiError: 
                If current user does not have a Spotify free or premium level account.  
                If nowplaying context is not a playlist.  
        """
        result:str = None
        
        # get nowplaying status.
        nowPlaying:PlayerPlayState = self.GetPlayerNowPlaying()
        
        # is a playlist playing?  if so, return the uri value.
        if nowPlaying is not None:
            context:Context = nowPlaying.Context
            if (context is not None) and (context.Type == SpotifyMediaTypes.PLAYLIST.value):
                result = context.Uri
            else:
                raise SpotifyApiError("Currently playing context is not a Playlist", logsi=_logsi)
                
        return result
    

    def GetPlayerNowPlayingShowUri(self) -> str:
        """
        Returns the show uri value of the currently playing media if something is
        playing; otherwise, null is returned.
        
        Raises:
            SpotifyApiError: 
                If current user does not have a Spotify free or premium level account.  
                If nowplaying context is not a show episode.  
        """
        result:str = None
        
        # get nowplaying status.
        nowPlaying:PlayerPlayState = self.GetPlayerNowPlaying(additionalTypes=SpotifyMediaTypes.EPISODE.value)
        
        # is an episode playing?  if so, return the parent show uri value.
        if nowPlaying is not None:
            if nowPlaying.CurrentlyPlayingType in [SpotifyMediaTypes.EPISODE.value]:
                playingItem:Episode = nowPlaying.Item
                if (playingItem is not None):
                    episode:Episode = self.GetEpisode(playingItem.Id)
                    result = episode.Show.Uri
            else:
                raise SpotifyApiError("Currently playing item is not a Show Episode", logsi=_logsi)
                
        return result
    

    def GetPlayerNowPlayingUri(
        self,
        additionalTypes:str=None,
        ) -> str:
        """
        Returns the uri value of the currently playing media type if something is
        playing; otherwise, null is returned.
        
        Args:
            additionalTypes (str):
                An item type that your client supports besides the default track type.  
                Valid types are: `track` and `episode`.  
                Specify `episode` to get podcast track information.  
        
        Raises:
            SpotifyApiError: 
                If current user does not have a Spotify free or premium level account.  
                If nowplaying item is not of the specified `additionalType`.  
        """
        result:str = None
        
        # get nowplaying status.
        nowPlaying:PlayerPlayState = self.GetPlayerNowPlaying(additionalTypes=additionalTypes)
        
        # is anything playing?  if so, return the uri value.
        if nowPlaying is not None:
            if nowPlaying.Item is not None:
                if additionalTypes is None:
                    # if not validating uri type then just return the uri.
                    result = nowPlaying.Item.Uri
                elif nowPlaying.CurrentlyPlayingType == additionalTypes:
                    # if validating uri type then return uri if nowplaying types matches desired type.
                    result = nowPlaying.Item.Uri
                else:
                    # otherwise nowplaying type is not the desired type!
                    raise SpotifyApiError("Currently playing item is not a %s" % additionalTypes, logsi=_logsi)
            else:
                # otherwise nowplaying item does not contain the desired type!
                if additionalTypes is None:
                    raise SpotifyApiError("Currently playing item context is not set", logsi=_logsi)
                else:
                    raise SpotifyApiError("Currently playing item context is not a %s item" % additionalTypes, logsi=_logsi)
                
        return result
    

    def GetPlayerPlaybackState(
        self, 
        market:str=None, 
        additionalTypes:str=None,
        refresh:bool=True,
        ) -> PlayerPlayState:
        """
        Get information about the user's current playback state, including track or episode, progress, 
        and active device.
        
        This method requires the `user-read-playback-state` scope.
        
        Args:
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
            additionalTypes (str):
                A comma-separated list of item types that your client supports besides the default track type.  
                Valid types are: `track` and `episode`.  
                Specify `episode` to get podcast track information.  
                Note: This parameter was introduced to allow existing clients to maintain their current behaviour 
                and might be deprecated in the future. In addition to providing this parameter, make sure that your client 
                properly handles cases of new types in the future by checking against the type field of each object.
            refresh (bool):
                True to return real-time information from the Spotify Web API and
                update the cache; otherwise, False to just return the cached value.  
                Default is True.
                
        Returns:
            A `PlayerPlayState` object that contains player state details as well as
            currently playing content.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetPlayerPlaybackState.py
        ```
        </details>
        """
        apiMethodName:str = 'GetPlayerPlaybackState'
        apiMethodParms:SIMethodParmListContext = None
        result:PlayerPlayState = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("market", market)
            apiMethodParms.AppendKeyValue("additionalTypes", additionalTypes)
            apiMethodParms.AppendKeyValue("refresh", refresh)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get the user's current playback state", apiMethodParms)
            
            # validations.
            if (refresh is None):
                refresh = True

            # are we getting the cached value? if so, then just return it.
            if (not refresh):

                result = self._ConfigurationCache.get(apiMethodName, None)
                if (result is None):
                    result = PlayerPlayState()

                # trace.
                _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName + " (cached)", type(result).__name__), result, excludeNonPublic=True)
                return result

            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market, forceReturnValue=True)

            # build spotify web api request parameters.
            urlParms:dict = {}
            if market is not None:
                urlParms['market'] = market
            if additionalTypes is not None:
                urlParms['additional_types'] = additionalTypes

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/player')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)

            # process results.
            result = PlayerPlayState(root=msg.ResponseData)

            # update cache with result.
            self._ConfigurationCache[apiMethodName] = result
           
            # is this an episode?  if so, then determine the item type (e.g. podcast or audiobook).
            if (not result.IsEmpty):
                if (result.Item is not None):
                    result.ItemType = SpotifyClient.GetTypeFromUri(result.Item.Uri)
                    if (result.CurrentlyPlayingType == SpotifyMediaTypes.EPISODE.value):
                        uriId:str = SpotifyClient.GetIdFromUri(result.Item.Uri)
                        if (self.IsChapterEpisode(uriId)):
                            result.ItemType = 'audiobook'
                        else:
                            result.ItemType = 'podcast'
        
            # check for a restricted device; if found, then grab the device id from the 
            # cached list of spotify connect devices (if present).
            if (not result.IsEmpty):
                device:Device = result.Device
                if (device is not None) and (device.Id is None or device.Id == ''):
                    cacheKey:str = 'GetSpotifyConnectDevices'
                    if (cacheKey in self._ConfigurationCache):
                        devices:SpotifyConnectDevices = self._ConfigurationCache[cacheKey]
                        scDevice:SpotifyConnectDevice = devices.GetDeviceByName(device.Name)
                        if scDevice is not None:
                            device.Id = scDevice.DeviceInfo.DeviceId
        
            # did Spotify return a playstate?
            # if so, then update the player last played info if something is playing.
            if (not result.IsEmpty):
                if (result._IsPlaying) and (result._Item is not None):
                    self._PlayerLastPlayedInfo = PlayerLastPlayedInfo(result)
                    _logsi.LogObject(SILevel.Verbose, "Updated internal PlayerLastPlayedInfo: %s" % self._PlayerLastPlayedInfo.Summary, self._PlayerLastPlayedInfo, excludeNonPublic=True)

            # update Spotify Connect Directory with active device details.
            # IMPORTANT - make sure result contains an object, otherwise it's an endless loop!
            if (result is not None):
                self.SpotifyConnectDirectory.UpdateActiveDevice(result)

            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetPlayerPlaybackStateSonos(
        self, 
        scDevice:SpotifyConnectDevice,
        ) -> PlayerPlayState:
        """
        Get information about the Sonos user's current playback state, including track or episode, progress, 
        and active device.
        
        This is not part of the Spotify Web API specification; it is for Sonos devices only!

        Args:
            scDevice (SpotifyConnectDevice):
                Spotify Connect device instance used to identify the Sonos player.
                
        Returns:
            A `PlayerPlayState` object that contains Sonos player state details as well as
            currently playing content.
                
        Raises:
            SpotifyApiError: 
                If the method fails for any other reason.
        """
        apiMethodName:str = 'GetPlayerPlaybackStateSonos'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("scDevice", scDevice)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get Sonos device current playback state", apiMethodParms)
            
            # create playstate object.
            playerState = PlayerPlayState()

            # get Sonos Controller instance for the device.
            _logsi.LogVerbose("Getting Sonos device status via Sonos Controller instance for device: %s" % (scDevice.Title))
            sonosPlayer:SoCo = self.SpotifyConnectDirectory.GetSonosPlayer(scDevice)

            # build a spotify playback status instance with equivalent Sonos state values.
            sonosTrackInfo:dict = sonosPlayer.get_current_track_info()
            _logsi.LogDictionary(SILevel.Verbose, "Sonos device current_track_info results for device: %s" % (scDevice.Title), sonosTrackInfo, prettyPrint=True)
            sonosTransportInfo:dict = sonosPlayer.get_current_transport_info()
            _logsi.LogDictionary(SILevel.Verbose, "Sonos device get_current_transport_info results for device: %s" % (scDevice.Title), sonosTransportInfo, prettyPrint=True)

            # indicate this is a device-specific playstate.
            playerState.IsDeviceState = True
            playerState.DeviceMusicSource = "" + str(sonosPlayer.music_source)

            # update Spotify Web API player state with Sonos player state.
            playerState._Device._Id = scDevice.Id
            playerState._Device._Name = sonosPlayer.player_name
            playerState._Device._VolumePercent = sonosPlayer.volume
            playerState._Device._IsActive = True
            playerState._Device._IsRestricted = True
            playerState._Device._SupportsVolume = True
            playerState._Device._Type = 'SPEAKER'
                
            # try to get the spotify uri from the "metadata" music library DIDL value, as
            # the "uri" value (e.g. "x-sonos-vli:RINCON_38420B909DC801400:2,spotify:e934941535d7b182815bf688490ce8a8")
            # is not a true spotify uri value (e.g. "spotify:track:6kYyS9g4WJeRzTYqsmcMmM")
            spotifyUri:str = sonosTrackInfo.get('uri','')
            didl:str = sonosTrackInfo.get('metadata',None)
            if (didl):
                METADATA_ID:str = 'x-sonos-spotify:'
                idx:int = didl.find(METADATA_ID)
                if (idx > -1):
                    spotifyUri:str = didl[idx + len(METADATA_ID):]
                    spotifyUri = urllib.parse.unquote(spotifyUri)
                    idx = spotifyUri.find('?')
                    if (idx > -1):
                        spotifyUri = spotifyUri[:idx]
            spotifyType = self.GetTypeFromUri(spotifyUri) or ''
            spotifyId = self.GetIdFromUri(spotifyUri) or ''
                
            # set base item properties.
            playerState.IsEmpty = False
            playerState.ItemType = spotifyType
            sTimeValue:str = sonosTrackInfo.get('position',None)
            playerState._ProgressMS = mediaPositionHMS_toSeconds(sTimeValue) * 1000        # convert h:mm:ss to milliseconds
                
            # set some item properties based on the playing type (episode or non-episode).
            if (spotifyType == SpotifyMediaTypes.EPISODE.value):

                # get the episode data from spotify, as Sonos Soco data is incomplete.
                playerState._CurrentlyPlayingType = SpotifyMediaTypes.EPISODE.value
                episode:Episode = self.GetEpisode(spotifyId)
                if (episode.Id is not None): 
                    playerState._Item = episode
                    if (playerState._Context is None):
                        playerState._Context = Context()
                        playerState._Context._Type = episode.Show.Type
                        playerState._Context._Uri = episode.Show.Uri
                        playerState._Context._Href = episode.Show.Href
                        playerState._Context._ExternalUrls = episode.Show.ExternalUrls
                else:
                    # if data could not be obtained from spotify, then use what's 
                    # available from Sonos Soco api metadata.
                    playerState._Item = Episode()
                    playerState._Item._Name = sonosTrackInfo.get('title','')
                    playerState._Item._Uri = spotifyUri
                    playerState._Item._Description = 'Sonos device does not provide a description'
                    sTimeValue:str = sonosTrackInfo.get('duration',None)
                    playerState._Item._DurationMS = mediaPositionHMS_toSeconds(sTimeValue) * 1000  # convert h:mm:ss to milliseconds
                    playerState._Item._Explicit = False
                    playerState._Item._Href = 'https://api.spotify.com/v1/episodes/' + spotifyId
                    playerState._Item._HtmlDescription = playerState._Item._Description
                    playerState._Item._Id = spotifyId
                    playerState._Item.Images.append(ImageObject())
                    playerState._Item.Images[0]._Url = sonosTrackInfo.get('album_art','')
                    playerState._Item._TrackNumber = sonosTrackInfo.get('playlist_position','')
                    playerState._Item._ReleaseDate = '0000'
                    playerState._Item._ReleaseDatePrecision = 'year'
                    playerState._Item._Type = SpotifyMediaTypes.EPISODE.value
                    playerState._Item._Show = Show()
                    playerState._Item._Show._Name = sonosTrackInfo.get('album','')  # TODO get this from metadata (<r:podcast>The Elfstones of Shannara</r:podcast>)
                    playerState._Item._Show.Images.append(ImageObject())
                    playerState._Item._Show.Images[0]._Url = sonosTrackInfo.get('album_art','')
                    playerState._Item._Show._Publisher = sonosTrackInfo.get('artist','')

                    # if show name not set then get it from metadata.
                    if (playerState._Item._Show._Name == ''):
                        if (didl):
                            METADATA_ID:str = '<r:podcast>'
                            METADATA_END:str = '</r:podcast>'
                            idx:int = didl.find(METADATA_ID)
                            if (idx > -1):
                                metaValue:str = didl[idx + len(METADATA_ID):]
                                idx = metaValue.find(METADATA_END)
                                if (idx > -1):
                                    metaValue = metaValue[:idx]
                                    playerState._Item._Show._Name = metaValue
                                    
                # if episode is playing then resolve the underlying type (audiobook / podcast show).
                if (self.IsChapterEpisode(spotifyId)):
                    playerState.ItemType = 'audiobook'
                else:
                    playerState.ItemType = 'podcast'
                        
            elif (spotifyType == SpotifyMediaTypes.TRACK.value):
                    
                # get the track data from spotify, as Sonos Soco data is incomplete.
                track:Track = self.GetTrack(spotifyId)
                if (track.Id is not None): 
                    playerState._Item = track
                    if (playerState._Context is None):
                        playerState._Context = Context()
                        playerState._Context._Type = track.Album.Type
                        playerState._Context._Uri = track.Album.Uri
                        playerState._Context._Href = track.Album.Href
                        playerState._Context._ExternalUrls = track.Album.ExternalUrls
                else:
                    # if data could not be obtained from spotify, then use what's 
                    # available from Sonos Soco api metadata.
                    playerState._CurrentlyPlayingType = SpotifyMediaTypes.TRACK.value
                    playerState.ItemType = playerState._CurrentlyPlayingType
                    playerState._Item = Track()
                    playerState._Item._Name = sonosTrackInfo.get('title','')
                    playerState._Item._Uri = spotifyUri
                    playerState._Item._Description = 'Sonos device does not provide a description'
                    sTimeValue:str = sonosTrackInfo.get('duration',None)
                    playerState._Item._DurationMS = mediaPositionHMS_toSeconds(sTimeValue) * 1000  # convert h:mm:ss to milliseconds
                    playerState._Item._Explicit = False
                    playerState._Item._Href = 'https://api.spotify.com/v1/episodes/' + spotifyId
                    playerState._Item._HtmlDescription = playerState._Item._Description
                    playerState._Item._Id = spotifyId
                    playerState._Item._TrackNumber = sonosTrackInfo.get('playlist_position','')
                    playerState._Item._ReleaseDate = '0000'
                    playerState._Item._ReleaseDatePrecision = 'year'
                    playerState._Item._Type = SpotifyMediaTypes.TRACK.value
                    playerState._Item._Album = Album()
                    playerState._Item._Album._Name = sonosTrackInfo.get('album','')
                    playerState._Item._Album.Images.append(ImageObject())
                    playerState._Item._Album.Images[0]._Url = sonosTrackInfo.get('album_art','')
                    playerState._Item.Artists.append(Artist())
                    playerState._Item.Artists[0]._Name = sonosTrackInfo.get('artist','')
                               
            # set transport actions.
            currentTransportState:str = sonosTransportInfo.get('current_transport_state','')
            if currentTransportState == 'PLAYING':
                playerState._IsPlaying = True
            elif currentTransportState in ['PAUSED_PLAYBACK','STOPPED']:
                playerState.Actions._Pausing = True
                    
            # only update the following PlayState attributes from SoCo if they are NOT set.
            # these values are used to set the Sonos PlayMode value, which is the actual value that determines
            # what the Repeat and Shuffle settings are (ya, it's weird!).  What is odd is that the Spotify
            # Web API PlayerState values for Shuffle and Repeat can be different than what the Sonos Controller
            # API (SoCo) report for the device!  This is why we use the Spotify Web API PlayerState values.
            if playerState._ShuffleState is None:
                playerState._ShuffleState = sonosPlayer.shuffle
            if playerState._RepeatState is None:
                sonosRepeat = sonosPlayer.repeat
                if sonosRepeat == 'ONE':
                    playerState._RepeatState = 'track'
                elif sonosRepeat == False:
                    playerState._RepeatState = 'off'
                elif sonosRepeat == True:
                    playerState._RepeatState = 'context'
        
            # trace.
            _logsi.LogObject(SILevel.Verbose, "Current Spotify player PlayState (built from Sonos device current state) for device: %s" % (scDevice.Title), playerState, excludeNonPublic=True)
            return playerState

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetPlayerQueueInfo(self) -> PlayerQueueInfo:
        """
        Get the list of objects that make up the user's playback queue.
        
        This method requires the `user-read-currently-playing` and `user-read-playback-state` scope.
        
        Returns:
            A `PlayerQueueInfo` object that contains the player queue information.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetPlayerQueueInfo.py
        ```
        </details>
        """
        apiMethodName:str = 'GetPlayerQueueInfo'
        result:PlayHistoryPage = None
        
        try:
            
            # trace.
            _logsi.EnterMethod(SILevel.Debug, apiMethodName)
            _logsi.LogVerbose("Get the list of objects that make up the user's playback queue")
                
            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/player/queue')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            self.MakeRequest('GET', msg)

            # process results.
            result = PlayerQueueInfo(root=msg.ResponseData)
            result.DateLastRefreshed = datetime.utcnow().timestamp()
        
            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetPlayerRecentTracks(
        self, 
        limit:int=50,
        after:int=None,
        before:int=None,
        limitTotal:int=None
        ) -> PlayHistoryPage:
        """
        Get tracks from the current user's recently played tracks.  
        Note: Currently doesn't support podcast episodes.
        
        This method requires the `user-read-recently-played` scope.
        
        Args:
            limit (int):
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            after (int):
                Returns all items after (but not including) this cursor position, which is 
                a Unix timestamp in milliseconds.  
                If `after` is specified, `before` must not be specified.  
                Use with limit to get the next set of items.  
                Default: `0` (the first item).  
            before (int):
                Returns all items before (but not including) this cursor position, which is 
                a Unix timestamp in milliseconds.  
                If `before` is specified, `after` must not be specified.  
                Use with limit to get the next set of items.  
                Default: `0` (the first item).  
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
                
        Spotify currently limits the maximum number of items returned to 50 no matter what you 
        supply for the `limitTotal` argument.
        
        The `after` and `before` arguments are based upon local time (not UTC time).  Recently
        played item history uses a local timestamp, and NOT a UTC timestamp.
        
        If both `after` and `before` arguments are null (or zero), then a `before` value
        is generated that will retrieve the last 50 recently played tracks.
                
        Returns:
            A `PlayHistoryPage` object that contains the recently played items.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code - After DateTime</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetPlayerRecentTracks_AfterDateTime.py
        ```
        </details>
        <details>
          <summary>Sample Code - For Past 1 Hour</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetPlayerRecentTracks_Past01Hours.py
        ```
        </details>
        """
        apiMethodName:str = 'GetPlayerRecentTracks'
        apiMethodParms:SIMethodParmListContext = None
        result:PlayHistoryPage = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("after", after)
            apiMethodParms.AppendKeyValue("before", before)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get tracks from the current user's recently played tracks", apiMethodParms)
            
            # validations.
            if before is None:
                before = 0
            if (not isinstance(before,int)):
                before = int(before)

            if after is None:
                after = 0
            if (not isinstance(after,int)):
                after = int(after)

            if limit is None: 
                limit = 20
            if not isinstance(limitTotal, int):
                limitTotal = 0

            # if no before or after values, then get the last 50 tracks played.
            if (after == 0) and (before == 0):
                before = GetUnixTimestampMSFromUtcNow(seconds=-1)
                limitTotal = 100  # spotify only returns 50 max.
                _logsi.LogVerbose("Defaulting to retrieve play history of the last 50 recently played items (before = %d)" % before)
                                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = PlayHistoryPage()

            # assume we are using an AFTER cursor.
            isAfterCursor:bool = True
                
            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'limit': limit,
            }
            if after > 0:
                urlParms['after'] = after
            if before > 0:
                urlParms['before'] = before
                isAfterCursor = False

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/player/recently-played')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                pageObj = PlayHistoryPage(root=msg.ResponseData)
        
                # trace.
                _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:PlayHistory = None
                    for item in pageObj.Items:
                        result.Items.append(item)
                        result.Limit = result.ItemsCount
                        if result.ItemsCount >= limitTotal:
                            break

                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithCursor(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break
                    
            # update result object with final paging details.
            # use ItemsCount for total value, as the paging object Total is zero for before / after cursor operations.
            result.Total = result.ItemsCount
            result.CursorAfter = pageObj.CursorAfter
            result.CursorBefore = pageObj.CursorBefore
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetPlaylist(
        self, 
        playlistId:str=None, 
        market:str=None,
        fields:str=None,
        additionalTypes:str=None
        ) -> Playlist:
        """
        Get a playlist owned by a Spotify user.
        
        Args:
            playlistId (str):  
                The Spotify ID of the playlist.  
                Example: `5v5ETK9WFXAnGQ3MRubKuE`
                If null, the currently playing playlist uri id value is used.
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
            fields (str):
                Filters for the query: a comma-separated list of the fields to return.  
                If omitted, all fields are returned. 
                For example, to get just the playlist's description and URI:  
                `fields=description,uri`. 
                A dot separator can be used to specify non-reoccurring fields, while parentheses can be used 
                to specify reoccurring fields within objects. For example, to get just the added date and user 
                ID of the adder:  
                `fields=items(added_at,added_by.id)`.   
                Use multiple parentheses to drill down into nested objects, for example:  
                `fields=items(track(name,href,album(name,href)))`.  
                Fields can be excluded by prefixing them with an exclamation mark, for example:  
                `fields=items(track(name,href,album(!name,href)))`  
                Example: fields=items(added_by.id,track(name,href,album(name,href)))
            additionalTypes (str):
                A comma-separated list of item types that your client supports besides the default track type.  
                Valid types are: track and episode.  
                Note: This parameter was introduced to allow existing clients to maintain their current behaviour 
                and might be deprecated in the future.  In addition to providing this parameter, make sure that your 
                client properly handles cases of new types in the future by checking against the type field of each object.                
                
        Returns:
            A `Playlist` object that contains the playlist details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.  

        <span class="warning">
            <b>DEPRECATED functionality as of 2024/11/27</b>  
            For unauthorized Spotify Developer Applications, the api endpoint will return a `404 - Resource Not Found` exception if a Spotify Algorithmic playlist is specified.<br/>
            For authorized Spotify Developer Applications, the api endpoint will return details if a Spotify Algorithmic playlist is specified.<br/>
            More information about the deprecated functionality can be found on the 
            <a href="https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api" target="_blank">Spotify Developer Forum Blog</a>
            page.
        <span>

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetPlaylist.py
        ```
          <summary>Sample Code - NowPlaying</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetPlaylist_NowPlaying.py
        ```
        </details>
        """
        apiMethodName:str = 'GetPlaylist'
        apiMethodParms:SIMethodParmListContext = None
        result:Playlist = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("playlistId", playlistId)
            apiMethodParms.AppendKeyValue("market", market)
            apiMethodParms.AppendKeyValue("fields", fields)
            apiMethodParms.AppendKeyValue("additionalTypes", additionalTypes)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get a playlist owned by a Spotify user", apiMethodParms)
                
            # are spotify web player credentials configured? if so, then we will use them to create
            # an elevated authorization access token for the Spotify Web API endpoint call.
            accessTokenHeaderValue:str = self._GetSpotifyWebPlayerTokenHeaderValue()

            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market)
            
            # if playlistId not specified, then return currently playing playlist id value.
            if (playlistId is None) or (len(playlistId.strip()) == 0):
                uri = self.GetPlayerNowPlayingPlaylistUri()
                if uri is not None:
                    playlistId = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'playlistId'), logsi=_logsi)

            # was the Spotify DJ playlist specified?
            # the DJ is not fully integrated with the playlist API, so the GET request will fail.
            # we will manually build a basic playlist object to return for the playlist.
            if (playlistId is not None) and (playlistId.lower() == SPOTIFY_DJ_PLAYLIST_ID):
                
                # build basic playlist response.
                result = Playlist()
                result._Collaborative = False
                result._Description = 'Spotify DJ Playlist'
                result._ExternalUrls._Spotify = SPOTIFY_ONLINE_LINK_PREFIX + "/playlist/" + playlistId
                result._Id = playlistId
                result._Name = 'DJ'
                result._Public = False
                result._Type = SpotifyMediaTypes.PLAYLIST.value
                result._Uri = 'spotify:playlist:%s' % playlistId
                               
                # trace.
                _logsi.LogVerbose("Spotify DJ Playlist detected; request will be bypassed, and a basic PlayList object returned")
                _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
                return result

            # build spotify web api request parameters.
            urlParms:dict = {}
            if market is not None:
                urlParms['market'] = market
            if fields is not None:
                urlParms['fields'] = fields
            if additionalTypes is not None:
                urlParms['additional_types'] = additionalTypes

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/playlists/{id}'.format(id=playlistId))
            msg.RequestHeaders[self.AuthToken.HeaderKey] = accessTokenHeaderValue or self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)

            # process results.
            result = Playlist(root=msg.ResponseData)
        
            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetPlaylistCoverImage(
        self, 
        playlistId:str=None, 
        ) -> ImageObject:
        """
        Get the current image associated with a specific playlist.
        
        Args:
            playlistId (str):  
                The Spotify ID of the playlist.  
                If null, the currently playing playlist uri id value is used.  
                Example: `5v5ETK9WFXAnGQ3MRubKuE`
                
        Returns:
            A `ImageObject` object that contains the image details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetPlaylistCoverImage.py
        ```
        </details>
        """
        apiMethodName:str = 'GetPlaylistCoverImage'
        apiMethodParms:SIMethodParmListContext = None
        result:ImageObject = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("playlistId", playlistId)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get the current image associated with a specific playlist", apiMethodParms)
                
            # if playlistId not specified, then return currently playing playlist id value.
            if (playlistId is None) or (len(playlistId.strip()) == 0):
                uri = self.GetPlayerNowPlayingPlaylistUri()
                if uri is not None:
                    playlistId = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'playlistId'), logsi=_logsi)

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/playlists/{playlist_id}/images'.format(playlist_id=playlistId))
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            self.MakeRequest('GET', msg)

            # process results.
            # this should always be a list with 1 item, as there is only 1 image for playlist cover art.
            items:list = msg.ResponseData
            for item in items:
                result = ImageObject(root=item)
                break
        
            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetPlaylistItems(
        self, 
        playlistId:str=None, 
        limit:int=50,
        offset:int=0,
        market:str=None,
        fields:str=None,
        additionalTypes:str=None,
        limitTotal:int=None
        ) -> PlaylistPage:
        """
        Get full details of the items of a playlist owned by a Spotify user.
        
        This method requires the `playlist-read-private` scope.
        
        Args:
            playlistId (str):  
                The Spotify ID of the playlist.  
                Example: `5v5ETK9WFXAnGQ3MRubKuE`
                If null, the currently playing playlist uri id value is used.
            limit (int):
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 50, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            offset (int):
                The page index offset of the first item to return.  
                Use with limit to get the next set of items.  
                Default: 0 (the first item).  
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
            fields (str):
                Filters for the query: a comma-separated list of the fields to return.  
                If omitted, all fields are returned. 
                For example, to get just the playlist's description and URI:  
                `fields=description,uri`. 
                A dot separator can be used to specify non-reoccurring fields, while parentheses can be used 
                to specify reoccurring fields within objects. For example, to get just the added date and user 
                ID of the adder:  
                `fields=items(added_at,added_by.id)`.   
                Use multiple parentheses to drill down into nested objects, for example:  
                `fields=items(track(name,href,album(name,href)))`.  
                Fields can be excluded by prefixing them with an exclamation mark, for example:  
                `fields=items(track(name,href,album(!name,href)))`  
                Example: fields=items(added_by.id,track(name,href,album(name,href)))
            additionalTypes (str):
                A comma-separated list of item types that your client supports besides the default track type.  
                Valid types are: track and episode.  
                Note: This parameter was introduced to allow existing clients to maintain their current behaviour 
                and might be deprecated in the future.  In addition to providing this parameter, make sure that your 
                client properly handles cases of new types in the future by checking against the type field of each object.                
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  * See notes below.
                Default: None (disabled)
                
        Returns:
            A `PlaylistPage` object that contains the playlist items.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.  

        <span class="warning">
            <b>Notes regarding `limit_total` processing</b>  
            There appears to be a bug in the Spotify Web API that forces you to use manual paging if 
            utilizing the `fields` argument.  It has been found that the API will only return a value
            of 50 (maximum) or less in the page `total` value if the `fields` argument is supplied.  
            The API will return the total number of playlist items in the page `total` value if the `fields` 
            argument is NOT supplied.  A good playlist id to test this on is `1XhVM7jWPrGLTiNiAy97Za`,
            which is the largest playlist on spotify (4700+ items).
        <span>
        
        <span class="warning">
            <b>DEPRECATED functionality as of 2024/11/27</b>  
            Spotify Algorithmic playlists (e.g. "Made For You", "Daily Mix n", etc) will no longer be included 
            in the returned results for unauthorized Spotify Developer Applications; they will be included in 
            the results for authorized Spotify Developer Applications.  More information about the deprecated 
            functionality can be found on the <a href="https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api" 
            target="_blank">Spotify Developer Forum Blog</a> page.
        <span>

        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetPlaylistItems.py
        ```
        </details>
        <details>
          <summary>Sample Code - Auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetPlaylistItems_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'GetPlaylistItems'
        apiMethodParms:SIMethodParmListContext = None
        result:PlaylistPage = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("playlistId", playlistId)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("offset", offset)
            apiMethodParms.AppendKeyValue("market", market)
            apiMethodParms.AppendKeyValue("fields", fields)
            apiMethodParms.AppendKeyValue("additionalTypes", additionalTypes)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get full details of the items of a playlist owned by a Spotify user", apiMethodParms)
                
            # are spotify web player credentials configured? if so, then we will use them to create
            # an elevated authorization access token for the Spotify Web API endpoint call.
            accessTokenHeaderValue:str = self._GetSpotifyWebPlayerTokenHeaderValue()

            # validations.
            if limit is None: 
                limit = 20
            if offset is None: 
                offset = 0
            if not isinstance(limitTotal, int):
                limitTotal = 0
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = PlaylistPage()

            # ensure we have a market value, in order to return track relinking (e.g. `linked_from`) data.
            market = self._ValidateMarket(market, forceReturnValue=True)

            # if playlistId not specified, then return currently playing playlist id value.
            if (playlistId is None) or (len(playlistId.strip()) == 0):
                uri = self.GetPlayerNowPlayingPlaylistUri()
                if uri is not None:
                    playlistId = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'playlistId'), logsi=_logsi)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'limit': limit,
                'offset': offset,
            }
            if market is not None:
                urlParms['market'] = market
            if fields is not None:
                urlParms['fields'] = fields
            if additionalTypes is not None:
                urlParms['additional_types'] = additionalTypes

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/playlists/{id}/tracks'.format(id=playlistId))
                msg.RequestHeaders[self.AuthToken.HeaderKey] = accessTokenHeaderValue or self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                pageObj = PlaylistPage(root=msg.ResponseData)

                # trace.
                _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:PlaylistTrack
                    for item in pageObj.Items:
                        result.Items.append(item)
                        result.Limit = result.ItemsCount
                        if result.ItemsCount >= limitTotal:
                            break
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithOffset(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break

            # update result object with final paging details.
            result.Total = pageObj.Total
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # do not sort this list, as it is in play order.
            
            # trace.
            _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE + result.PagingInfo) % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetPlaylistFavorites(
        self, 
        limit:int=20, 
        offset:int=0,
        limitTotal:int=None,
        sortResult:bool=True,
        ) -> PlaylistPageSimplified:
        """
        Get a list of the playlists owned or followed by the current Spotify user.

        This method requires the `playlist-read-private` scope.

        Args:
            limit (int):
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            offset (int):
                The page index offset of the first item to return.  
                Use with limit to get the next set of items.  
                Default: 0 (the first item).  
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
            sortResult (bool):
                True to sort the items by name; otherwise, False to leave the items in the same order they 
                were returned in by the Spotify Web API.  
                Default: True
                
        Returns:
            An `PlaylistPageSimplified` object that contains playlist information.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.  

        <span class="warning">
            <b>DEPRECATED functionality as of 2024/11/27</b>  
            Spotify Algorithmic playlists (e.g. "Made For You", "Daily Mix n", etc) will no longer be included 
            in the returned results for unauthorized Spotify Developer Applications; they will be included in 
            the results for authorized Spotify Developer Applications.  More information about the deprecated 
            functionality can be found on the <a href="https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api" 
            target="_blank">Spotify Developer Forum Blog</a> page.
        <span>

        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetPlaylistFavorites.py
        ```
        </details>
        <details>
          <summary>Sample Code - Auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetPlaylistFavorites_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'GetPlaylistFavorites'
        apiMethodParms:SIMethodParmListContext = None
        result:PlaylistPageSimplified = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("offset", offset)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            apiMethodParms.AppendKeyValue("sortResult", sortResult)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get a list of the users playlist favorites", apiMethodParms)
                
            # are spotify web player credentials configured? if so, then we will use them to create
            # an elevated authorization access token for the Spotify Web API endpoint call.
            accessTokenHeaderValue:str = self._GetSpotifyWebPlayerTokenHeaderValue()

            # validations.
            if limit is None: 
                limit = 20
            if offset is None: 
                offset = 0
            if not isinstance(limitTotal, int):
                limitTotal = 0
            if sortResult is None: 
                sortResult = True
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = PlaylistPageSimplified()

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'limit': limit,
                'offset': offset,
            }

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/playlists')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = accessTokenHeaderValue or self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                pageObj = PlaylistPageSimplified(root=msg.ResponseData)

                # trace.
                _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:PlaylistSimplified
                    for item in pageObj.Items:
                        result.Items.append(item)
                        result.Limit = result.ItemsCount
                        if result.ItemsCount >= limitTotal:
                            break
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithOffset(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break

            # update result object with final paging details.
            result.Total = pageObj.Total
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # sort result items.
            if (len(result.Items) > 0):
                if (sortResult is True):
                    result.Items.sort(key=lambda x: (x.Name or "").lower(), reverse=False)
            
            # trace.
            _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE + result.PagingInfo) % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetPlaylistsForUser(
        self, 
        userId:str,
        limit:int=20, 
        offset:int=0,
        limitTotal:int=None,
        sortResult:bool=True,
        ) -> PlaylistPageSimplified:
        """
        Get a list of the playlists owned or followed by a Spotify user.
        
        This method requires the `playlist-read-private` and `playlist-read-collaborative` scope.

        Args:
            userId (str):
                The user's Spotify user ID.  
                Example: `smedjan`
            limit (int):
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            offset (int):
                The page index offset of the first item to return.  
                Use with limit to get the next set of items.  
                Default: 0 (the first item).  
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
            sortResult (bool):
                True to sort the items by name; otherwise, False to leave the items in the same order they 
                were returned in by the Spotify Web API.  
                Default: True
                
        Returns:
            An `PlaylistPageSimplified` object that contains user playlist information.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetPlaylistsForUser.py
        ```
        </details>
        <details>
          <summary>Sample Code - Auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetPlaylistsForUser_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'GetPlaylistsForUser'
        apiMethodParms:SIMethodParmListContext = None
        result:PlaylistPageSimplified = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("userId", userId)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("offset", offset)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            apiMethodParms.AppendKeyValue("sortResult", sortResult)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get a list of the playlists owned or followed by a Spotify user", apiMethodParms)
                
            # validations.
            if limit is None: 
                limit = 20
            if offset is None: 
                offset = 0
            if not isinstance(limitTotal, int):
                limitTotal = 0
            if sortResult is None: 
                sortResult = True
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = PlaylistPageSimplified()

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'userId': userId,
                'limit': limit,
                'offset': offset,
            }

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/users/{user_id}/playlists'.format(user_id=userId))
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                pageObj = PlaylistPageSimplified(root=msg.ResponseData)

                # trace.
                _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:PlaylistSimplified
                    for item in pageObj.Items:
                        result.Items.append(item)
                        result.Limit = result.ItemsCount
                        if result.ItemsCount >= limitTotal:
                            break
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithOffset(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break

            # update result object with final paging details.
            result.Total = pageObj.Total
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # sort result items.
            if (len(result.Items) > 0):
                if (sortResult is True):
                    result.Items.sort(key=lambda x: (x.Name or "").lower(), reverse=False)
            
            # trace.
            _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE + result.PagingInfo) % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetShow(
        self, 
        showId:str=None, 
        market:str=None,
        ) -> Show:
        """
        Get Spotify catalog information for a single show identified by its unique Spotify ID.
        
        Args:
            showId (str):  
                The Spotify ID for the show.
                Example: `5CfCWKI5pZ28U0uOzXkDHe`
                If null, the currently playing show uri id value is used; a Spotify Free or Premium account 
                is required to correctly read the currently playing context.
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
                
        Returns:
            A `Show` object that contain the show details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        Important policy notes:  
        - Spotify content may not be downloaded.  
        - Keep visual content in its original form.  
        - Ensure content attribution.  
        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetShow.py
        ```
          <summary>Sample Code - NowPlaying</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetShow_NowPlaying.py
        ```
        </details>
        """
        apiMethodName:str = 'GetShow'
        apiMethodParms:SIMethodParmListContext = None
        result:Show = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("showId", showId)
            apiMethodParms.AppendKeyValue("market", market)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get Spotify catalog information for a single show", apiMethodParms)
                
            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market)

            # if showId not specified, then return currently playing show id value.
            if (showId is None) or (len(showId.strip()) == 0):
                uri = self.GetPlayerNowPlayingShowUri()
                if uri is not None:
                    showId = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'showId'), logsi=_logsi)

            # build spotify web api request parameters.
            urlParms:dict = {}
            if market is not None:
                urlParms['market'] = market

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/shows/{id}'.format(id=showId))
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)

            # process results.
            result = Show(root=msg.ResponseData)
        
            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetShowEpisodes(
        self, 
        showId:str=None, 
        limit:int=20, 
        offset:int=0,
        market:str=None,
        limitTotal:int=None
        ) -> EpisodePageSimplified:
        """
        Get Spotify catalog information about a show's episodes.
        
        Optional parameters can be used to limit the number of episodes returned.
        
        Args:
            showId (str):  
                The Spotify ID for the show.
                Example: `6kAsbP8pxwaU2kPibKTuHE`
                If null, the currently playing show uri id value is used; a Spotify Free or Premium account 
                is required to correctly read the currently playing context.
            limit (int):  
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            offset (int):  
                The index of the first item to return; use with limit to get the next set of items.  
                Default: 0 (the first item).  
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
                
        Returns:
            A `EpisodePageSimplified` object that contains simplified track information for the showId.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetShowEpisodes.py
        ```
        </details>
        <details>
          <summary>Sample Code - Auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetShowEpisodes_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'GetShowEpisodes'
        apiMethodParms:SIMethodParmListContext = None
        result:EpisodePageSimplified = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("showId", showId)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("offset", offset)
            apiMethodParms.AppendKeyValue("market", market)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get Spotify catalog information about a show's episodes", apiMethodParms)
                
            # validations.
            if limit is None: 
                limit = 20
            if offset is None: 
                offset = 0
            if not isinstance(limitTotal, int):
                limitTotal = 0
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = EpisodePageSimplified()

            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market)

            # if showId not specified, then return currently playing show id value.
            if (showId is None) or (len(showId.strip()) == 0):
                uri = self.GetPlayerNowPlayingShowUri()
                if uri is not None:
                    showId = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'showId'), logsi=_logsi)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'limit': limit,
                'offset': offset,
            }
            if market is not None:
                urlParms['market'] = market

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/shows/{id}/episodes'.format(id=showId))
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                pageObj = EpisodePageSimplified(root=msg.ResponseData)

                # trace.
                _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:EpisodeSimplified
                    for item in pageObj.Items:
                        result.Items.append(item)
                        result.Limit = result.ItemsCount
                        if result.ItemsCount >= limitTotal:
                            break
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithOffset(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break

            # update result object with final paging details.
            result.Total = pageObj.Total
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # no sort, as items are in playable order.

            # trace.
            _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE + result.PagingInfo) % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetShowFavorites(
        self, 
        limit:int=20, 
        offset:int=0,
        limitTotal:int=None,
        sortResult:bool=True,
        excludeAudiobooks:bool=True,
        ) -> ShowPageSaved:
        """
        Get a list of the shows saved in the current Spotify user's 'Your Library'.
        
        This method requires the `user-library-read` scope.

        Args:
            limit (int):
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            offset (int):
                The page index offset of the first item to return.  
                Use with limit to get the next set of items.  
                Default: 0 (the first item).  
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
            sortResult (bool):
                True to sort the items by name; otherwise, False to leave the items in the same order they 
                were returned in by the Spotify Web API.  
                Default: True
            excludeAudiobooks (bool):
                True to exclude audiobook shows from the returned list, leaving only podcast shows;
                otherwise, False to include all results returned by the Spotify Web API.  
                Default: True  
                
        Returns:
            An `ShowPageSaved` object that contains saved show information.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.
                
        For some reason, Spotify Web API returns audiobooks AND podcasts with the `/me/shows` service.
        Spotify Web API returns only audiobooks with the `/me/audiobooks` service.
        The reasoning for that is unclear, but the `excludeAudiobooks` argument allows you to
        only return podcast shows in the results if desired.

        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetShowFavorites.py
        ```
        </details>
        <details>
          <summary>Sample Code - Auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetShowFavorites_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'GetShowFavorites'
        apiMethodParms:SIMethodParmListContext = None
        result:ShowPageSaved = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("offset", offset)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            apiMethodParms.AppendKeyValue("sortResult", sortResult)
            apiMethodParms.AppendKeyValue("excludeAudiobooks", excludeAudiobooks)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get a list of the users show favorites", apiMethodParms)
                
            # validations.
            if limit is None: 
                limit = 20
            if offset is None: 
                offset = 0
            if not isinstance(limitTotal, int):
                limitTotal = 0
            if sortResult is None: 
                sortResult = True
            if excludeAudiobooks is None: 
                excludeAudiobooks = True
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = ShowPageSaved()

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'limit': limit,
                'offset': offset,
            }

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/shows')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                pageObj = ShowPageSaved(root=msg.ResponseData)
            
                # trace.
                _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:ShowSaved
                    for item in pageObj.Items:
                        # sometimes spotify api returns items with no information; discard these!
                        if (item.Show is not None) and (item.Show.Uri is not None):
                            result.Items.append(item)
                            result.Limit = result.ItemsCount
                            if result.ItemsCount >= limitTotal:
                                break
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithOffset(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break

            # exclude audiobook shows if requested.
            if (excludeAudiobooks):

                item:ShowSaved
                idx:int = 0
                while idx < len(result.Items):
                    if (result.Items[idx].Show is not None) \
                    and (result.Items[idx].Show.Description is not None) \
                    and (result.Items[idx].Show.Description.startswith('Author(s):')):
                        del result.Items[idx]
                        pageObj.Total -= 1
                    else:
                        idx += 1

            # update result object with final paging details.
            result.Total = pageObj.Total
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # sort result items.
            if (len(result.Items) > 0):
                if (sortResult is True):
                    result.Items.sort(key=lambda x: (x.Show.Name or "").lower(), reverse=False)
                else:
                    result.Items.sort(key=lambda x: (x.AddedAt or "").lower(), reverse=True)
            
            # trace.
            _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE + result.PagingInfo) % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetShows(
        self, 
        ids:str, 
        market:str=None,
        ) -> list[ShowSimplified]:
        """
        Get Spotify catalog information for several shows based on their Spotify IDs.
        
        Args:
            ids (str):  
                A comma-separated list of the Spotify IDs for the shows.  
                Maximum: 50 IDs.  
                Example: `5CfCWKI5pZ28U0uOzXkDHe,5as3aKmN2k11yfDDDSrvaZ`
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
                
        Returns:
            A list of `ShowSimplified` objects that contain the show details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        Important policy notes:  
        - Spotify content may not be downloaded.  
        - Keep visual content in its original form.  
        - Ensure content attribution.  
        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetShows.py
        ```
        </details>
        """
        apiMethodName:str = 'GetShows'
        apiMethodParms:SIMethodParmListContext = None
        result:list[ShowSimplified] = []
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            apiMethodParms.AppendKeyValue("market", market)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get Spotify catalog information for multiple shows", apiMethodParms)
                
            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'ids': ids,
            }
            if market is not None:
                urlParms['market'] = market

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/shows')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)

            # process results.
            items = msg.ResponseData.get('shows',None)
            if items is not None:
                for item in items:
                    result.append(ShowSimplified(root=item))
        
            # trace.
            _logsi.LogArray(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, 'list[ShowSimplified]'), result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetSpotifyConnectDevice(
        self, 
        deviceValue:str, 
        verifyUserContext:bool=True,
        verifyTimeout:float=5.0,
        refreshDeviceList:bool=False,
        activateDevice:bool=True,
        delay:float=0.25
        ) -> Device:
        """
        Get information about a specific Spotify Connect player device, and (optionally)
        activate the device if it requires it.
        
        This method requires the `user-read-playback-state` scope.
        
        Resolves a Spotify Connect device from a specified device id, name, alias id,
        or alias name.  This will ensure that the device can be found on the network, and that
        playback can be immediately transferred to the device.
        
        Args:
            deviceValue (str):
                The device id / name value to check.
            verifyUserContext (bool):
                DEPRECATED - no longer used, but left here to maintain compatibility.
            verifyTimeout (float):
                Maximum time to wait (in seconds) for the device to become active in the Spotify
                Connect device list.  This value is only used if a Connect command has to be
                issued to activate the device.
                Default is 5; value range is 0 - 10.
            refreshDeviceList (bool):
                DEPRECATED - no longer used, but left here to maintain compatibility.
            activateDevice (bool):
                True to activate the device if necessary; otherwise, False.  
                Default is True.  
            delay (float):
                Time delay (in seconds) to wait AFTER issuing any command to the device.  
                This delay will give the spotify zeroconf api time to process the change before 
                another command is issued.  
                Default is 0.25; value range is 0 - 10.
                
        Returns:
            A `SpotifyConnectDevice` object for the deviceValue if one could be resolved.
            otherwise, a null value with the understanding that subsequent operations will probably 
            fail since it's not in the Spotify Connect device list.  
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyZeroconfApiError:
                If any Spotify Zeroconf API request failed.
            SpotifyApiError: 
                If the `deviceValue` could not be resolved to a valid device instance.
                If the `spotifyConnectLoginId` argument was not specified for the class contructor.  
                If the `spotifyConnectUsername` argument was not specified for the class contructor.  
                If the `spotifyConnectPassword` argument was not specified for the class contructor.  
                If the method fails for any other reason.

        The Spotify Connect discovery list is searched for the specified device value; the search will 
        match on either a Device ID or RemoteName as well as any alias ID's or Names that are in use.
        The cached Spotify Connect Directory will be used to resolve the device object.
        
        The `SpotifyConnectDevice` object is returned if a match is found; otherwise, an exception is
        raised to indicate an unknown device which would be returned anyway by Spotify Web API.

        A Spotify Connect Zeroconf Disconnect (e.g. `resetUsers`) will be issued if the `activateDevice`
        argument is True, AND the device is not a dynamic device.  This will temporarily remove the device
        from the Spotify Connect device list, but the device will be re-added when the Connect
        call is issued.
        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetSpotifyConnectDevice.py
        ```
        </details>
        """
        apiMethodName:str = 'GetSpotifyConnectDevice'
        apiMethodParms:SIMethodParmListContext = None
        scDevice:SpotifyConnectDevice = None
        sonosPlayer:SoCo = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("deviceValue", deviceValue)
            apiMethodParms.AppendKeyValue("verifyUserContext (DEPRECATED)", verifyUserContext)
            apiMethodParms.AppendKeyValue("verifyTimeout", verifyTimeout)
            apiMethodParms.AppendKeyValue("refreshDeviceList (DEPRECATED)", refreshDeviceList)
            apiMethodParms.AppendKeyValue("activateDevice", activateDevice)
            apiMethodParms.AppendKeyValue("delay", delay)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get Spotify Connect Device object for deviceValue \"%s\"" % (deviceValue), apiMethodParms)

            # validations.
            delay = validateDelay(delay, 0.25, 10)
            verifyTimeout = validateDelay(verifyTimeout, 5, 10)
            if (activateDevice is None):
                activateDevice = True

            # resolve the device id from the specified device value.
            # returned value will be null if the device could not be resolved!
            scDevice = self._SpotifyConnectDirectory.GetDevice(deviceValue, refreshDynamicDevices=True, raiseExceptionIfNotFound=False)

            # if device could not be resolved, then go no further as it will result in a 
            # "device not found" error from the Spotify Web API anyway!
            if (scDevice is None):
                _logsi.LogVerbose("Spotify Player device was not found, and there is no active Spotify player; no need to re-activate")
                return None

            discovery:ZeroconfDiscoveryResult = scDevice.DiscoveryResult
            info:ZeroconfGetInfo = scDevice.DeviceInfo
            scDevice.WasReConnected = False

            # is the device already active? if so, then we are done.
            if (scDevice.IsActiveDevice):
                _logsi.LogVerbose("Spotify Connect device %s is already active; no need to re-activate" % (scDevice.Title))
                return scDevice

            # is this an amazon device? if so, then we will issue a transfer playback call 
            # to wake it up and make it the active device.  this call usually fails so we
            # will wrap it up in a "try ... catch" block.  we will keep calling transfer
            # playback until it activates the device, or we time out.
            if (scDevice.IsAmazonDevice):
                if (activateDevice):

                    # wait for the amazon device to become the active device.
                    loopTotalDelay:float = 0
                    LOOP_DELAY:float = 0.500
                    while True:
                        
                        try:
                            _logsi.LogVerbose("Re-activating Amazon Spotify Connect device: %s" % (scDevice.Title))

                            # are spotify web player credentials configured? if so, then we will use them to create
                            # an elevated authorization access token for the Spotify Web API endpoint call.
                            accessTokenHeaderValue:str = self._GetSpotifyWebPlayerTokenHeaderValue()

                            # build spotify web api request parameters.
                            reqData:dict = \
                            {
                                'device_ids': [(scDevice.DeviceIdActivated or scDevice.Id)],
                                'play': False
                            }

                            # execute spotify web api request.
                            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/player')
                            msg.RequestHeaders[self.AuthToken.HeaderKey] = accessTokenHeaderValue or self.AuthToken.HeaderValue
                            msg.RequestJson = reqData
                            self.MakeRequest('PUT', msg)
            
                        except Exception as ex:
                            _logsi.LogVerbose("Ignored Amazon Spotify Connect reactivation exception for device: %s - %s" % (scDevice.Title, str(ex)))

                        # wait just a bit between active device queries.
                        _logsi.LogVerbose(TRACE_MSG_DELAY_DEVICE % LOOP_DELAY)
                        time.sleep(LOOP_DELAY)
                        loopTotalDelay = loopTotalDelay + LOOP_DELAY

                        # get the currently active player device.
                        scActiveDevice:SpotifyConnectDevice = self._SpotifyConnectDirectory.GetActiveDevice(refresh=True)

                        # is the amazon device the active player device? if so, then we are done.
                        if (scActiveDevice is not None):
                            if (scActiveDevice.Name == scDevice.Name) or (scActiveDevice.Id == scDevice.Id):
                                _logsi.LogVerbose("Amazon Spotify Connect device %s is now the active player device; device found within %f seconds of Connect" % (scDevice.Title, loopTotalDelay))
                                scDevice = scActiveDevice
                                break

                        # only check so many times before we give up;
                        # we will keep checking until we find the device, or we exceed the verifyTimeout value.
                        if (loopTotalDelay > verifyTimeout):
                            _logsi.LogWarning("Verification timeout waiting for Amazon Spotify Connect device %s to become the active device; device not activated within %f seconds of Connect" % (scDevice.Title, verifyTimeout))
                            break

                    # return device to caller.
                    return scDevice

            # is the device in the player device list? if so, then it's ready to be selected.
            # note that if another user is controlling the device, then it will not be in the 
            # active device list for the current user.
            if (scDevice.IsInDeviceList):
                _logsi.LogVerbose("Spotify Connect device %s is already in the available device list; no need to re-activate" % (scDevice.Title))
                return scDevice

            # if this is a Sonos device and there is no Spotify Client Application token then don't bother.
            # in this case, we will exit and let the calling method switch to the Sonos device and play 
            # using the Sonos local queue.
            if (scDevice.IsSonos):

                # check if the Spotify Desktop Application Client oauth2 token is defined.
                hasToken:bool = AuthClient.HasTokenForKey(
                    clientId=SPOTIFY_DESKTOP_APP_CLIENT_ID,
                    tokenProviderId='SpotifyWebApiAuthCodePkce',
                    tokenProfileId=self._SpotifyConnectLoginId,
                    tokenStorageDir=self.TokenStorageDir,
                    tokenStorageFile=self.TokenStorageFile,
                )
                
                # if no token, then just return the device and hope it works.
                if not hasToken:
                    _logsi.LogVerbose("Spotify Desktop Application Client oauth2 token was not found for Spotify LoginId: '%s'" % (self._SpotifyConnectLoginId))
                    return scDevice

                # get Sonos Controller instance for the device.
                _logsi.LogVerbose("Target device is Sonos; getting Sonos Controller instance for device %s" % (scDevice.Title))
                sonosPlayer = self.SpotifyConnectDirectory.GetSonosPlayer(scDevice)

            # was device activation requested?  if not, then we are done.
            if (not activateDevice):
                _logsi.LogVerbose("Activation not requested for Spotify Connect device: %s" % (scDevice.Title))
                return scDevice
            
            # at this point, we will try to activate the device if needed.
                    
            # chromecast devices always require activation if they are not the active device.
            # note that `transferPlayback=false`, as transfer should be done after we return to caller.
            if (scDevice.IsChromeCast):

                # activate the spotify cast application on the device.
                _logsi.LogVerbose("Activating Chromecast Spotify Connect device: %s on host ip: %s" % (scDevice.Title, scDevice.DiscoveryResult.HostIpTitle))
                deviceIdActivated:str = self._SpotifyConnectDirectory.ActivateCastAppSpotify(scDevice.Id or scDevice.Name, transferPlayback=False)

                # re-fetch device instance, as it has updated properties from the activation sequence.
                # do not need to refresh from Spotify Web API, as only zeroconf response data was changed.
                scDevice = self._SpotifyConnectDirectory.GetDevice(deviceValue, refreshDynamicDevices=False)
                
                # return device to caller.
                return scDevice

            zcfResult:ZeroconfResponse

            # store the currently active user of the device, in case we need to switch users later on.
            oldActiveUser:str = info.ActiveUser.lower()
                
            # create a ZeroconfConnect object to access the device.
            # note that we are using the "HostIpAddress" property value here, with "Server" as a fallback.
            # the "Server" property is an alias, which must be resolved via a DNS lookup under
            # the covers and adds a significant delay (2-3 seconds!) to the activation time.
            zconn:ZeroconfConnect = ZeroconfConnect(
                discovery.HostIpAddress, 
                discovery.HostIpPort, 
                discovery.SpotifyConnectCPath,
                useSSL=False,
                tokenStorageDir=self.TokenStorageDir,
                tokenStorageFile=self.TokenStorageFile)
            
            # is this a Sonos device?
            if (scDevice.IsSonos):
                               
                # trace.
                sonosMusicSource:str = sonosPlayer.music_source
                _logsi.LogVerbose("Sonos device %s music source before Connect: \"%s\"" % (scDevice.Title, sonosMusicSource))

                # was the Sonos device music source set to SPOTIFY_CONNECT?
                # if not, then issue a Disconnect to (hopefully) reset the music source. this should allow
                # the subsequent Connect to re-establish a SPOTIFY_CONNECT music source on the Sonos device.
                if sonosMusicSource != "SPOTIFY_CONNECT":
                    _logsi.LogVerbose("Issuing Disconnect to Sonos Spotify Connect device %s" % (scDevice.Title))
                    zcfResult = zconn.Disconnect(ignoreStatusResult=True)

            # connect the device to OUR Spotify Connect user context.
            # note that the result here only indicates that the connect was submitted - NOT that it was successful!
            _logsi.LogVerbose("Issuing Connect to Spotify Connect device %s for user context \"%s\" (ip=%s:%s)" % (scDevice.Title, self._SpotifyConnectLoginId, zconn.HostIpAddress, zconn.HostIpPort))
            zcfResult = zconn.Connect(self._SpotifyConnectUsername, self._SpotifyConnectPassword, self._SpotifyConnectLoginId)
                    
            # indicate device was reconnected.
            scDevice.WasReConnected = True
                    
            # trace.
            _logsi.LogVerbose("User context switched from \"%s\" to \"%s\" for Spotify Connect device %s" % (oldActiveUser, self._SpotifyConnectLoginId, scDevice.Title))

            # is this a Sonos device?
            if (scDevice.IsSonos):
                               
                # trace.
                sonosMusicSource:str = sonosPlayer.music_source
                _logsi.LogVerbose("Sonos device %s music source after Connect: \"%s\"" % (scDevice.Title, sonosMusicSource))

                # was the Sonos device music source set to Spotify Connect?
                # if not, then it's a lost cause at this point since it's probably in an UNKNOWN state.
                if sonosMusicSource != "SPOTIFY_CONNECT":
                    _logsi.LogVerbose("Sonos device %s music source after Connect is not SPOTIFY_CONNECT; it will probably fail to play" % (scDevice.Title))
                elif (self.HasSpotifyWebPlayerCredentials):
                    # if using Spotify Web Player credentials, then we don't have to wait for device.
                    _logsi.LogVerbose("Sonos device with Spotify Web Player Credentials detected; no need to wait for device active player device")
                    return scDevice
                else:
                    # if not using Spotify Web Player credentials, then resume play on the device.
                    # at this point the music source is "SPOTIFY_CONNECT", so it should transfer control.
                    self.PlayerMediaResume(scDevice)

            # at this point the Sonos music source should be set to SPOTIFY_CONNECT, and control
            # transferred to the device.  note that the Sonos device will still NOT appear in the 
            # player device list, but SHOULD be the active (restricted) device in player state.
                
            # wait for the device to enter the Spotify Web API player device list, or
            # to become the active device.  
            # Sonos devices are famous for not showing up in the device list, but DO 
            # appear as the active (restricted) device!  Note that if using Spotify Web Player 
            # Credentials, they will not appear as the active device until AFTER the transfer
            # playback endpoint has been called.
            loopTotalDelay:float = 0
            LOOP_DELAY:float = 0.350
            while True:
                        
                # wait just a bit between available device list queries.
                _logsi.LogVerbose(TRACE_MSG_DELAY_DEVICE % LOOP_DELAY)
                time.sleep(LOOP_DELAY)
                loopTotalDelay = loopTotalDelay + LOOP_DELAY

                # refresh the player device list, and return the active device.
                scActiveDevice:SpotifyConnectDevice = self._SpotifyConnectDirectory.RefreshDynamicDevices()

                # is the device the active player device?
                # sometimes restricted devices will not appear in the player device list (e.g. Sonos),
                # so we need to check the active player device as well.
                if (scActiveDevice is not None):
                    if (scActiveDevice.Name == scDevice.Name) or (scActiveDevice.Id == scDevice.Id):
                        _logsi.LogVerbose("Spotify Connect device %s is now the active player device; device found within %f seconds of Connect" % (scDevice.Title, loopTotalDelay))
                        scDevice = scActiveDevice
                        break

                # was the device name added to the player device list?
                # note that we already refreshed dynamic devices above, so no need to do it again.
                scPlayerDevice:SpotifyConnectDevice = self._SpotifyConnectDirectory.GetPlayerDevice(scDevice.Name, refresh=False)
                if (scPlayerDevice is not None):
                    _logsi.LogVerbose("Spotify Connect device %s is now in the available device list; device found (by Name) within %f seconds of Connect" % (scDevice.Title, loopTotalDelay))
                    scDevice = scPlayerDevice
                    break
                        
                # was the device id added to the player device list?
                # note that we already refreshed dynamic devices above, so no need to do it again.
                scPlayerDevice:SpotifyConnectDevice = self._SpotifyConnectDirectory.GetPlayerDevice(scDevice.Id, refresh=False)
                if (scPlayerDevice is not None):
                    _logsi.LogVerbose("Spotify Connect device %s is now in the available device list; device found (by Id) within %f seconds of Connect" % (scDevice.Title, loopTotalDelay))
                    scDevice = scPlayerDevice
                    break
                        
                # only check so many times before we give up;
                # we will keep checking until we find the device, or we exceed the verifyTimeout value.
                if (loopTotalDelay > verifyTimeout):
                    _logsi.LogWarning("Verification timeout waiting for Spotify Connect device %s to be added to the player device list or become the active device; device not found within %f seconds of Connect" % (scDevice.Title, verifyTimeout))
                    break

            # return the device instance.
            return scDevice

        except SpotifyZeroconfApiError: raise  # pass handled exceptions on thru
        except SpotifyApiError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetSpotifyConnectDevices(
        self, 
        refresh:bool=True,
        sortResult:bool=True,
        ) -> SpotifyConnectDevices:
        """
        Get information about all available Spotify Connect player devices.
        
        This method requires the `user-read-playback-state` scope.
        
        Args:
            refresh (bool):
                True (default) to return real-time information about devices and update the cache;
                otherwise, False to just return the cached value.
            sortResult (bool):
                DEPRECATED - no longer used, but left here to maintain compatibility.
        
        Returns:
            A `SpotifyConnectDevices` object that contain Spotify Connect devices that are registered
            with Zeroconf on the local network, as well as dynamic devices that are only known to the
            Spotify Web API.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        The current list of devices is copied from the Zeroconf Directory task master device list, which
        contains a real-time update of Spotify Connect Zeroconf devices.
        
        If the `refresh` argument is true, a real-time query of the Spotify Web API is also performed 
        to retrieve the active player (from playerState) as well as player dynamic devices.
        
        Dynamic devices are Spotify Connect devices that are not found in the Zeroconf discovery
        process, but still exist in the player device list.  These are usually Spotify Connect
        web or mobile players with temporary device id's.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetSpotifyConnectDevices.py
        ```
        </details>
        """
        apiMethodName:str = 'GetSpotifyConnectDevices'
        apiMethodParms:SIMethodParmListContext = None
        result:SpotifyConnectDevices = SpotifyConnectDevices()
        cacheDesc:str = CACHE_SOURCE_CURRENT
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("refresh", refresh)
            apiMethodParms.AppendKeyValue("sortResult (DEPRECATED)", sortResult)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get available Spotify Connect devices", apiMethodParms)

            # validations.
            if refresh is None:
                refresh = True

            # give zeroconf threads a chance to catch up if needed.
            time.sleep(0.25)

            # if requested, refresh dynamic devices and the active player.
            if (refresh):
                self._SpotifyConnectDirectory.RefreshDynamicDevices()

            # get devices from Spotify Connect Directory task.
            # note that collection is already sorted as devices are added.
            result = self._SpotifyConnectDirectory.GetDevices()

            # update cache.
            self._ConfigurationCache[apiMethodName] = result

            # trace.
            _logsi.LogArray(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE_CACHED % (apiMethodName, type(result).__name__, cacheDesc), result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetTrack(
        self, 
        trackId:str=None, 
        market:str=None,
        ) -> Track:
        """
        Get Spotify catalog information for a single track identified by its unique Spotify ID.
        
        Args:
            trackId (str):  
                The Spotify ID of the track.  
                Example: `1kWUud3vY5ij5r62zxpTRy`
                If null, the currently playing track uri id value is used; a Spotify Free or Premium account 
                is required to correctly read the currently playing context.
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
                
        Returns:
            A `Track` object that contains the track details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetTrack.py
        ```
          <summary>Sample Code - NowPlaying</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetTrack_NowPlaying.py
        ```
        </details>
        """
        apiMethodName:str = 'GetTrack'
        apiMethodParms:SIMethodParmListContext = None
        result:Track = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("trackId", trackId)
            apiMethodParms.AppendKeyValue("market", market)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get Spotify catalog information for a single track", apiMethodParms)

            # ensure we have a market value, in order to return track relinking (e.g. `linked_from`) data.
            market = self._ValidateMarket(market, forceReturnValue=True)

            # build spotify web api request parameters.
            urlParms:dict = { }
            if market is not None:
                urlParms['market'] = market
                
            # if trackId not specified, then return currently playing track id value.
            if (trackId is None) or (len(trackId.strip()) == 0):
                uri = self.GetPlayerNowPlayingUri(SpotifyMediaTypes.TRACK.value)
                if uri is not None:
                    trackId = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'trackId'), logsi=_logsi)

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/tracks/{id}'.format(id=trackId))
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)

            # process results.
            result = Track(root=msg.ResponseData)
        
            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetTrackAudioFeatures(
        self, 
        trackId:str=None, 
        ) -> AudioFeatures:
        """
        <span class="deprecated">
            DEPRECATED - api endpoint no longer supported by Spotify as of 2024/11/27 for unauthorized Spotify Developer Applications.
            The api endpoint IS still supported by Spotify for authorized Spotify Developer Applications.
            More information about the deprecated functionality can be found on the 
            <a href="https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api" target="_blank">Spotify Developer Forum Blog</a>
            page.
        </span>       
        
        Get audio feature information for a single track identified by its unique Spotify ID.
        
        Args:
            trackId (str):  
                The Spotify ID of the track.  
                Example: `1kWUud3vY5ij5r62zxpTRy`
                If null, the currently playing track uri id value is used; a Spotify Free or Premium account 
                is required to correctly read the currently playing context.
                
        Returns:
            An `AudioFeatures` object that contains the audio feature details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetTrackAudioFeatures.py
        ```
        </details>
        """
        apiMethodName:str = 'GetTrackAudioFeatures'
        apiMethodParms:SIMethodParmListContext = None
        result:AudioFeatures = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("trackId", trackId)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get audio feature information for a single track", apiMethodParms)
                
            # are spotify web player credentials configured? if so, then we will use them to create
            # an elevated authorization access token for the Spotify Web API endpoint call.
            accessTokenHeaderValue:str = self._GetSpotifyWebPlayerTokenHeaderValue()

            # if spotify web player credentials not configured then we are done; the Spotify Web API
            # endpoint is no longer supported by unauthorized Spotify Developer Applications as of 2024/11/27.
            if (accessTokenHeaderValue is None):
                raise SpotifyApiError(SAAppMessages.MSG_SPOTIFY_DEPRECATED_ENDPOINT % apiMethodName)

            # if trackId not specified, then return currently playing track id value.
            if (trackId is None) or (len(trackId.strip()) == 0):
                uri = self.GetPlayerNowPlayingUri(SpotifyMediaTypes.TRACK.value)
                if uri is not None:
                    trackId = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'trackId'), logsi=_logsi)

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/audio-features/{id}'.format(id=trackId))
            msg.RequestHeaders[self.AuthToken.HeaderKey] = accessTokenHeaderValue or self.AuthToken.HeaderValue
            self.MakeRequest('GET', msg)

            # process results.
            result = AudioFeatures(root=msg.ResponseData)
        
            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetTrackFavorites(
        self, 
        limit:int=20, 
        offset:int=0,
        market:str=None,
        limitTotal:int=None,
        sortResult:bool=True,
        ) -> TrackPageSaved:
        """
        Get a list of the tracks saved in the current Spotify user's 'Your Library'.
        
        This method requires the `user-library-read` scope.

        Args:
            limit (int):
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            offset (int):
                The page index offset of the first item to return.  
                Use with limit to get the next set of items.  
                Default: 0 (the first item).  
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
            sortResult (bool):
                True to sort the items by name; otherwise, False to leave the items in the same order they 
                were returned in by the Spotify Web API.  
                Default: True
                
        Returns:
            An `TrackPageSaved` object that contains saved track information.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetTrackFavorites.py
        ```
        </details>
        <details>
          <summary>Sample Code - Auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetTrackFavorites_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'GetTrackFavorites'
        apiMethodParms:SIMethodParmListContext = None
        result:TrackPageSaved = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("offset", offset)
            apiMethodParms.AppendKeyValue("market", market)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            apiMethodParms.AppendKeyValue("sortResult", sortResult)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get a list of the users track favorites", apiMethodParms)
                
            # validations.
            if limit is None: 
                limit = 20
            if offset is None: 
                offset = 0
            if not isinstance(limitTotal, int):
                limitTotal = 0
            if sortResult is None: 
                sortResult = True
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = TrackPageSaved()

            # ensure we have a market value, in order to return track relinking (e.g. `linked_from`) data.
            market = self._ValidateMarket(market, forceReturnValue=True)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'limit': limit,
                'offset': offset,
            }
            if market is not None:
                urlParms['market'] = market

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/tracks')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                pageObj = TrackPageSaved(root=msg.ResponseData)
            
                # trace.
                _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:TrackSaved
                    for item in pageObj.Items:
                        # sometimes spotify api returns items with no information; discard these!
                        if (item.Track is not None) and (item.Track.Uri is not None):
                            result.Items.append(item)
                            result.Limit = result.ItemsCount
                            if result.ItemsCount >= limitTotal:
                                break
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithOffset(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break

            # update result object with final paging details.
            result.Total = pageObj.Total
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # sort result items.
            if (len(result.Items) > 0):
                if (sortResult is True):
                    result.Items.sort(key=lambda x: (x.Track.Name or "").lower(), reverse=False)
                else:
                    result.Items.sort(key=lambda x: (x.AddedAt or "").lower(), reverse=True)

            # trace.
            _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE + result.PagingInfo) % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetTracks(
        self, 
        ids:list[str], 
        market:str=None,
        ) -> list[Track]:
        """
        Get Spotify catalog information for multiple tracks based on their Spotify IDs.
        
        Args:
            ids (list[str]):  
                A comma-separated list of the Spotify track IDs. 
                Maximum: 50 IDs.  
                Example: `7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B`
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
            
        Returns:
            A list of `Track` objects that contain the track details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetTracks.py
        ```
        </details>
        """
        apiMethodName:str = 'GetTracks'
        apiMethodParms:SIMethodParmListContext = None
        result:list[Track] = []
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            apiMethodParms.AppendKeyValue("market", market)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get Spotify catalog information for multiple tracks", apiMethodParms)
                
            # ensure we have a market value, in order to return track relinking (e.g. `linked_from`) data.
            market = self._ValidateMarket(market, forceReturnValue=True)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'ids': ids
            }
            if market is not None:
                urlParms['market'] = market

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/tracks')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)

            # process results.
            items = msg.ResponseData.get('tracks',None)
            if items is not None:
                for item in items:
                    result.append(Track(root=item))
        
            # trace.
            _logsi.LogArray(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, 'list[Track]'), result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetTracksAudioFeatures(
        self, 
        ids:list[str], 
        ) -> list[AudioFeatures]:
        """
        Get audio features for multiple tracks based on their Spotify IDs.
        
        Args:
            ids (list[str]):  
                A comma-separated list of the Spotify track IDs. 
                Maximum: 100 IDs.  
                Example: `7ouMYWpwJ422jRcDASZB7P,4VqPOruhp5EdPBeR92t6lQ,2takcwOaAZWiXQijPHIx7B`
            
        Returns:
            A list of `AudioFeatures` objects that contain the audio feature details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetTracksAudioFeatures.py
        ```
        </details>
        """
        apiMethodName:str = 'GetTracksAudioFeatures'
        apiMethodParms:SIMethodParmListContext = None
        result:list[AudioFeatures] = []
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get audio features for track(s)", apiMethodParms)
                
            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'ids': ids
            }

            # are spotify web player credentials configured? if so, then we will use them to create
            # an elevated authorization access token for the Spotify Web API endpoint call.
            accessTokenHeaderValue:str = self._GetSpotifyWebPlayerTokenHeaderValue()

            # if spotify web player credentials not configured then we are done; the Spotify Web API
            # endpoint is no longer supported by unauthorized Spotify Developer Applications as of 2024/11/27.
            if (accessTokenHeaderValue is None):
                raise SpotifyApiError(SAAppMessages.MSG_SPOTIFY_DEPRECATED_ENDPOINT % apiMethodName)

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/audio-features')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = accessTokenHeaderValue or self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)

            # process results.
            items = msg.ResponseData.get('audio_features',None)
            if items is not None:
                for item in items:
                    result.append(AudioFeatures(root=item))
        
            # trace.
            _logsi.LogArray(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, 'list[AudioFeatures]'), result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetTrackRecommendations(
        self, 
        limit:int=50, 
        market:str=None, 
        seedArtists:str=None, 
        seedGenres:str=None, 
        seedTracks:str=None, 
        minAcousticness:float=None, maxAcousticness:float=None, targetAcousticness:float=None, 
        minDanceability:float=None, maxDanceability:float=None, targetDanceability:float=None, 
        minDurationMS:int=None, maxDurationMS:int=None, targetDurationMS:int=None, 
        minEnergy:float=None, maxEnergy:float=None, targetEnergy:float=None, 
        minInstrumentalness:float=None, maxInstrumentalness:float=None, targetInstrumentalness:float=None, 
        minKey:int=None, maxKey:int=None, targetKey:int=None, 
        minLiveness:float=None, maxLiveness:float=None, targetLiveness:float=None, 
        minLoudness:float=None, maxLoudness:float=None, targetLoudness:float=None, 
        minMode:float=None, maxMode:float=None, targetMode:float=None, 
        minPopularity:int=None, maxPopularity:int=None, targetPopularity:int=None, 
        minSpeechiness:float=None, maxSpeechiness:float=None, targetSpeechiness:float=None, 
        minTempo:int=None, maxTempo:int=None, targetTempo:int=None, 
        minTimeSignature:int=None, maxTimeSignature:int=None, targetTimeSignature:int=None, 
        minValence:float=None, maxValence:float=None, targetValence:float=None
        ) -> TrackRecommendations:
        """
        <span class="deprecated">
            DEPRECATED - api endpoint no longer supported by Spotify as of 2024/11/27 for unauthorized Spotify Developer Applications.
            The api endpoint IS still supported by Spotify for authorized Spotify Developer Applications.
            More information about the deprecated functionality can be found on the 
            <a href="https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api" target="_blank">Spotify Developer Forum Blog</a>
            page.
        </span>       
        
        Get track recommendations for specified criteria.
        
        Use the `GetTrackAudioFeatures` method to get an idea of what to specify for some of the
        minX / maxX / and targetX argument values.
        
        Args:
            limit (int):
                The maximum number of items to return in a page of items.  
                Default: 20, Range: 1 to 50.  
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
            seedArtists (str):
                A comma separated list of Spotify IDs for seed artists.  
                Up to 5 seed values may be provided in any combination of seedArtists, seedTracks and seedGenres.  
                Note: only required if seedGenres and seedTracks are not set.  
                Example: `4NHQUGzhtTLFvgF5SZesLK`
            seedGenres (str):
                A comma separated list of any genres in the set of available genre seeds.  
                Up to 5 seed values may be provided in any combination of seedArtists, seedTracks and seedGenres.  
                Note: only required if seedArtists and seedTracks are not set.  
                Example: `classical,country`
            seedTracks (str):
                A comma separated list of Spotify IDs for a seed track.  
                Up to 5 seed values may be provided in any combination of seedArtists, seedTracks and seedGenres.  
                Note: only required if seedArtists and seedGenres are not set.  
                Example: `0c6xIDDpzE81m2q797ordA`  
            minAcousticness (float):
                Restrict results to only those tracks whose acousticness level is greater than the specified value.  
                Range: `0` - `1`
            maxAcousticness (float):
                Restrict results to only those tracks whose acousticness level is less than the specified value.  
                Range: `0` - `1`  
            targetAcousticness (float):
                Restrict results to only those tracks whose acousticness level is equal to the specified value.  
                Range: `0` - `1`  
            minDanceability (float):
                Restrict results to only those tracks whose danceability level is greater than the specified value.  
                Range: `0` - `1`  
            maxDanceability (float):
                Restrict results to only those tracks whose danceability level is less than the specified value.  
                Range: `0` - `1`  
            targetDanceability (float):
                Restrict results to only those tracks whose acousticness is equal to the specified value.  
                Range: `0` - `1`  
            minDurationMS (int):
                Restrict results to only those tracks whose duration is greater than the specified value in milliseconds.  
            maxDurationMS (int):
                Restrict results to only those tracks whose duration is less than the specified value in milliseconds.  
            targetDurationMS (int):
                Restrict results to only those tracks whose duration is equal to the specified value in milliseconds.  
            minEnergy (float):
                Restrict results to only those tracks whose energy level is greater than the specified value.  
                Range: `0` - `1`  
            maxEnergy (float):
                Restrict results to only those tracks whose energy level is less than the specified value.  
                Range: `0` - `1`  
            targetEnergy (float):
                Restrict results to only those tracks whose energy level is equal to the specified value.  
                Range: `0` - `1`  
            minInstrumentalness (float):
                Restrict results to only those tracks whose instrumentalness level is greater than the specified value.  
                Range: `0` - `1`  
            maxInstrumentalness (float):
                Restrict results to only those tracks whose instrumentalness level is less than the specified value.  
                Range: `0` - `1`  
            targetInstrumentalness (float):
                Restrict results to only those tracks whose instrumentalness level is equal to the specified value.  
                Range: `0` - `1`  
            minKey (int):
                Restrict results to only those tracks whose key level is greater than the specified value.  
                Range: `0` - `11`  
            maxKey (int):
                Restrict results to only those tracks whose key level is less than the specified value.  
                Range: `0` - `11`  
            targetKey (int):
                Restrict results to only those tracks whose key level is equal to the specified value.  
                Range: `0` - `11`
            minLiveness (float):
                Restrict results to only those tracks whose liveness level is greater than the specified value.  
                Range: `0` - `1`  
            maxLiveness (float):
                Restrict results to only those tracks whose liveness level is less than the specified value.  
                Range: `0` - `1`  
            targetLiveness (float):
                Restrict results to only those tracks whose liveness level is equal to the specified value.  
                Range: `0` - `1`  
            minLoudness (float):
                Restrict results to only those tracks whose loudness level is greater than the specified value.  
            maxLoudness (float):
                Restrict results to only those tracks whose loudness level is less than the specified value.  
            targetLoudness (float):
                Restrict results to only those tracks whose loudness level is equal to the specified value.  
            minMode (float):
                Restrict results to only those tracks whose mode level is greater than the specified value.  
                Range: `0` - `1`  
            maxMode (float):
                Restrict results to only those tracks whose mode level is less than the specified value.  
                Range: `0` - `1`  
            targetMode (float):
                Restrict results to only those tracks whose mode level is equal to the specified value.  
                Range: `0` - `1`  
            minPopularity (int):
                Restrict results to only those tracks whose popularity level is greater than the specified value.  
                Range: `0` - `100`  
            maxPopularity (int):
                Restrict results to only those tracks whose popularity level is less than the specified value.  
                Range: `0` - `100`  
            targetPopularity (int):
                Restrict results to only those tracks whose popularity level is equal to the specified value.  
                Range: `0` - `100`  
            minSpeechiness (float):
                Restrict results to only those tracks whose speechiness level is greater than the specified value.  
                Range: `0` - `1`  
            maxSpeechiness (float):
                Restrict results to only those tracks whose speechiness level is less than the specified value.  
                Range: `0` - `1`  
            targetSpeechiness (float):
                Restrict results to only those tracks whose speechiness level is equal to the specified value.  
                Range: `0` - `1`  
            minTempo (int):
                Restrict results to only those tracks with a tempo greater than the specified number of beats per minute.  
            maxTempo (int):
                Restrict results to only those tracks with a tempo less than the specified number of beats per minute.  
            targetTempo (int):
                Restrict results to only those tracks with a tempo equal to the specified number of beats per minute.  
            minTimeSignature (int):
                Restrict results to only those tracks whose time signature is greater than the specified value.  
                Maximum value: 11
            maxTimeSignature (int):
                Restrict results to only those tracks whose time signature is less than the specified value.  
            targetTimeSignature (int):
                Restrict results to only those tracks whose time signature is equal to the specified value.  
            minValence (float):
                Restrict results to only those tracks whose valence level is greater than the specified value.  
                Range: `0` - `1`  
            maxValence (float):
                Restrict results to only those tracks whose valence level is less than the specified value.  
                Range: `0` - `1`  
            targetValence (float):
                Restrict results to only those tracks whose valence level is equal to the specified value.  
                Range: `0` - `1`  
            
        Returns:
            A `TrackRecommendations` object that contain the recommendations.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        Recommendations are generated based on the available information for a given seed entity and matched 
        against similar artists and tracks. If there is sufficient information about the provided seeds, a 
        list of tracks will be returned together with pool size details.  

        For artists and tracks that are very new or obscure there might not be enough data to generate a list of tracks.

        Important policy note:  
        - Spotify content may not be used to train machine learning or AI model.
        
        <details>
          <summary>Sample Code - Wind Down</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetTrackRecommendations_WindDown.py
        ```
        </details>
        
        <details>
          <summary>Sample Code - I Wanna Rock!</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetTrackRecommendations_IWannaRock.py
        ```
        </details>
        """
        apiMethodName:str = 'GetTrackRecommendations'
        apiMethodParms:SIMethodParmListContext = None
        result:list[AudioFeatures] = []
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("market", market)
            apiMethodParms.AppendKeyValue("seedArtists", seedArtists)
            apiMethodParms.AppendKeyValue("seedGenres", seedGenres)
            apiMethodParms.AppendKeyValue("seedTracks", seedTracks)
            apiMethodParms.AppendKeyValue("minAcousticness", minAcousticness)
            apiMethodParms.AppendKeyValue("maxAcousticness", maxAcousticness)
            apiMethodParms.AppendKeyValue("targetAcousticness", targetAcousticness)
            apiMethodParms.AppendKeyValue("minDanceability", minDanceability)
            apiMethodParms.AppendKeyValue("maxDanceability", maxDanceability)
            apiMethodParms.AppendKeyValue("targetDanceability", targetDanceability)
            apiMethodParms.AppendKeyValue("minDurationMS", minDurationMS)
            apiMethodParms.AppendKeyValue("maxDurationMS", maxDurationMS)
            apiMethodParms.AppendKeyValue("targetDurationMS", targetDurationMS)
            apiMethodParms.AppendKeyValue("minEnergy", minEnergy)
            apiMethodParms.AppendKeyValue("maxEnergy", maxEnergy)
            apiMethodParms.AppendKeyValue("targetEnergy", targetEnergy)
            apiMethodParms.AppendKeyValue("minInstrumentalness", minInstrumentalness)
            apiMethodParms.AppendKeyValue("maxInstrumentalness", maxInstrumentalness)
            apiMethodParms.AppendKeyValue("targetInstrumentalness", targetInstrumentalness)
            apiMethodParms.AppendKeyValue("minKey", minKey)
            apiMethodParms.AppendKeyValue("maxKey", maxKey)
            apiMethodParms.AppendKeyValue("targetKey", targetKey)
            apiMethodParms.AppendKeyValue("minLiveness", minLiveness)
            apiMethodParms.AppendKeyValue("maxLiveness", maxLiveness)
            apiMethodParms.AppendKeyValue("targetLiveness", targetLiveness)
            apiMethodParms.AppendKeyValue("minLoudness", minLoudness)
            apiMethodParms.AppendKeyValue("maxLoudness", maxLoudness)
            apiMethodParms.AppendKeyValue("targetLoudness", targetLoudness)
            apiMethodParms.AppendKeyValue("minMode", minMode)
            apiMethodParms.AppendKeyValue("maxMode", maxMode)
            apiMethodParms.AppendKeyValue("targetMode", targetMode)
            apiMethodParms.AppendKeyValue("minPopularity", minPopularity)
            apiMethodParms.AppendKeyValue("maxPopularity", maxPopularity)
            apiMethodParms.AppendKeyValue("targetPopularity", targetPopularity)
            apiMethodParms.AppendKeyValue("minSpeechiness", minSpeechiness)
            apiMethodParms.AppendKeyValue("maxSpeechiness", maxSpeechiness)
            apiMethodParms.AppendKeyValue("targetSpeechiness", targetSpeechiness)
            apiMethodParms.AppendKeyValue("minTempo", minTempo)
            apiMethodParms.AppendKeyValue("maxTempo", maxTempo)
            apiMethodParms.AppendKeyValue("targetTempo", targetTempo)
            apiMethodParms.AppendKeyValue("minTimeSignature", minTimeSignature)
            apiMethodParms.AppendKeyValue("maxTimeSignature", maxTimeSignature)
            apiMethodParms.AppendKeyValue("targetTimeSignature", targetTimeSignature)
            apiMethodParms.AppendKeyValue("minValence", minValence)
            apiMethodParms.AppendKeyValue("maxValence", maxValence)
            apiMethodParms.AppendKeyValue("targetValence", targetValence)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get track recommendations for specified criteria", apiMethodParms)
                
            # are spotify web player credentials configured? if so, then we will use them to create
            # an elevated authorization access token for the Spotify Web API endpoint call.
            accessTokenHeaderValue:str = self._GetSpotifyWebPlayerTokenHeaderValue()

            # if spotify web player credentials not configured then we are done; the Spotify Web API
            # endpoint is no longer supported by unauthorized Spotify Developer Applications as of 2024/11/27.
            if (accessTokenHeaderValue is None):
                raise SpotifyApiError(SAAppMessages.MSG_SPOTIFY_DEPRECATED_ENDPOINT % apiMethodName)

            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'limit': limit
            }
            if market is not None:
                urlParms['market'] = market

            if seedArtists is not None:
                urlParms['seed_artists'] = seedArtists
            if seedGenres is not None:
                urlParms['seed_genres'] = seedGenres
            if seedTracks is not None:
                urlParms['seed_tracks'] = seedTracks
                
            if minAcousticness is not None:
                urlParms['min_acousticness'] = minAcousticness
            if maxAcousticness is not None:
                urlParms['max_acousticness'] = maxAcousticness
            if targetAcousticness is not None:
                urlParms['target_acousticness'] = targetAcousticness
                
            if minDanceability is not None:
                urlParms['min_danceability'] = minDanceability
            if maxDanceability is not None:
                urlParms['max_danceability'] = maxDanceability
            if targetDanceability is not None:
                urlParms['target_danceability'] = targetDanceability
                
            if minDurationMS is not None:
                urlParms['min_duration_ms'] = minDurationMS
            if maxDurationMS is not None:
                urlParms['max_duration_ms'] = maxDurationMS
            if targetDurationMS is not None:
                urlParms['target_duration_ms'] = targetDurationMS
                
            if minEnergy is not None:
                urlParms['min_energy'] = minEnergy
            if maxEnergy is not None:
                urlParms['max_energy'] = maxEnergy
            if targetEnergy is not None:
                urlParms['target_energy'] = targetEnergy

            if minInstrumentalness is not None:
                urlParms['min_instrumentalness'] = minInstrumentalness
            if maxInstrumentalness is not None:
                urlParms['max_instrumentalness'] = maxInstrumentalness
            if targetInstrumentalness is not None:
                urlParms['target_instrumentalness'] = targetInstrumentalness
                
            if minKey is not None:
                urlParms['min_key'] = minKey
            if maxKey is not None:
                urlParms['max_key'] = maxKey
            if targetKey is not None:
                urlParms['target_key'] = targetKey
                
            if minLiveness is not None:
                urlParms['min_liveness'] = minLiveness
            if maxLiveness is not None:
                urlParms['max_liveness'] = maxLiveness
            if targetLiveness is not None:
                urlParms['target_liveness'] = targetLiveness
                
            if minLoudness is not None:
                urlParms['min_loudness'] = minLoudness
            if maxLoudness is not None:
                urlParms['max_loudness'] = maxLoudness
            if targetLoudness is not None:
                urlParms['target_loudness'] = targetLoudness
                
            if minMode is not None:
                urlParms['min_mode'] = minMode
            if maxMode is not None:
                urlParms['max_mode'] = maxMode
            if targetMode is not None:
                urlParms['target_mode'] = targetMode
                
            if minPopularity is not None:
                urlParms['min_popularity'] = minPopularity
            if maxPopularity is not None:
                urlParms['max_popularity'] = maxPopularity
            if targetPopularity is not None:
                urlParms['target_popularity'] = targetPopularity
                
            if minSpeechiness is not None:
                urlParms['min_speechiness'] = minSpeechiness
            if maxSpeechiness is not None:
                urlParms['max_speechiness'] = maxSpeechiness
            if targetSpeechiness is not None:
                urlParms['target_speechiness'] = targetSpeechiness
                
            if minTempo is not None:
                urlParms['min_tempo'] = minTempo
            if maxTempo is not None:
                urlParms['max_tempo'] = maxTempo
            if targetTempo is not None:
                urlParms['target_tempo'] = targetTempo
                
            if minTimeSignature is not None:
                urlParms['min_time_signature'] = minTimeSignature
            if maxTimeSignature is not None:
                urlParms['max_time_signature'] = maxTimeSignature
            if targetTimeSignature is not None:
                urlParms['target_time_signature'] = targetTimeSignature
                
            if minValence is not None:
                urlParms['min_valence'] = minValence
            if maxValence is not None:
                urlParms['max_valence'] = maxValence
            if targetValence is not None:
                urlParms['target_valence'] = targetValence
                
            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/recommendations')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = accessTokenHeaderValue or self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('GET', msg)

            # process results.
            result = TrackRecommendations(root=msg.ResponseData)
        
            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    @staticmethod
    def GetTypeFromUri(
        uri:str, 
        ) -> str:
        """
        Get the type portion from a Spotify uri value.
        
        Args:
            uri (str):  
                The Spotify URI value.
                Example: `spotify:track:5v5ETK9WFXAnGQ3MRubKuE`
                
        Returns:
            A string containing the type value (e.g. `track`).
            
        No exceptions are raised with this method.
        """
        result:str = None
        
        try:
            
            # validations.
            if uri is None or len(uri.strip()) == 0:
                return result

            # get type from uri value.
            colonCnt:int = uri.count(':')
            if colonCnt == 2:
                idxStart:int = uri.find(':')
                if idxStart > -1:
                    if (idxStart + 1) > len(uri):
                        return result
                    idxEnd:int = uri.find(':', idxStart + 1)
                    if idxEnd > -1:
                        result = uri[idxStart+1:idxEnd]

            return result

        except Exception as ex:
            
            _logsi.LogWarning("GetTypeFromUri failed: %s" % str(ex))
            return None


    def GetUsersCurrentProfile(
        self,
        refresh:bool=True
        ) -> UserProfileCurrentUser:
        """
        Get detailed profile information about the current user (including the current user's username).
        
        This method requires the `user-read-private` and `user-read-email` scope.
        
        Args:
            refresh (bool):
                True (default) to return real-time information from the spotify web api and
                update the cache; otherwise, False to just return the cached value.
        
        Returns:
            A `UserProfile` object that contains the user details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        The `ConfigurationCache` is updated with the results of this method.  Use the
        `refresh` argument (with False value) to retrieve the cached value and avoid
        the spotify web api request.  This results in better performance.
                        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetUsersCurrentProfile.py
        ```
        </details>
        """
        apiMethodName:str = 'GetUsersCurrentProfile'
        apiMethodParms:SIMethodParmListContext = None
        result:Track = UserProfile
        cacheDesc:str = CACHE_SOURCE_CURRENT
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get profile information about the current user", apiMethodParms)
                
            # validations.
            if (refresh is None):
                refresh = True

            # can we use the cached value?
            if (not refresh) and (apiMethodName in self._ConfigurationCache):
                
                result = self._ConfigurationCache[apiMethodName]
                cacheDesc = CACHE_SOURCE_CACHED
                
            else:
                
                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                self.MakeRequest('GET', msg)

                # process results.
                result = UserProfile(root=msg.ResponseData)

                # update cache.
                self._ConfigurationCache[apiMethodName] = result

            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE_CACHED % (apiMethodName, type(result).__name__, cacheDesc), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetUsersPublicProfile(
        self,
        userId:str,
        ) -> UserProfileSimplified:
        """
        Get public profile information about a Spotify user.
       
        Args:
            userId (str):
                The user's Spotify user ID.
                Example: `smedjan`
                
        Returns:
            A `UserProfileSimplified` object that contains the user's public details.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetUsersPublicProfile.py
        ```
        </details>
        """
        apiMethodName:str = 'GetUsersPublicProfile'
        apiMethodParms:SIMethodParmListContext = None
        result:UserProfileSimplified = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("userId", userId)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get public profile information about a Spotify user", apiMethodParms)
                
            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/users/{user_id}'.format(user_id=userId))
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            self.MakeRequest('GET', msg)

            # process results.
            result = UserProfileSimplified(root=msg.ResponseData)

            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT_TYPE % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetUsersTopArtists(
        self, 
        timeRange:str='medium_term',
        limit:int=20, 
        offset:int=0,
        limitTotal:int=None,
        sortResult:bool=True,
        ) -> ArtistPage:
        """
        Get the current user's top artists based on calculated affinity.
        
        Args:
            timeRange (str):
                Over what time frame the affinities are computed.  
                Valid values:  
                - long_term (calculated from several years of data and including all new data as it becomes available).  
                - medium_term (approximately last 6 months).  
                - short_term (approximately last 4 weeks).  
                Default: `medium_term`  
                Example: `long_term`
            limit (int):
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            offset (int):
                The page index offset of the first item to return.  
                Use with limit to get the next set of items.  
                Default: 0 (the first item), Range: 0 to 1000
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
            sortResult (bool):
                True to sort the items by name; otherwise, False to leave the items in the same order they 
                were returned in by the Spotify Web API.  
                Default: True
                
        Returns:
            An `ArtistPage` object of matching results.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetUsersTopArtists.py
        ```
        </details>
        <details>
          <summary>Sample Code - Auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetUsersTopArtists_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'GetUsersTopArtists'
        apiMethodParms:SIMethodParmListContext = None
        result:ArtistPage = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("timeRange", timeRange)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("offset", offset)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            apiMethodParms.AppendKeyValue("sortResult", sortResult)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get the current user's top artists", apiMethodParms)
                
            # validations.
            if timeRange is None:
                timeRange = 'medium_term'
            if limit is None: 
                limit = 20
            if offset is None: 
                offset = 0
            if not isinstance(limitTotal, int):
                limitTotal = 0
            if sortResult is None: 
                sortResult = True
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = ArtistPage()

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'time_range': timeRange,
                'limit': limit,
                'offset': offset,
            }

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/top/artists')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                pageObj = ArtistPage(root=msg.ResponseData)

                # trace.
                _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:Artist
                    for item in pageObj.Items:
                        result.Items.append(item)
                        result.Limit = result.ItemsCount
                        if result.ItemsCount >= limitTotal:
                            break
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithOffset(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break

            # update result object with final paging details.
            result.Total = pageObj.Total
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # sort result items.
            if (len(result.Items) > 0):
                if (sortResult is True):
                    result.Items.sort(key=lambda x: (x.Name or "").lower(), reverse=False)
        
            # trace.
            _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE + result.PagingInfo) % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetUsersTopTracks(
        self, 
        timeRange:str='medium_term',
        limit:int=20, 
        offset:int=0,
        limitTotal:int=None,
        sortResult:bool=True,
        ) -> TrackPage:
        """
        Get the current user's top tracks based on calculated affinity.
        
        Args:
            timeRange (str):
                Over what time frame the affinities are computed.  
                Valid values:  
                - long_term (calculated from several years of data and including all new data as it becomes available).  
                - medium_term (approximately last 6 months).  
                - short_term (approximately last 4 weeks).  
                Default: `medium_term`  
                Example: `long_term`
            limit (int):
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            offset (int):
                The page index offset of the first item to return.  
                Use with limit to get the next set of items.  
                Default: 0 (the first item).  
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
            sortResult (bool):
                True to sort the items by name; otherwise, False to leave the items in the same order they 
                were returned in by the Spotify Web API.  
                Default: True
                
        Returns:
            An `TrackPage` object of matching results.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetUsersTopTracks.py
        ```
        </details>
        <details>
          <summary>Sample Code - Auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/GetUsersTopTracks_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'GetUsersTopTracks'
        apiMethodParms:SIMethodParmListContext = None
        result:TrackPage = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("timeRange", timeRange)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("offset", offset)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            apiMethodParms.AppendKeyValue("sortResult", sortResult)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get the current user's top tracks", apiMethodParms)
                
            # validations.
            if timeRange is None:
                timeRange = 'medium_term'
            if limit is None: 
                limit = 20
            if offset is None: 
                offset = 0
            if not isinstance(limitTotal, int):
                limitTotal = 0
            if sortResult is None: 
                sortResult = True
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = TrackPage()

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'time_range': timeRange,
                'limit': limit,
                'offset': offset,
            }

            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/top/tracks')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                pageObj = TrackPage(root=msg.ResponseData)

                # trace.
                _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:Track
                    for item in pageObj.Items:
                        result.Items.append(item)
                        result.Limit = result.ItemsCount
                        if result.ItemsCount >= limitTotal:
                            break
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithOffset(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break

            # update result object with final paging details.
            result.Total = pageObj.Total
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # sort result items.
            if (len(result.Items) > 0):
                if (sortResult is True):
                    result.Items.sort(key=lambda x: (x.Name or "").lower(), reverse=False)
        
            # trace.
            _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE + result.PagingInfo) % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def IsChapterEpisode(
        self, 
        episodeId:str=None, 
        market:str=None,
        ) -> bool:
        """
        Returns true if the specified episode id is an audiobook chapter; otherwise, false.
        
        Args:
            episodeId (str):  
                The Spotify ID to check.
                Example: `74aydHJKgYz3AIq3jjBSv1`
                If null, the currently playing uri id value is used; a Spotify Free or Premium account 
                is required to correctly read the currently playing context.
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
                
        Returns:
            True if the specified id is an audiobook chapter; otherwise, false.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/IsChapterEpisode.py
        ```
          <summary>Sample Code - NowPlaying</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/IsChapterEpisode_NowPlaying.py
        ```
        </details>
        """
        apiMethodName:str = 'IsChapterEpisode'
        apiMethodParms:SIMethodParmListContext = None
        result:bool = False
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("episodeId", episodeId)
            apiMethodParms.AppendKeyValue("market", market)
            _logsi.LogMethodParmList(SILevel.Verbose, "Check if episode id is an audiobook chapter or not", apiMethodParms)
                
            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market)

            # if id not specified, then return currently playing id value.
            # this will issue a GetChapter call to retrieve the actual audiobook id.
            # the `GetPlayerNowPlayingAudiobookUri` method will fail if it's not a chapter id.
            if (episodeId is None) or (len(episodeId.strip()) == 0):
                
                uri = self.GetPlayerNowPlayingAudiobookUri(market, True)
                result = (uri is not None)
                
            else:
                
                # if id was supplied, then call the `GetChapter` method to retrieve chapter information.
                # the `GetChapter` method will fail if it's not a chapter id.
                chapter:Chapter = self.GetChapter(episodeId, market, True)
                result = (chapter.Id is not None)
                
            return result

        except Exception as ex:
            
            # at this point we can safely assume it's NOT an audiobook chapter.
            result = False
            return result
               
        finally:
        
            # trace.
            _logsi.LogValue(SILevel.Verbose, TRACE_METHOD_RESULT % (apiMethodName), result)

            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    @staticmethod
    def IsDeviceId(value:str) -> bool:
        """
        Get the assumed device value format.
               
        Args:
            value (str):
                The id or name of a Spotify Connect device.
                Example id: `0d1841b0976bae2a3a310dd74c0f3df354899bc8`  
                Example id: `48b677ca-ef9b-516f-b702-93bf2e8c67ba`  
                Example name: `Web Player (Chrome)`  

        Returns:
            True if the specified value is a device id format; 
            otherwise, False to indicate it is a device name format.
            
        No exceptions are raised with this method.
        """
        result:bool = False
        try:
            # if it is a hex string (or uuid format), then it is assumed to be a device id.
            if value is not None:
                value = str(value)
                value = value.replace('-','')
                intValue:int = int(str(value), 16)
                result = True
        except Exception as ex:
            # otherwise, assume it's a device name.
            result = False
            
        return result


    @staticmethod
    def IsSpotifyUri(
        uri:str, 
        ) -> bool:
        """
        Determines if the specified value is a Spotify URI or not.
        
        Args:
            uri (str):  
                The possible Spotify URI value.
                Example: `spotify:track:5v5ETK9WFXAnGQ3MRubKuE`
                
        Returns:
            True if the value is a Spotify URI value; otherwise, false.
            
        No exceptions are raised with this method.

        Simple tests are used to determine if the value is a Spotify URI.
        - 2 colons must be present.
        - value must start with "spotify:".
        """
        try:
            
            # validations.
            if uri is None or len(uri.strip()) == 0:
                return False

            # convert case for comparison.
            uri = uri.lower()

            # simple test for Spotify URI format.
            if (uri.count(':') != 2):
                return False
            if (not uri.startswith("spotify:")):
                return False

            # if it passed the test, then it must be true.
            return True

        except Exception:
            
            return False


    def PlayerMediaPause(
        self, 
        deviceId:str=None,
        delay:float=0.50
        ) -> None:
        """
        Pause media play for the specified Spotify Connect device.
        
        This method requires the `user-modify-playback-state` scope.

        Args:
            deviceId (str | SpotifyConnectDevice) | None):
                The target player device identifier.
                This could be an id, name, a default device indicator (e.g. "*"), a 
                SpotifyConnectDevice object, or null to utilize the active player device.
                A device is considered resolved if a SpotifyConnectDevice object is passed
                for this argument.  An exception will be raised if the argument value could 
                not be resolved or activated.
                Examples are `0d1841b0976bae2a3a310dd74c0f3df354899bc8`, `Office`, `*`, None.  
            delay (float):
                Time delay (in seconds) to wait AFTER issuing the command to the player.  
                This delay will give the spotify web api time to process the change before 
                another command is issued.  
                Default is 0.50; value range is 0 - 10.
                                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        This API only works for users who have Spotify Premium. 
        
        The order of execution is not guaranteed when you use this API with other Player API endpoints.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/PlayerMediaPause.py
        ```
        </details>
        """
        apiMethodName:str = 'PlayerMediaPause'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("deviceId", deviceId)
            apiMethodParms.AppendKeyValue("delay", delay)
            _logsi.LogMethodParmList(SILevel.Verbose, "Spotify Connect device pause playback", apiMethodParms)
                
            # validations.
            delay = validateDelay(delay, 0.50, 10)

            # resolve the device object from the device id.
            scDevice:SpotifyConnectDevice = self._ResolveDeviceObject(deviceId, False)

            # are spotify web player credentials configured? if so, then we will use them to create
            # an elevated authorization access token for the Spotify Web API endpoint call.
            accessTokenHeaderValue:str = self._GetSpotifyWebPlayerTokenHeaderValue(scDevice)

            # is this an active Sonos device?
            # Sonos device can still be active, even if there is no active device in Spotify playstate.
            if (scDevice is not None) and (scDevice.IsSonos) and (accessTokenHeaderValue is None):

                _logsi.LogVerbose("Issuing command to Sonos device %s: PAUSE" % (scDevice.Title))
                sonosPlayer:SoCo = self.SpotifyConnectDirectory.GetSonosPlayer(scDevice)
                sonosPlayer.pause()

            else:

                # was the deviceId resolved? 
                # if not, then raise an exception as the Spotify Web API request will fail anyway.
                self._CheckForDeviceNotFound(scDevice, deviceId)

                # build spotify web api request parameters.
                urlParms:dict = {}
                if (scDevice is not None):
                    urlParms['device_id'] = (scDevice.DeviceIdActivated or scDevice.Id)

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/player/pause')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = accessTokenHeaderValue or self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('PUT', msg)
            
            # give spotify web api time to process the change.
            if delay > 0:
                _logsi.LogVerbose(TRACE_MSG_DELAY_DEVICE % delay)
                time.sleep(delay)

            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def PlayerMediaPlayContext(
        self, 
        contextUri:str,
        offsetUri:str=None,
        offsetPosition:int=None,
        positionMS:int=0,
        deviceId:str=None,
        delay:float=0.50,
        resolveDeviceId:bool=True,
        shuffle:bool=None,
        ) -> None:
        """
        Start playing one or more tracks of the specified context on a Spotify Connect device.
        
        This method requires the `user-modify-playback-state` scope.

        Args:
            contextUri (str):
                Spotify URI (or URL) of the context to play.  
                Valid contexts are albums, artists & playlists.  
                Example: `spotify:album:6vc9OTcyd3hyzabCmsdnwE`.   
                Example: `https://open.spotify.com/playlist/4ufyQwaLq1MR49KvGRCNAo`.   
            offsetUri (str):
                Indicates from what Uri in the context playback should start.  
                Only available when contextUri corresponds to an artist, album or playlist.  
                The offsetPosition argument will be used if this value is null.  
                This value is ignored if the `shuffle` argument is True.  
                Default is null.  
                Example: `spotify:track:1301WleyT98MSxVHPZCA6M` start playing at the specified track Uri.  
            offsetPosition (int):
                Indicates from what position in the context playback should start.  
                The value is zero-based, and can't be negative.  
                Only available when contextUri corresponds to an album or playlist.  
                This value is ignored if the `shuffle` argument is True.  
                Default is `0`.  
                Example: `3`  start playing at track number 4.
            positionMS (int):
                The position in milliseconds to seek to; must be a positive number.  
                Passing in a position that is greater than the length of the track will cause the 
                player to start playing the next track.  
                Default is `0`.  
                Example: `25000`  
            deviceId (str | SpotifyConnectDevice) | None):
                The target player device identifier.
                This could be an id, name, a default device indicator (e.g. "*"), a 
                SpotifyConnectDevice object, or null to utilize the active player device.
                A device is considered resolved if a SpotifyConnectDevice object is passed
                for this argument.  An exception will be raised if the argument value could 
                not be resolved or activated.
                Examples are `0d1841b0976bae2a3a310dd74c0f3df354899bc8`, `Office`, `*`, None.  
            delay (float):
                Time delay (in seconds) to wait AFTER issuing the command to the player.  
                This delay will give the spotify web api time to process the change before 
                another command is issued.  
                Default is 0.50; value range is 0 - 10.
            resolveDeviceId (bool):
                DEPRECATED - no longer used, but left here to maintain compatibility.
            shuffle (bool):
                True to enable player shuffle mode; False to disable player shuffle mode; 
                None to use current player shuffle mode.  
                Default is None.  
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        This API only works for users who have Spotify Premium. 
        
        The order of execution is not guaranteed when you use this API with other Player API endpoints.

        For Sonos devices that have shuffle enabled, the first item of the first context uri will always 
        be played first; subsequent items will be played in shuffled order.  
        This is due to the way the Sonos local queue is used to play the context uri items.

        A `Player command failed: Restriction violated` error will occur if the `offset_position` value exceeds 
        the number of items in the context.  For example, if there are 500 entries in the playlist context and 
        you specify 501 for the `offset_position` value.

        A `Can't have offset for context type: ARTIST` error will occur if the `offsetPosition` or `offsetUri`
        argument is specified for an artist context.

        You can also use the `spotify:user:YOUR_LOGIN_ID:collection` syntax to play track favorites; just replace 
        the `YOUR_LOGIN_ID` with your Spotify login id value (e.g. `smedjan`, `3758dfdsfjk435hjk6k79lm0n3c4`, etc).
        
        <details>
          <summary>Sample Code - Play Album</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/PlayerMediaPlayContext_Album.py
        ```
        </details>
        
        <details>
          <summary>Sample Code - Play Artist</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/PlayerMediaPlayContext_Artist.py
        ```
        </details>
        
        <details>
          <summary>Sample Code - Play Playlist</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/PlayerMediaPlayContext_Playlist.py
        ```
        </details>
        """
        apiMethodName:str = 'PlayerMediaPlayContext'
        apiMethodParms:SIMethodParmListContext = None
        scDevice:SpotifyConnectDevice = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("contextUri", contextUri)
            apiMethodParms.AppendKeyValue("offsetUri", offsetUri)
            apiMethodParms.AppendKeyValue("offsetPosition", offsetPosition)
            apiMethodParms.AppendKeyValue("positionMS", positionMS)
            apiMethodParms.AppendKeyValue("deviceId", deviceId)
            apiMethodParms.AppendKeyValue("delay", delay)
            apiMethodParms.AppendKeyValue("resolveDeviceId (DEPRECATED)", resolveDeviceId)
            apiMethodParms.AppendKeyValue("shuffle", shuffle)
            _logsi.LogMethodParmList(SILevel.Verbose, "Spotify Connect device play context", apiMethodParms)
                
            # validations.
            delay = validateDelay(delay, 0.50, 10)
            if (positionMS is None) or (positionMS < 0):
                positionMS = 0
            if (offsetPosition is None) or (offsetPosition < 0):
                offsetPosition = 0

            # if shuffle specified, then we will reset the offset argument values
            # since we are playing things in random order anyway.
            if (shuffle):
                _logsi.LogVerbose("Shuffle=True was specified; ignoring offsetPosition and offsetUri values")
                offsetPosition = 0
                offsetUri = None

            # resolve the device object from the device idl activate if it's dormant.
            scDevice = self._ResolveDeviceObject(deviceId, True)

            # are spotify web player credentials configured? if so, then we will use them to create
            # an elevated authorization access token for the Spotify Web API endpoint call.
            accessTokenHeaderValue:str = self._GetSpotifyWebPlayerTokenHeaderValue(scDevice)
            
            # is this an active Sonos device?
            # Sonos device can still be active, even if there is no active device in Spotify playstate.
            # if spotify web player credentials are NOT configured, then we will transfer control to the
            # Sonos device local queue for playback; otherwise, we will just call the Spotify Web API
            # endpoint below with the elevated authorization access token to start playback under the
            # control of Spotify Connect. 
            if (scDevice is not None) and (scDevice.IsSonos) and (accessTokenHeaderValue is None):

                # trace.
                _logsi.LogVerbose("Context will be played on Sonos local queue for device: %s" % (scDevice.Title))

                # set desired shuffle mode (if specified).
                if (shuffle is not None):

                    self.PlayerSetShuffleMode(shuffle, scDevice, delay)

                    # give Sonos Controller time to process the change.
                    if delay > 0:
                        _logsi.LogVerbose(TRACE_MSG_DELAY_DEVICE_SONOS % delay)
                        time.sleep(delay)

                # Sonos cannot handle playing an artist context!
                # if this is an artist context, then we will get a list of the artist's albums
                # and add them to the queue.    
                if (contextUri.find(':artist:') > -1):
                    artistId:str = contextUri.replace('spotify:artist:','')
                    #includeGroups:str = 'album,single,appears_on,compilation'
                    includeGroups:str = 'album'
                    _logsi.LogVerbose("Getting ALL albums for artist id: %s" % (artistId))
                    pageObj:AlbumPageSimplified = self.GetArtistAlbums(artistId, includeGroups, limitTotal=75)
                    contextUri:list = []
                    albumSimplified:AlbumSimplified
                    for albumSimplified in pageObj.Items:
                        contextUri.append(albumSimplified.Uri)

                # build a list of all item uri's.
                # remove any leading / trailing spaces in case user put a space between the items.
                arrUris:list[str] = None
                if isinstance(contextUri, list):
                    arrUris = contextUri
                else:
                    arrUris = contextUri.split(',')
                    for idx in range(0, len(arrUris)):
                        arrUris[idx] = arrUris[idx].strip()

                # if shuffle enabled, then randomize the context uri's.
                # note that this randomizes the list of context uri's, and NOT the items
                # contained within each context uri (e.g. playlist items, album tracks, etc).
                if (shuffle):
                    _logsi.LogVerbose("Shuffle enabled; randomizing list of track uri's to play")
                    random.shuffle(arrUris)

                # get the Sonos Controller player instance.
                sonosPlayer:SoCo = self.SpotifyConnectDirectory.GetSonosPlayer(scDevice)

                # clear the Sonos local queue.
                _logsi.LogVerbose("Issuing command to Sonos device \"%s\": CLEAR_QUEUE" % (scDevice.Name))
                sonosPlayer.clear_queue()

                # add all context items to the Sonos local queue.
                sharelink = ShareLinkPlugin(sonosPlayer)
                for idx in range(0, len(arrUris)):

                    # add context to the Sonos local queue.
                    uri = arrUris[idx].strip()
                    _logsi.LogVerbose("Issuing command to Sonos device \"%s\": ADD_SHARE_LINK_TO_QUEUE (uri=%s)" % (scDevice.Name, uri))
                    sharelink.add_share_link_to_queue(uri)

                    # if this is the first item added, then start play of the queue as
                    # it may take awhile to load the rest of the items.
                    if (idx == 0):

                        # start playing the Sonos local queue.
                        _logsi.LogVerbose("Issuing command to Sonos device \"%s\": PLAY_FROM_QUEUE (index=%s)" % (scDevice.Name, offsetPosition))
                        sonosPlayer.play_from_queue(index=offsetPosition)
                
                        # was a track seek position specified?
                        if (positionMS > 0):

                            # seek to the position in the track.
                            sonosPosition:str = mediaPositionHMS_fromSeconds(positionMS / 1000)  # convert from milliseconds to Sonos H:MM:SS format
                            _logsi.LogVerbose("Issuing command to Sonos device \"%s\": SEEK (position=%s)" % (scDevice.Name, sonosPosition))
                            sonosPlayer.seek(position=sonosPosition)
                
                            # give Sonos Controller time to process the change.
                            if delay > 0:
                                _logsi.LogVerbose(TRACE_MSG_DELAY_DEVICE_SONOS % delay)
                                time.sleep(delay)

                # set desired shuffle mode (if specified).
                if (shuffle is not None):

                    # give Sonos Controller time to process the change.
                    if delay > 0:
                        _logsi.LogVerbose(TRACE_MSG_DELAY_DEVICE_SONOS % delay)
                        time.sleep(delay)

                    # set shuffle mode.
                    # note that we already did this before loading the Sonos local queue.
                    # we do it again, as the `add_share_link_to_queue` method seems to cause
                    # the shuffle mode to change in some instances (a SoCo API bug maybe?).
                    self.PlayerSetShuffleMode(shuffle, scDevice, delay)

            else:

                # was the deviceId resolved? 
                # if not, then raise an exception as the Spotify Web API request will fail anyway.
                self._CheckForDeviceNotFound(scDevice, deviceId)

                # trace.
                _logsi.LogVerbose("Context will be played on the Spotify Connect device via Spotify Web API")

                # get current player state.
                playerState:PlayerPlayState = self.GetPlayerPlaybackState(additionalTypes=SpotifyMediaTypes.EPISODE.value)

                # if shuffle was specified, then we will enable / disable player shuffle state PRIOR to starting play.
                # if shuffle is None, then the current shuffle mode is not changed.
                # we only want to set shuffle state if the specified device is in the device list and not restricted, as
                # trying to set shuffle state for restricted devices fail with `Restriction violated` error.
                shuffleSetPriorToPlay:bool = False
                if (shuffle is not None):
                    if (scDevice.IsInDeviceList) and (not scDevice.IsRestricted) and (playerState.Context):
                        if (shuffle != playerState.IsShuffleEnabled):
                            self.PlayerSetShuffleMode(shuffle, scDevice, delay)
                            playerState.IsShuffleEnabled = shuffle    # force shuffles to match
                            shuffleSetPriorToPlay = True

                # is shuffle enabled? and is this a Spotify URI value (e.g. `spotify:type:id`)?
                if (shuffle or playerState.IsShuffleEnabled) and (self.IsSpotifyUri(contextUri)):

                    # get uri parts.
                    uriType:str = self.GetTypeFromUri(contextUri)
                    uriId:str = self.GetIdFromUri(contextUri)
                    uriItems:PageObject = None

                    # wrap this in a try, as errors will be returned if context contains
                    # spotify algorithmic data (e.g. Made For You, Daily Mix n, etc).
                    try:

                        # trace.
                        _logsi.LogVerbose("Shuffle is enabled; getting context item count (50 max)")

                        # get number of items in the context, up to 50 max.
                        # we limit it to 50 to keep it fast, as some context lists are quite large!
                        # note that playlist type is the only type we can limit the amount of data returned.
                        # note that offset cannot be specified for artist context type; a `400 - Bad Request
                        # Can't have offset for context type: ARTIST` error is returned if specified.
                        if (uriType == SpotifyMediaTypes.PLAYLIST.value):
                            uriItems = self.GetPlaylistItems(uriId, limitTotal=50, fields="items(track(name))")
                        elif (uriType == SpotifyMediaTypes.ALBUM.value):
                            uriItems = self.GetAlbumTracks(uriId, limitTotal=50)

                    except Exception as ex:

                        # ignore exceptions.
                        # trace.
                        _logsi.LogVerbose("Could not get first 50 (max) items in context: %s" % str(ex))
                        
                    # set random offset position based on how many context items there are
                    # if context items were obtained (0 to 50 max).
                    if (uriItems is not None) and (uriItems.ItemsCount > 0):
                        offsetPosition = random.randint(0, uriItems.ItemsCount - 1)
                        _logsi.LogVerbose("Shuffle is enabled; setting random offsetPosition to %s" % str(offsetPosition))

                # build spotify web api request parameters.
                reqData:dict = \
                {
                    'context_uri': contextUri,
                }

                if (positionMS is not None) and (positionMS > 0):
                    reqData['position_ms'] = positionMS

                # offset should only be applied if it's not zero / a uri is specified; otherwise,
                # it will not shuffle correctly if shuffle is enabled.
                if offsetUri is not None:
                    reqData['offset'] = { 'uri': offsetUri }
                elif (offsetPosition > 0):
                    reqData['offset'] = { 'position': offsetPosition }

                # formulate url parms; will manually add them since we are adding json body as well.
                urlParms:str = ''
                if (scDevice is not None):
                    urlParms = '?device_id=%s' % (scDevice.DeviceIdActivated or scDevice.Id)

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/player/play{url_parms}'.format(url_parms=urlParms))
                msg.RequestHeaders[self.AuthToken.HeaderKey] = accessTokenHeaderValue or self.AuthToken.HeaderValue
                msg.RequestJson = reqData
                self.MakeRequest('PUT', msg)
            
                # give spotify web api time to process the change.
                if delay > 0:
                    _logsi.LogVerbose(TRACE_MSG_DELAY_DEVICE % delay)
                    time.sleep(delay)

                # set desired shuffle mode (if specified, and not set prior to play).
                # this is necessary for some players, as starting play sometimes resets shuffle mode
                # and it needs to be restored after play starts (e.g. SpotifyConnect AddOn).
                # if shuffle argument not specified, then use initial playstate shuffle value (if one exists).
                if (shuffle is not None) and (not shuffleSetPriorToPlay):
                    self.PlayerSetShuffleMode(shuffle, scDevice, delay)
                elif (shuffle is None) and (not playerState.IsEmpty):
                    self.PlayerSetShuffleMode(playerState.IsShuffleEnabled, scDevice, delay)

            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def PlayerMediaPlayTrackFavorites(
        self, 
        deviceId:str=None,
        shuffle:bool=None,
        delay:float=0.50,
        resolveDeviceId:bool=True,
        limitTotal:int=200,
        ) -> None:
        """
        Get a list of the tracks saved in the current Spotify user's 'Your Library'
        and starts playing them.
        
        Args:
            deviceId (str | SpotifyConnectDevice) | None):
                The target player device identifier.
                This could be an id, name, a default device indicator (e.g. "*"), a 
                SpotifyConnectDevice object, or null to utilize the active player device.
                A device is considered resolved if a SpotifyConnectDevice object is passed
                for this argument.  An exception will be raised if the argument value could 
                not be resolved or activated.
                Examples are `0d1841b0976bae2a3a310dd74c0f3df354899bc8`, `Office`, `*`, None.  
            shuffle (bool):
                True to set player shuffle mode to on; False to set player shuffle mode to off;
                null to leave the shuffle mode as-is.  
                Default is null.
            delay (float):
                Time delay (in seconds) to wait AFTER issuing the command to the player.  
                This delay will give the spotify web api time to process the change before 
                another command is issued.  
                Default is 0.50; value range is 0 - 10.
            resolveDeviceId (bool):
                DEPRECATED - no longer used, but left here to maintain compatibility.
            limitTotal (int):
                The maximum number of items to retrieve from favorites.  
                Default is 200; value range is 1 - 750.  
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        This API only works for users who have Spotify Premium. 
        
        This method simply calls the `GetTrackFavorites` method to retrieve the current users
        favorite tracks, then calls the `PlayerMediaPlayTracks` method to play them.  

        While there is no limitation documented in the Spotify Web API for the `PlayerMediaPlayTracks` 
        method, it has been found that request fail if more than 750 entries are allowed.  I believe
        this is due to a limitation on the request size itself, rather than a limitation on the
        number of tracks allowed for the request.
        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/PlayerMediaPlayTrackFavorites.py
        ```
        </details>
        """
        apiMethodName:str = 'PlayerMediaPlayTrackFavorites'
        apiMethodParms:SIMethodParmListContext = None
        scDevice:SpotifyConnectDevice = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("deviceId", deviceId)
            apiMethodParms.AppendKeyValue("shuffle", shuffle)
            apiMethodParms.AppendKeyValue("delay", delay)
            apiMethodParms.AppendKeyValue("resolveDeviceId (DEPRECATED)", resolveDeviceId)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            _logsi.LogMethodParmList(SILevel.Verbose, "Spotify Connect device play track favorites", apiMethodParms)
                
            # validations.
            delay = validateDelay(delay, 0.50, 10)
            if (limitTotal is None):
                limitTotal = 200
            if (isinstance(limitTotal,int)) and (limitTotal > 750):
                limitTotal = 750

            # get current users favorite tracks.
            tracks:TrackPageSaved = self.GetTrackFavorites(limitTotal=limitTotal, sortResult=False)
            if (tracks.ItemsCount == 0):
                _logsi.LogVerbose("Current user has no favorite tracks; nothing to do")
                return

            # build a list of all item uri's.
            arrUris:list[str] = []
            trackSaved:TrackSaved
            for trackSaved in tracks.Items:
                arrUris.append(trackSaved.Track.Uri)

            # resolve the device object from the device id.
            scDevice = self._ResolveDeviceObject(deviceId, True)

            # play the tracks.
            # indicate device id has already been resolved.
            self.PlayerMediaPlayTracks(arrUris, deviceId=scDevice, shuffle=shuffle, delay=delay)
            
            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def PlayerMediaPlayTracks(
        self, 
        uris:list[str],
        positionMS:int=0,
        deviceId:str=None,
        delay:float=0.50,
        resolveDeviceId:bool=True,
        shuffle:bool=None,
        ) -> None:
        """
        Start playing one or more tracks on the specified Spotify Connect device.
        
        This method requires the `user-modify-playback-state` scope.

        Args:
            uris (str):
                A list of Spotify track URIs to play; can be track or episode URIs.  
                Example: [`spotify:track:6zd8T1PBe9JFHmuVnurdRp` ,`spotify:track:1kWUud3vY5ij5r62zxpTRy`].  
                It can also be specified as a comma-delimited string.  
                Example: `spotify:track:6zd8T1PBe9JFHmuVnurdRp,spotify:track:1kWUud3vY5ij5r62zxpTRy`.  
                A maximum of 50 items can be added in one request.
            positionMS (int):
                The position in milliseconds to seek to; must be a positive number.  
                Passing in a position that is greater than the length of the track will cause the 
                player to start playing the next track.  
                Default is `0`.  
                Example: `25000`  
            deviceId (str | SpotifyConnectDevice) | None):
                The target player device identifier.
                This could be an id, name, a default device indicator (e.g. "*"), a 
                SpotifyConnectDevice object, or null to utilize the active player device.
                A device is considered resolved if a SpotifyConnectDevice object is passed
                for this argument.  An exception will be raised if the argument value could 
                not be resolved or activated.
                Examples are `0d1841b0976bae2a3a310dd74c0f3df354899bc8`, `Office`, `*`, None.  
            delay (float):
                Time delay (in seconds) to wait AFTER issuing the command to the player.  
                This delay will give the spotify web api time to process the change before 
                another command is issued.  
                Default is 0.50; value range is 0 - 10.
            resolveDeviceId (bool):
                DEPRECATED - no longer used, but left here to maintain compatibility.
            shuffle (bool):
                True to enable player shuffle mode; False to disable player shuffle mode; 
                None to use current player shuffle mode.  
                Default is None.  
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        This API only works for users who have Spotify Premium. 
        
        The order of execution is not guaranteed when you use this API with other Player API endpoints.
        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/PlayerMediaPlayTracks.py
        ```
        </details>
        """
        apiMethodName:str = 'PlayerMediaPlayTracks'
        apiMethodParms:SIMethodParmListContext = None
        scDevice:SpotifyConnectDevice = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("uris", uris)
            apiMethodParms.AppendKeyValue("positionMS", positionMS)
            apiMethodParms.AppendKeyValue("deviceId", deviceId)
            apiMethodParms.AppendKeyValue("delay", delay)
            apiMethodParms.AppendKeyValue("resolveDeviceId (DEPRECATED)", resolveDeviceId)
            apiMethodParms.AppendKeyValue("shuffle", shuffle)
            _logsi.LogMethodParmList(SILevel.Verbose, "Spotify Connect device play tracks", apiMethodParms)
                
            # validations.
            delay = validateDelay(delay, 0.50, 10)
            if (positionMS is None) or (positionMS < 0):
                positionMS = 0
            offsetPosition:int = 0

            # build a list of all item uri's.
            # remove any leading / trailing spaces in case user put a space between the items.
            arrUris:list[str] = None
            if isinstance(uris, list):
                arrUris = uris
            else:
                arrUris = uris.split(',')
                for idx in range(0, len(arrUris)):
                    arrUris[idx] = arrUris[idx].strip()

            # resolve the device object from the device id; activate if it's dormant.
            scDevice = self._ResolveDeviceObject(deviceId, True)

            # are spotify web player credentials configured? if so, then we will use them to create
            # an elevated authorization access token for the Spotify Web API endpoint call.
            accessTokenHeaderValue:str = self._GetSpotifyWebPlayerTokenHeaderValue(scDevice)

            # is this an active Sonos device?
            # Sonos device can still be active, even if there is no active device in Spotify playstate.
            # if spotify web player credentials are NOT configured, then we will transfer control to the
            # Sonos device local queue for playback; otherwise, we will just call the Spotify Web API
            # endpoint below with the elevated authorization access token to start playback under the
            # control of Spotify Connect. 
            if (scDevice is not None) and (scDevice.IsSonos) and (accessTokenHeaderValue is None):

                # trace.
                _logsi.LogVerbose("Tracks will be played on Sonos local queue for device: %s" % (scDevice.Title))

                # if shuffle enabled, then randomize the track uri's.
                if (shuffle):
                    _logsi.LogVerbose("Shuffle enabled; randomizing list of track uri's to play")
                    random.shuffle(arrUris)

                # set desired shuffle mode (if specified).
                if (shuffle is not None):

                    self.PlayerSetShuffleMode(shuffle, scDevice, delay)

                    # give Sonos Controller time to process the change.
                    if delay > 0:
                        _logsi.LogVerbose(TRACE_MSG_DELAY_DEVICE_SONOS % delay)
                        time.sleep(delay)

                # get the Sonos Controller player instance.
                sonosPlayer:SoCo = self.SpotifyConnectDirectory.GetSonosPlayer(scDevice)

                # clear the Sonos local queue.
                _logsi.LogVerbose("Issuing command to Sonos device \"%s\": CLEAR_QUEUE" % (scDevice.Name))
                sonosPlayer.clear_queue()

                # add all track items to the Sonos local queue.
                sharelink = ShareLinkPlugin(sonosPlayer)
                for idx in range(0, len(arrUris)):

                    # add track to the Sonos local queue.
                    uri = arrUris[idx].strip()
                    _logsi.LogVerbose("Issuing command to Sonos device \"%s\": ADD_SHARE_LINK_TO_QUEUE (uri=%s)" % (scDevice.Name, uri))
                    sharelink.add_share_link_to_queue(uri)

                    # if this is the first item added, then start play of the queue as
                    # it may take awhile to load the rest of the items.
                    if (idx == 0):

                        # start playing the Sonos local queue.
                        _logsi.LogVerbose("Issuing command to Sonos device \"%s\": PLAY_FROM_QUEUE (index=%s)" % (scDevice.Name, offsetPosition))
                        sonosPlayer.play_from_queue(index=offsetPosition)
                
                        # was a track seek position specified?
                        if (positionMS > 0):

                            # seek to the position in the track.
                            sonosPosition:str = mediaPositionHMS_fromSeconds(positionMS / 1000)  # convert from milliseconds to Sonos H:MM:SS format
                            _logsi.LogVerbose("Issuing command to Sonos device \"%s\": SEEK (position=%s)" % (scDevice.Name, sonosPosition))
                            sonosPlayer.seek(position=sonosPosition)
                
                            # give Sonos Controller time to process the change.
                            if delay > 0:
                                _logsi.LogVerbose(TRACE_MSG_DELAY_DEVICE_SONOS % delay)
                                time.sleep(delay)

                # set desired shuffle mode (if specified).
                if (shuffle is not None):

                    # give Sonos Controller time to process the change.
                    if delay > 0:
                        _logsi.LogVerbose(TRACE_MSG_DELAY_DEVICE_SONOS % delay)
                        time.sleep(delay)

                    # set shuffle mode.
                    # note that we already did this before loading the Sonos local queue.
                    # we do it again, as the `add_share_link_to_queue` method seems to cause
                    # the shuffle mode to change in some instances (a SoCo API bug maybe?).
                    self.PlayerSetShuffleMode(shuffle, scDevice, delay)

            else:

                # was the deviceId resolved? 
                # if not, then raise an exception as the Spotify Web API request will fail anyway.
                self._CheckForDeviceNotFound(scDevice, deviceId)

                # trace.
                _logsi.LogVerbose("Tracks will be played on the Spotify Connect device via Spotify Web API")

                # get current player state.
                playerState:PlayerPlayState = self.GetPlayerPlaybackState(additionalTypes=SpotifyMediaTypes.EPISODE.value)

                # if shuffle was specified, then we will enable / disable player shuffle state PRIOR to starting play.
                # if shuffle is None, then the current shuffle mode is not changed.
                # we only want to set shuffle state if the specified device is in the device list and not restricted, as
                # trying to set shuffle state for restricted devices fail with `Restriction violated` error.
                shuffleSetPriorToPlay:bool = False
                if (shuffle is not None):
                    if (scDevice.IsInDeviceList) and (not scDevice.IsRestricted) and (playerState.Context):
                        if (shuffle != playerState.IsShuffleEnabled):
                            self.PlayerSetShuffleMode(shuffle, scDevice, delay)
                            playerState.IsShuffleEnabled = shuffle    # force shuffles to match
                            shuffleSetPriorToPlay = True

                # if shuffle enabled, then randomize the track uri's.
                if (shuffle or playerState.IsShuffleEnabled):
                    _logsi.LogVerbose("Shuffle enabled; randomizing list of track uri's to play")
                    random.shuffle(arrUris)

                # build spotify web api request parameters.
                reqData:dict = \
                {
                    'position_ms': positionMS
                }
                if uris is not None:
                    reqData['uris'] = arrUris

                # formulate url parms; will manually add them since we are adding json body as well.
                urlParms:str = ''
                if (scDevice is not None):
                    urlParms = '?device_id=%s' % (scDevice.DeviceIdActivated or scDevice.Id)

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/player/play{url_parms}'.format(url_parms=urlParms))
                msg.RequestHeaders[self.AuthToken.HeaderKey] = accessTokenHeaderValue or self.AuthToken.HeaderValue
                msg.RequestJson = reqData
                self.MakeRequest('PUT', msg)
            
                # give spotify web api time to process the change.
                if delay > 0:
                    _logsi.LogVerbose(TRACE_MSG_DELAY_DEVICE % delay)
                    time.sleep(delay)
                
                # set desired shuffle mode (if specified, and not set prior to play).
                # this is necessary for some players, as starting play sometimes resets shuffle mode
                # and it needs to be restored after play starts (e.g. SpotifyConnect AddOn).
                # if shuffle argument not specified, then use initial playstate shuffle value (if one exists).
                # NOTE - track play does not support shuffle mode set; left the following commented for possible future use.
                if (shuffle is not None) and (not shuffleSetPriorToPlay):
                    #self.PlayerSetShuffleMode(shuffle, scDevice, delay)
                    pass
                elif (shuffle is None) and (not playerState.IsEmpty):
                    #self.PlayerSetShuffleMode(playerState.IsShuffleEnabled, scDevice, delay)
                    pass

            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def PlayerMediaResume(
        self, 
        deviceId:str=None,
        delay:float=0.50
        ) -> None:
        """
        Resume media play for the specified Spotify Connect device.
        
        This method requires the `user-modify-playback-state` scope.

        Args:
            deviceId (str | SpotifyConnectDevice) | None):
                The target player device identifier.
                This could be an id, name, a default device indicator (e.g. "*"), a 
                SpotifyConnectDevice object, or null to utilize the active player device.
                A device is considered resolved if a SpotifyConnectDevice object is passed
                for this argument.  An exception will be raised if the argument value could 
                not be resolved or activated.
                Examples are `0d1841b0976bae2a3a310dd74c0f3df354899bc8`, `Office`, `*`, None.  
            delay (float):
                Time delay (in seconds) to wait AFTER issuing the command to the player.  
                This delay will give the spotify web api time to process the change before 
                another command is issued.  
                Default is 0.50; value range is 0 - 10.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        This API only works for users who have Spotify Premium. 
        
        The order of execution is not guaranteed when you use this API with other Player API endpoints.
               
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/PlayerMediaResume.py
        ```
        </details>
        """
        apiMethodName:str = 'PlayerMediaResume'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("deviceId", deviceId)
            apiMethodParms.AppendKeyValue("delay", delay)
            _logsi.LogMethodParmList(SILevel.Verbose, "Spotify Connect device resume playback", apiMethodParms)
                
            # validations.
            delay = validateDelay(delay, 0.50, 10)

            # resolve the device object from the device id; activate if it's dormant.
            # we activate the device here, as it may have been paused for a long time.
            scDevice:SpotifyConnectDevice = self._ResolveDeviceObject(deviceId, True)

            # are spotify web player credentials configured? if so, then we will use them to create
            # an elevated authorization access token for the Spotify Web API endpoint call.
            accessTokenHeaderValue:str = self._GetSpotifyWebPlayerTokenHeaderValue(scDevice)

            # is this an active Sonos device?
            # Sonos device can still be active, even if there is no active device in Spotify playstate.
            if (scDevice is not None) and (scDevice.IsSonos) and (accessTokenHeaderValue is None):

                _logsi.LogVerbose("Issuing command to Sonos device %s: PLAY (RESUME)" % (scDevice.Title))
                sonosPlayer:SoCo = self.SpotifyConnectDirectory.GetSonosPlayer(scDevice)
                sonosPlayer.play()

            else:

                # was the deviceId resolved? 
                # if not, then raise an exception as the Spotify Web API request will fail anyway.
                self._CheckForDeviceNotFound(scDevice, deviceId)

                # build spotify web api request parameters.
                urlParms:dict = {}
                if (scDevice is not None):
                    urlParms['device_id'] = (scDevice.DeviceIdActivated or scDevice.Id)

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/player/play')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = accessTokenHeaderValue or self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('PUT', msg)
            
            # give spotify web api time to process the change.
            if delay > 0:
                _logsi.LogVerbose(TRACE_MSG_DELAY_DEVICE % delay)
                time.sleep(delay)

            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def PlayerMediaSeek(
        self, 
        positionMS:int=0,
        deviceId:str=None,
        delay:float=0.50,
        relativePositionMS:int=0,
        ) -> None:
        """
        Seeks to the given absolute or relative position in the user's currently playing track 
        for the specified Spotify Connect device.
        
        This method requires the `user-modify-playback-state` scope.

        Args:
            positionMS (int):
                The absolute position in milliseconds to seek to; must be a positive number or
                zero if the `relativePositionMS` argument is specified.  
                Passing in a position that is greater than the length of the track will cause the 
                player to start playing the next song.  
                Example = `25000` to start playing at the 25 second mark.  
            deviceId (str | SpotifyConnectDevice) | None):
                The target player device identifier.
                This could be an id, name, a default device indicator (e.g. "*"), a 
                SpotifyConnectDevice object, or null to utilize the active player device.
                A device is considered resolved if a SpotifyConnectDevice object is passed
                for this argument.  An exception will be raised if the argument value could 
                not be resolved or activated.
                Examples are `0d1841b0976bae2a3a310dd74c0f3df354899bc8`, `Office`, `*`, None.  
            delay (float):
                Time delay (in seconds) to wait AFTER issuing the command to the player.  
                This delay will give the spotify web api time to process the change before 
                another command is issued.  
                Default is 0.50; value range is 0 - 10.
            relativePositionMS (int):
                The relative position in milliseconds to seek to; can be a positive or negative number,
                or zero if the `positionMS` argument is specified.  
                Example = `-10000` to seek behind by 10 seconds.  
                Example = `10000` to seek ahead by 10 seconds.  
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        This API only works for users who have Spotify Premium. 
        
        The order of execution is not guaranteed when you use this API with other Player API endpoints.
        
        If using relative positioning, the `positionMS` argument must be zero (or null); the `positionMS`
        argument takes precedence if it and the `relativePositionMS` argument are specified. A positive 
        relative position that causes the seek position to be greater than the length of the track will 
        cause the player to start playing the next song.  A negative relative position that causes the 
        seek position to be less than zero will cause the player to start playing the track from the beginning.

        Note that the `relativePositionMS` functionality is not defined by the Spotify Web API.  This
        argument was added to this API to support "skip" seeking.  
                        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/PlayerMediaSeek.py
        ```
        </details>
        <details>
          <summary>Sample Code - Relative Positioning</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/PlayerMediaSeek_Relative.py
        ```
        </details>
        """
        apiMethodName:str = 'PlayerMediaSeek'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("positionMS", positionMS)
            apiMethodParms.AppendKeyValue("deviceId", deviceId)
            apiMethodParms.AppendKeyValue("delay", delay)
            apiMethodParms.AppendKeyValue("relativePositionMS", relativePositionMS)
            _logsi.LogMethodParmList(SILevel.Verbose, "Spotify Connect device seek position", apiMethodParms)
                
            # validations.
            delay = validateDelay(delay, 0.50, 10)
            if (positionMS is None):
                positionMS = 0
            if (relativePositionMS is None):
                relativePositionMS = 0

            # resolve the device object from the device id.
            scDevice:SpotifyConnectDevice = self._ResolveDeviceObject(deviceId, False)
           
            # was relative seeking specified?
            if (scDevice is not None) and (relativePositionMS != 0) and ((positionMS is None) or (positionMS <= 0)):
                
                # get current track position (from cache, since we called _ResolveDeviceObject method above).
                playState:PlayerPlayState = self.GetDevicePlaybackState(scDevice)
                newPositionMS:int = playState.ProgressMS
                if (newPositionMS is not None) and (newPositionMS > 0):
                    
                    # calculate new position; if less than zero, then force it to zero.
                    newPositionMS += relativePositionMS
                    if (newPositionMS < 0):
                        newPositionMS = 0
                    positionMS = newPositionMS

            # are spotify web player credentials configured? if so, then we will use them to create
            # an elevated authorization access token for the Spotify Web API endpoint call.
            accessTokenHeaderValue:str = self._GetSpotifyWebPlayerTokenHeaderValue(scDevice)

            # is this an active Sonos device?
            # Sonos device can still be active, even if there is no active device in Spotify playstate.
            if (scDevice is not None) and (scDevice.IsSonos) and (accessTokenHeaderValue is None):

                sonosPosition:str = mediaPositionHMS_fromSeconds(positionMS / 1000)    # convert from milliseconds to Sonos H:MM:SS format
                _logsi.LogVerbose("Issuing command to Sonos device %s: SEEK (sonosPosition=%s)" % (scDevice.Title, sonosPosition))
                sonosPlayer:SoCo = self.SpotifyConnectDirectory.GetSonosPlayer(scDevice)
                sonosPlayer.seek(str(sonosPosition))

            else:

                # was the deviceId resolved? 
                # if not, then raise an exception as the Spotify Web API request will fail anyway.
                self._CheckForDeviceNotFound(scDevice, deviceId)

                # build spotify web api request parameters.
                urlParms:dict = \
                {
                    'position_ms': positionMS
                }
                if (scDevice is not None):
                    urlParms['device_id'] = (scDevice.DeviceIdActivated or scDevice.Id)

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/player/seek')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = accessTokenHeaderValue or self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('PUT', msg)
            
            # give spotify web api time to process the change.
            if delay > 0:
                _logsi.LogVerbose(TRACE_MSG_DELAY_DEVICE % delay)
                time.sleep(delay)

            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def PlayerMediaSkipNext(
        self, 
        deviceId:str=None,
        delay:float=0.50
        ) -> None:
        """
        Skips to next track in the user's queue for the specified Spotify Connect device.
        
        This method requires the `user-modify-playback-state` scope.

        Args:
            deviceId (str | SpotifyConnectDevice) | None):
                The target player device identifier.
                This could be an id, name, a default device indicator (e.g. "*"), a 
                SpotifyConnectDevice object, or null to utilize the active player device.
                A device is considered resolved if a SpotifyConnectDevice object is passed
                for this argument.  An exception will be raised if the argument value could 
                not be resolved or activated.
                Examples are `0d1841b0976bae2a3a310dd74c0f3df354899bc8`, `Office`, `*`, None.  
            delay (float):
                Time delay (in seconds) to wait AFTER issuing the command to the player.  
                This delay will give the spotify web api time to process the change before 
                another command is issued.  
                Default is 0.50; value range is 0 - 10.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        This API only works for users who have Spotify Premium. 
        
        The order of execution is not guaranteed when you use this API with other Player API endpoints.
        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/PlayerMediaSkipNext.py
        ```
        </details>
        """
        apiMethodName:str = 'PlayerMediaSkipNext'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("deviceId", deviceId)
            apiMethodParms.AppendKeyValue("delay", delay)
            _logsi.LogMethodParmList(SILevel.Verbose, "Spotify Connect device skip next", apiMethodParms)
                
            # validations.
            delay = validateDelay(delay, 0.50, 10)

            # resolve the device object from the device id.
            scDevice:SpotifyConnectDevice = self._ResolveDeviceObject(deviceId, False)

            # are spotify web player credentials configured? if so, then we will use them to create
            # an elevated authorization access token for the Spotify Web API endpoint call.
            accessTokenHeaderValue:str = self._GetSpotifyWebPlayerTokenHeaderValue(scDevice)

            # is this an active Sonos device?
            # Sonos device can still be active, even if there is no active device in Spotify playstate.
            if (scDevice is not None) and (scDevice.IsSonos) and (accessTokenHeaderValue is None):

                _logsi.LogVerbose("Issuing command to Sonos device %s: NEXT" % (scDevice.Title))
                sonosPlayer:SoCo = self.SpotifyConnectDirectory.GetSonosPlayer(scDevice)
                sonosPlayer.next()

            else:

                # was the deviceId resolved? 
                # if not, then raise an exception as the Spotify Web API request will fail anyway.
                self._CheckForDeviceNotFound(scDevice, deviceId)

                # build spotify web api request parameters.
                urlParms:dict = {}
                if (scDevice is not None):
                    urlParms['device_id'] = (scDevice.DeviceIdActivated or scDevice.Id)

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/player/next')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = accessTokenHeaderValue or self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('POST', msg)
            
            # give spotify web api time to process the change.
            if delay > 0:
                _logsi.LogVerbose(TRACE_MSG_DELAY_DEVICE % delay)
                time.sleep(delay)

            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def PlayerMediaSkipPrevious(
        self, 
        deviceId:str=None,
        delay:float=0.50
        ) -> None:
        """
        Skips to previous track in the user's queue for the specified Spotify Connect device.
        
        This method requires the `user-modify-playback-state` scope.

        Args:
            deviceId (str | SpotifyConnectDevice) | None):
                The target player device identifier.
                This could be an id, name, a default device indicator (e.g. "*"), a 
                SpotifyConnectDevice object, or null to utilize the active player device.
                A device is considered resolved if a SpotifyConnectDevice object is passed
                for this argument.  An exception will be raised if the argument value could 
                not be resolved or activated.
                Examples are `0d1841b0976bae2a3a310dd74c0f3df354899bc8`, `Office`, `*`, None.  
            delay (float):
                Time delay (in seconds) to wait AFTER issuing the command to the player.  
                This delay will give the spotify web api time to process the change before 
                another command is issued.  
                Default is 0.50; value range is 0 - 10.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        This API only works for users who have Spotify Premium. 
        
        The order of execution is not guaranteed when you use this API with other Player API endpoints.
        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/PlayerMediaSkipPrevious.py
        ```
        </details>
        """
        apiMethodName:str = 'PlayerMediaSkipPrevious'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("deviceId", deviceId)
            apiMethodParms.AppendKeyValue("delay", delay)
            _logsi.LogMethodParmList(SILevel.Verbose, "Spotify Connect device skip previous", apiMethodParms)
                
            # validations.
            delay = validateDelay(delay, 0.50, 10)

            # resolve the device object from the device id.
            scDevice:SpotifyConnectDevice = self._ResolveDeviceObject(deviceId, False)

            # are spotify web player credentials configured? if so, then we will use them to create
            # an elevated authorization access token for the Spotify Web API endpoint call.
            accessTokenHeaderValue:str = self._GetSpotifyWebPlayerTokenHeaderValue(scDevice)

            # is this an active Sonos device?
            # Sonos device can still be active, even if there is no active device in Spotify playstate.
            if (scDevice is not None) and (scDevice.IsSonos) and (accessTokenHeaderValue is None):

                _logsi.LogVerbose("Issuing command to Sonos device %s: PREVIOUS" % (scDevice.Title))
                sonosPlayer:SoCo = self.SpotifyConnectDirectory.GetSonosPlayer(scDevice)
                sonosPlayer.previous()

            else:

                # was the deviceId resolved? 
                # if not, then raise an exception as the Spotify Web API request will fail anyway.
                self._CheckForDeviceNotFound(scDevice, deviceId)

                # build spotify web api request parameters.
                urlParms:dict = {}
                if (scDevice is not None):
                    urlParms['device_id'] = (scDevice.DeviceIdActivated or scDevice.Id)

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/player/previous')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = accessTokenHeaderValue or self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('POST', msg)
            
            # give spotify web api time to process the change.
            if delay > 0:
                _logsi.LogVerbose(TRACE_MSG_DELAY_DEVICE % delay)
                time.sleep(delay)

            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def PlayerSetRepeatMode(
        self, 
        state:str='off',
        deviceId:str=None,
        delay:float=0.50
        ) -> None:
        """
        Set repeat mode for the specified Spotify Connect device.
        
        This method requires the `user-modify-playback-state` scope.

        Args:
            state (str):
                The repeat mode to set: 
                - `track`   - will repeat the current track.
                - `context` - will repeat the current context.
                - `off`     - will turn repeat off.
                Default: `off`  
            deviceId (str | SpotifyConnectDevice) | None):
                The target player device identifier.
                This could be an id, name, a default device indicator (e.g. "*"), a 
                SpotifyConnectDevice object, or null to utilize the active player device.
                A device is considered resolved if a SpotifyConnectDevice object is passed
                for this argument.  An exception will be raised if the argument value could 
                not be resolved or activated.
                Examples are `0d1841b0976bae2a3a310dd74c0f3df354899bc8`, `Office`, `*`, None.  
            delay (float):
                Time delay (in seconds) to wait AFTER issuing the command to the player.  
                This delay will give the spotify web api time to process the change before 
                another command is issued.  
                Default is 0.50; value range is 0 - 10.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        This API only works for users who have Spotify Premium. 
        
        The order of execution is not guaranteed when you use this API with other Player API endpoints.
        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/PlayerSetRepeatMode.py
        ```
        </details>
        """
        apiMethodName:str = 'PlayerSetRepeatMode'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("state", state)
            apiMethodParms.AppendKeyValue("deviceId", deviceId)
            apiMethodParms.AppendKeyValue("delay", delay)
            _logsi.LogMethodParmList(SILevel.Verbose, "Set Spotify Connect device set repeat mode", apiMethodParms)
                
            # validations.
            delay = validateDelay(delay, 0.50, 10)

            # resolve the device object from the device id.
            scDevice:SpotifyConnectDevice = self._ResolveDeviceObject(deviceId, False)

            # are spotify web player credentials configured? if so, then we will use them to create
            # an elevated authorization access token for the Spotify Web API endpoint call.
            accessTokenHeaderValue:str = self._GetSpotifyWebPlayerTokenHeaderValue(scDevice)

            # is this an active Sonos device?
            # Sonos device can still be active, even if there is no active device in Spotify playstate.
            if (scDevice is not None) and (scDevice.IsSonos) and (accessTokenHeaderValue is None):

                # get current Spotify Connect player state.
                playerState = self.GetPlayerPlaybackStateSonos(scDevice)
            
                # set the Sonos PlayMode directly (instead of setting the Sonos repeat property)!
                # The Spotify Web API PlayerState `ShuffleState` value can sometimes be different than what the
                # Sonos device reports for its `shuffle` property value!
                if state == 'track':
                    sonos_repeat = 'ONE'
                elif state == 'off':
                    sonos_repeat = False
                elif state == 'context':
                    sonos_repeat = True
                else:
                    sonos_repeat = False
                playMode:str = SONOS_PLAY_MODE_BY_MEANING[(playerState.ShuffleState, sonos_repeat)]
                
                # execute SoCo api request.
                _logsi.LogVerbose("Issuing command to Sonos device %s: REPEAT (playmode=%s)" % (scDevice.Title, playMode))
                sonosPlayer:SoCo = self.SpotifyConnectDirectory.GetSonosPlayer(scDevice)
                sonosPlayer.play_mode = playMode

            else:

                # was the deviceId resolved? 
                # if not, then raise an exception as the Spotify Web API request will fail anyway.
                self._CheckForDeviceNotFound(scDevice, deviceId)

                # build spotify web api request parameters.
                urlParms:dict = \
                {
                    'state': state
                }
                if (scDevice is not None):
                    urlParms['device_id'] = (scDevice.DeviceIdActivated or scDevice.Id)

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/player/repeat')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = accessTokenHeaderValue or self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('PUT', msg)
            
            # give spotify web api time to process the change.
            if delay > 0:
                _logsi.LogVerbose(TRACE_MSG_DELAY_DEVICE % delay)
                time.sleep(delay)

            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def PlayerSetShuffleMode(
        self, 
        state:bool=False,
        deviceId:str=None,
        delay:float=0.50
        ) -> None:
        """
        Set shuffle mode for the specified Spotify Connect device.
        
        This method requires the `user-modify-playback-state` scope.

        Args:
            state (bool):
                The shuffle mode to set: 
                - `True`  - Shuffle user's playback.
                - `False` - Do not shuffle user's playback.
                Default is False
            deviceId (str | SpotifyConnectDevice) | None):
                The target player device identifier.
                This could be an id, name, a default device indicator (e.g. "*"), a 
                SpotifyConnectDevice object, or null to utilize the active player device.
                A device is considered resolved if a SpotifyConnectDevice object is passed
                for this argument.  An exception will be raised if the argument value could 
                not be resolved or activated.
                Examples are `0d1841b0976bae2a3a310dd74c0f3df354899bc8`, `Office`, `*`, None.  
            delay (float):
                Time delay (in seconds) to wait AFTER issuing the command to the player.  
                This delay will give the spotify web api time to process the change before 
                another command is issued.  
                Default is 0.50; value range is 0 - 10.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        This API only works for users who have Spotify Premium. 
        
        The order of execution is not guaranteed when you use this API with other Player API endpoints.
        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/PlayerSetShuffleMode.py
        ```
        </details>
        """
        apiMethodName:str = 'PlayerSetShuffleMode'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("state", state)
            apiMethodParms.AppendKeyValue("deviceId", deviceId)
            apiMethodParms.AppendKeyValue("delay", delay)
            _logsi.LogMethodParmList(SILevel.Verbose, "Set Spotify Connect device set shuffle mode", apiMethodParms)
                
            # validations.
            delay = validateDelay(delay, 0.50, 10)

            # resolve the device object from the device id.
            scDevice:SpotifyConnectDevice = self._ResolveDeviceObject(deviceId, False)

            # are spotify web player credentials configured? if so, then we will use them to create
            # an elevated authorization access token for the Spotify Web API endpoint call.
            accessTokenHeaderValue:str = self._GetSpotifyWebPlayerTokenHeaderValue(scDevice)

            # is this an active Sonos device?
            # Sonos device can still be active, even if there is no active device in Spotify playstate.
            if (scDevice is not None) and (scDevice.IsSonos) and (accessTokenHeaderValue is None):

                # get current Spotify Connect player state.
                playerState = self.GetPlayerPlaybackStateSonos(scDevice)
            
                # set the Sonos PlayMode directly (instead of setting the Sonos `shuffle` property)!
                # the Spotify Web API PlayerState `RepeatState` value can sometimes be different than what the
                # Sonos device reports for its `repeat` property value!
                sonos_repeat:str
                if playerState.RepeatState == 'track':
                    sonos_repeat = 'ONE'
                elif playerState.RepeatState == 'off':
                    sonos_repeat = False
                elif playerState.RepeatState == 'context':
                    sonos_repeat = True
                else:   # assume off if nothing else.
                    sonos_repeat = False
                playMode:str = SONOS_PLAY_MODE_BY_MEANING[(state, sonos_repeat)]
                
                # execute SoCo api request.
                _logsi.LogVerbose("Issuing command to Sonos device %s: SHUFFLE (playmode=%s)" % (scDevice.Title, playMode))
                sonosPlayer:SoCo = self.SpotifyConnectDirectory.GetSonosPlayer(scDevice)
                sonosPlayer.play_mode = playMode

                # give Sonos Controller time to process the change.
                if delay > 0:
                    _logsi.LogVerbose(TRACE_MSG_DELAY_DEVICE_SONOS % delay)
                    time.sleep(delay)

            else:

                # was the deviceId resolved? 
                # if not, then raise an exception as the Spotify Web API request will fail anyway.
                self._CheckForDeviceNotFound(scDevice, deviceId)

                # build spotify web api request parameters.
                urlParms:dict = \
                {
                    'state': state
                }
                if (scDevice is not None):
                    urlParms['device_id'] = (scDevice.DeviceIdActivated or scDevice.Id)

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/player/shuffle')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = accessTokenHeaderValue or self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('PUT', msg)
            
                # give spotify web api time to process the change.
                if delay > 0:
                    _logsi.LogVerbose(TRACE_MSG_DELAY_DEVICE % delay)
                    time.sleep(delay)

            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def PlayerSetVolume(
        self, 
        volumePercent:int,
        deviceId:str=None,
        delay:float=0.50
        ) -> None:
        """
        Set volume level for the specified Spotify Connect device.
        
        This method requires the `user-modify-playback-state` scope.

        Args:
            volumePercent (int):
                The volume to set.  
                Must be a value from 0 to 100 inclusive.
                Example: `50`
            deviceId (str | SpotifyConnectDevice) | None):
                The target player device identifier.
                This could be an id, name, a default device indicator (e.g. "*"), a 
                SpotifyConnectDevice object, or null to utilize the active player device.
                A device is considered resolved if a SpotifyConnectDevice object is passed
                for this argument.  An exception will be raised if the argument value could 
                not be resolved or activated.
                Examples are `0d1841b0976bae2a3a310dd74c0f3df354899bc8`, `Office`, `*`, None.  
            delay (float):
                Time delay (in seconds) to wait AFTER issuing the command to the player.  
                This delay will give the spotify web api time to process the change before 
                another command is issued.  
                Default is 0.50; value range is 0 - 10.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        This API only works for users who have Spotify Premium. 
        
        The order of execution is not guaranteed when you use this API with other Player API endpoints.
        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/PlayerSetVolume.py
        ```
        </details>
        """
        apiMethodName:str = 'PlayerSetVolume'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("volumePercent", volumePercent)
            apiMethodParms.AppendKeyValue("deviceId", deviceId)
            apiMethodParms.AppendKeyValue("delay", delay)
            _logsi.LogMethodParmList(SILevel.Verbose, "Set Spotify Connect device set volume level", apiMethodParms)
                
            # validations.
            delay = validateDelay(delay, 0.50, 10)

            # resolve the device object from the device id.
            scDevice:SpotifyConnectDevice = self._ResolveDeviceObject(deviceId, False)

            # are spotify web player credentials configured? if so, then we will use them to create
            # an elevated authorization access token for the Spotify Web API endpoint call.
            accessTokenHeaderValue:str = self._GetSpotifyWebPlayerTokenHeaderValue(scDevice)

            # is this an active Sonos device?
            # Sonos device can still be active, even if there is no active device in Spotify playstate.
            if (scDevice is not None) and (scDevice.IsSonos) and (accessTokenHeaderValue is None):

                _logsi.LogVerbose("Issuing command to Sonos device %s: VOLUME = %s" % (scDevice.Title, volumePercent))
                sonosPlayer:SoCo = self.SpotifyConnectDirectory.GetSonosPlayer(scDevice)
                sonosPlayer.volume = volumePercent

            else:

                # was the deviceId resolved? 
                # if not, then raise an exception as the Spotify Web API request will fail anyway.
                self._CheckForDeviceNotFound(scDevice, deviceId)

                # build spotify web api request parameters.
                urlParms:dict = \
                {
                    'volume_percent': volumePercent
                }
                if (scDevice is not None):
                    urlParms['device_id'] = (scDevice.DeviceIdActivated or scDevice.Id)

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/player/volume')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = accessTokenHeaderValue or self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('PUT', msg)
            
            # give spotify web api time to process the change.
            if delay > 0:
                _logsi.LogVerbose(TRACE_MSG_DELAY_DEVICE % delay)
                time.sleep(delay)

            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def PlayerTransferPlayback(
        self, 
        deviceId:str=None,
        play:bool=True,
        delay:float=0.50,
        refreshDeviceList:bool=True,
        forceActivateDevice:bool=True,
        deviceIdFrom:str=None,
        ) -> SpotifyConnectDevice:
        """
        Transfer playback to a new Spotify Connect device and optionally begin playback.
        
        This method requires the `user-modify-playback-state` scope.

        Args:
            deviceId (str | SpotifyConnectDevice) | None):
                The target player device identifier.
                This could be an id, name, a default device indicator (e.g. "*"), a 
                SpotifyConnectDevice object, or null to utilize the active player device.
                A device is considered resolved if a SpotifyConnectDevice object is passed
                for this argument.  An exception will be raised if the argument value could 
                not be resolved or activated.
                Examples are `0d1841b0976bae2a3a310dd74c0f3df354899bc8`, `Office`, `*`, None.  
            play (bool):
                The transfer method:  
                - `True`  - ensure playback happens on new device.   
                - `False` - keep the current playback state.  
                Default: `True`  
            delay (float):
                Time delay (in seconds) to wait AFTER issuing the command to the player.  
                This delay will give the spotify web api time to process the change before 
                another command is issued.  
                Default is 0.50; value range is 0 - 10.
            refreshDeviceList (bool):
                DEPRECATED - no longer used, but left here to maintain compatibility.
            forceActivateDevice (bool):
                True to issue a Spotify Connect Disconnect call prior to transfer, which will
                force the device to reconnect to Spotify Connect; otherwise, False to not
                disconnect.
                Default is True.  
            deviceIdFrom (str | SpotifyConnectDevice) | None):
                The player device identifier where play is being transferred from.
                This could be an id, name, a default device indicator (e.g. "*"), a 
                SpotifyConnectDevice object, or null.
                A device is considered resolved if a SpotifyConnectDevice object is passed
                for this argument.  
                Examples are `0d1841b0976bae2a3a310dd74c0f3df354899bc8`, `Office`, `*`, None.  
                
        Returns:
            A `SpotifyConnectDevice` object for the device where playback was transferred to.

        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        This API only works for users who have Spotify Premium. 
        
        The order of execution is not guaranteed when you use this API with other Player API endpoints.

        The `deviceIdFrom` argument is not part of the Spotify Web API specification.  If a value
        was supplied, then we will attempt to stop play on the device if it's needed.  This is required 
        if transferring playback from a Sonos device that is playing content on its local queue; if you 
        don't stop playback on it, then it and the target device will both be playing!
        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/PlayerTransferPlayback.py
        ```
        </details>
        """
        apiMethodName:str = 'PlayerTransferPlayback'
        apiMethodParms:SIMethodParmListContext = None
        scDevice:SpotifyConnectDevice = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("deviceId", deviceId)
            apiMethodParms.AppendKeyValue("play", play)
            apiMethodParms.AppendKeyValue("delay", delay)
            apiMethodParms.AppendKeyValue("refreshDeviceList (DEPRECATED)", refreshDeviceList)
            apiMethodParms.AppendKeyValue("forceActivateDevice", forceActivateDevice)
            apiMethodParms.AppendKeyValue("deviceIdFrom", deviceIdFrom)
            _logsi.LogMethodParmList(SILevel.Verbose, "Transfer playback to a new Spotify Connect device", apiMethodParms)
            
            # validations.
            delay = validateDelay(delay, 0.50, 10)
            if (play is None):
                play = True
            if (forceActivateDevice is None):
                forceActivateDevice = True

            # was a from deviceId specified? if so, then we will attempt to stop play on the device
            # if it's needed.  this is required if transferring playback from a Sonos device that is
            # playing content on its local queue; if you don't stop playback on it, then it and the
            # target device will both be playing!
            if (deviceIdFrom is not None):

                # trace.
                _logsi.LogVerbose("FROM deviceId supplied; checking to see if we need to pause play on device \"%s\" prior to transferring playback to device \"%s\"" % (deviceIdFrom, deviceId))

                # resolve from device object; no need to activate it for what we want here.
                scDeviceFrom:SpotifyConnectDevice = self._ResolveDeviceObject(deviceIdFrom, activateDevice=False)

                # if it's a Sonos, then pause the player.
                # note that for other brands, the Spotify Web API transfer playback takes care of
                # pausing the player since everything is under the Spotify players control.
                if (scDeviceFrom is not None) and (scDeviceFrom.IsSonos):
                    #self.PlayerMediaPause(scDeviceFrom)
                    try:
                        self.PlayerMediaPause(scDeviceFrom)
                    except:
                        # ignore exceptions, since this is a convenience call to pause the from player.
                        _logsi.LogVerbose("Ignoring previous exception, since this is a convenience call to pause the from player")
                        pass

            # resolve the device object from the device id; activate if it's dormant.
            # for transfer playback, we will always activate the device.
            scDevice = self._ResolveDeviceObject(deviceId, True)

            # was the deviceId resolved? 
            # if not, then raise an exception as the Spotify Web API request will fail anyway.
            self._CheckForDeviceNotFound(scDevice, deviceId)

            # are spotify web player credentials configured? if so, then we will use them to create
            # an elevated authorization access token for the Spotify Web API endpoint call.
            accessTokenHeaderValue:str = self._GetSpotifyWebPlayerTokenHeaderValue()

            # is this a Sonos device? 
            # if so, then control was automatically transferred by activating the device.
            # note that the Spotify Web API cannot stop nor start play on the device either, 
            # as it's considered a restricted device and the Spotify Web API cannot control it!
            # all requests to control the device will be made via the Sonos Controller API.
            if (scDevice.IsSonos) and (accessTokenHeaderValue is None):

                # get Sonos Controller instance for the device.
                sonosPlayer:SoCo = self.SpotifyConnectDirectory.GetSonosPlayer(scDevice)

                # get current Sonos transport status.
                sonosTransportInfo:dict = sonosPlayer.get_current_transport_info()
                currentTransportState:str = sonosTransportInfo.get('current_transport_state', None)
                currentTransportStatus:str = sonosTransportInfo.get('current_transport_status', None)
                _logsi.LogVerbose("Sonos device %s current transport state after activation: \"%s\" (Status=%s)" % (scDevice.Title, currentTransportState, currentTransportStatus))

                # stop / start play as requested.
                wasCmdIssued:bool = False
                if currentTransportState == 'PLAYING':
                    if play == False:
                        self.PlayerMediaPause(scDevice)
                        wasCmdIssued = True
                elif currentTransportState in ['PAUSED_PLAYBACK','STOPPED','TRANSITIONING']:
                    if play == True:
                        self.PlayerMediaResume(scDevice)
                        wasCmdIssued = True
                                        
                # give Sonos Controller time to process the change.
                if (wasCmdIssued) and (delay > 0):
                    _logsi.LogVerbose(TRACE_MSG_DELAY_DEVICE_SONOS % delay)
                    time.sleep(delay)

                # trace.
                _logsi.LogVerbose("Sonos device detected (IsRestricted); bypassing call to Spotify Web API Transfer Playback endpoint")
                return scDevice

            # before transferring playback to the device, we first need to check to see if anything
            # is currently playing.  if nothing is playing, AND we are not using Spotify Web Player
            # elevated access token, then we have to start something; otherwise the transfer playback 
            # will result in a `Restriction Violated` error!  

            # do we have a currently active player?
            scActiveDevice:SpotifyConnectDevice = self._SpotifyConnectDirectory.GetActiveDevice(refresh=False)
            if (scActiveDevice is None) and (accessTokenHeaderValue is None):

                # no - at this point nothing is playing, so we will try to start playing something
                # to avoid the `Restriction Violated` error.  this will automatically transfer
                # playback to the default device.
                _logsi.LogVerbose("Nothing is currently playing on Spotify Connect device %s" % (scDevice.Title))

                # any previously played content?
                if (self.PlayerLastPlayedInfo.IsEmpty):

                    # no - start playing track favorites instead of transferring playback.
                    _logsi.LogVerbose("Playing track favorites instead of transferring playback")
                    self.PlayerMediaPlayTrackFavorites(scDevice, False, limitTotal=20)
                    return scDevice

                else:

                    # yes - play previously played content.
                    if (self.PlayerLastPlayedInfo.Context is not None):
                        _logsi.LogVerbose("Resuming last played context and track instead of transferring playback")
                        self.PlayerMediaPlayContext(self.PlayerLastPlayedInfo.Context.Uri, self.PlayerLastPlayedInfo.Item.Uri, None, self.PlayerLastPlayedInfo.ProgressMS, scDevice, shuffle=False)
                    else:
                        _logsi.LogVerbose("Resuming last played track instead of transferring playback")
                        self.PlayerMediaPlayTracks(self.PlayerLastPlayedInfo.Item.Uri, self.PlayerLastPlayedInfo.ProgressMS, scDevice, shuffle=False)
                    return scDevice

            # is the resolved device already active?
            if (scActiveDevice is not None) and (scActiveDevice.Id == scDevice.Id):

                # trace.
                _logsi.LogVerbose("Spotify Connect device %s is already active (by Id); no need to transfer playback" % (scDevice.Title))

            elif (scActiveDevice is not None) and (scActiveDevice.Name == scDevice.Name) and ((scActiveDevice.Id or "") == ""):

                # trace.
                _logsi.LogVerbose("Spotify Connect device %s is already active (by Name); no need to transfer playback" % (scDevice.Title))

            else:

                # build spotify web api request parameters.
                reqData:dict = \
                {
                    'device_ids': [(scDevice.DeviceIdActivated or scDevice.Id)]
                }
                if (play is not None):
                    reqData['play'] = play

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/player')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = accessTokenHeaderValue or self.AuthToken.HeaderValue
                msg.RequestJson = reqData
                self.MakeRequest('PUT', msg)
            
                # give spotify web api time to process the change.
                if delay > 0:
                    _logsi.LogVerbose(TRACE_MSG_DELAY_DEVICE % delay)
                    time.sleep(delay)

            # pause / resume play based on `play` argument specified.
            # sometimes the `play` argument to the Spotify Web API transfer playback command 
            # is not honored, so we do a pause / resume here to ensure it's correct.  
            try:
                # if (play is None):
                #     _logsi.LogVerbose("Resuming play on device was bypassed, as play argument was not supplied")
                if (play):
                    _logsi.LogVerbose("Resuming play on device, in case it's not already playing")
                    self.PlayerMediaResume(scDevice)
                else:
                    _logsi.LogVerbose("Pausing play on device, in case it's not already paused")
                    self.PlayerMediaPause(scDevice)
            except:
                # in case a "Restriction violated" error is raised; just ignore it.
                pass
                
            # return target player device instance.
            return scDevice

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def RemoveAlbumFavorites(
        self, 
        ids:str=None
        ) -> None:
        """
        Remove one or more albums from the current user's 'Your Library'.
        
        This method requires the `user-library-modify` scope.
        
        Args:
            ids (str):  
                A comma-separated list of the Spotify IDs for the albums.  
                Maximum: 50 IDs.  
                Example: `6vc9OTcyd3hyzabCmsdnwE,382ObEPsp2rxGrnsizN5TX`
                If null, the currently playing track album uri id value is used.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.
                
        No error will be raised if an album id in the list does not exist in the 
        user's 'Your Library'.
        
        An SpotifyWebApiError will be raised if a specified album id does not exist
        in the Spotify music catalog.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/RemoveAlbumFavorites.py
        ```
        </details>
        """
        apiMethodName:str = 'RemoveAlbumFavorites'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            _logsi.LogMethodParmList(SILevel.Verbose, "Remove album(s) from user favorites", apiMethodParms)
                
            # if ids not specified, then return currently playing album id value.
            if (ids is None) or (len(ids.strip()) == 0):
                uri = self.GetPlayerNowPlayingAlbumUri()
                if uri is not None:
                    ids = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'ids'), logsi=_logsi)

            # build a list of all item id's.
            # remove any leading / trailing spaces in case user put a space between the items.
            arrIds:list[str] = ids.split(',')
            for idx in range(0, len(arrIds)):
                arrIds[idx] = arrIds[idx].strip()
                
            # build spotify web api request parameters.
            reqData:dict = \
            {
                'ids': arrIds
            }

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/albums')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.RequestJson = reqData
            self.MakeRequest('DELETE', msg)
            
            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def RemoveAudiobookFavorites(
        self, 
        ids:str=None,
        ) -> None:
        """
        Remove one or more audiobooks from the current user's 'Your Library'.
        
        This method requires the `user-library-modify` scope.
        
        Args:
            ids (str):  
                A comma-separated list of the Spotify IDs for the audiobooks.  
                Maximum: 50 IDs.  
                Example: `3PFyizE2tGCSRLusl2Qizf,7iHfbu1YPACw6oZPAFJtqe`
                If null, the currently playing audiobook uri id value is used.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.
                
        No error will be raised if a audiobook id in the list does not exist in the 
        user's 'Your Library'.
        
        An SpotifyWebApiError will be raised if a specified album id does not exist
        in the Spotify music catalog.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/RemoveAudiobookFavorites.py
        ```
        </details>
        """
        apiMethodName:str = 'RemoveAudiobookFavorites'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            _logsi.LogMethodParmList(SILevel.Verbose, "Remove audiobook(s) from user favorites", apiMethodParms)
                
            # if ids not specified, then return currently playing id value.
            if (ids is None) or (len(ids.strip()) == 0):
                uri = self.GetPlayerNowPlayingAudiobookUri()
                if uri is not None:
                    ids = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'ids'), logsi=_logsi)

            # build a list of all item id's.
            # remove any leading / trailing spaces in case user put a space between the items.
            arrIds:list[str] = ids.split(',')
            for idx in range(0, len(arrIds)):
                arrIds[idx] = arrIds[idx].strip()
                
            # build spotify web api request parameters.
            reqData:dict = \
            {
                'ids': arrIds
            }

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/audiobooks')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.RequestJson = reqData
            self.MakeRequest('DELETE', msg)
            
            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def RemoveEpisodeFavorites(
        self, 
        ids:str=None,
        ) -> None:
        """
        Remove one or more episodes from the current user's 'Your Library'.
        
        This method requires the `user-library-modify` scope.
        
        Args:
            ids (str):  
                A comma-separated list of the Spotify IDs for the episodes.  
                Maximum: 50 IDs.  
                Example: `6kAsbP8pxwaU2kPibKTuHE,4rOoJ6Egrf8K2IrywzwOMk`
                If null, the currently playing episode uri id value is used.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.
                
        No error will be raised if a episode id in the list does not exist in the 
        user's 'Your Library'.
        
        An SpotifyWebApiError will be raised if a specified album id does not exist
        in the Spotify music catalog.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/RemoveEpisodeFavorites.py
        ```
        </details>
        """
        apiMethodName:str = 'RemoveEpisodeFavorites'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            _logsi.LogMethodParmList(SILevel.Verbose, "Remove episode(s) from user favorites", apiMethodParms)
                
            # if ids not specified, then return currently playing id value.
            if (ids is None) or (len(ids.strip()) == 0):
                uri = self.GetPlayerNowPlayingUri(SpotifyMediaTypes.EPISODE.value)
                if uri is not None:
                    ids = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'ids'), logsi=_logsi)

            # build a list of all item id's.
            # remove any leading / trailing spaces in case user put a space between the items.
            arrIds:list[str] = ids.split(',')
            for idx in range(0, len(arrIds)):
                arrIds[idx] = arrIds[idx].strip()
                
            # build spotify web api request parameters.
            reqData:dict = \
            {
                'ids': arrIds
            }

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/episodes')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.RequestJson = reqData
            self.MakeRequest('DELETE', msg)
            
            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def RemovePlaylist(
        self, 
        playlistId:str=None, 
        ) -> None:
        """
        Remove a user's playlist (calls the `UnfollowPlaylist` method).
        
        This method requires the `playlist-modify-public` and `playlist-modify-private` scope.
        
        Args:
        
            playlistId (str):  
                The Spotify ID of the playlist (e.g. `5AC9ZXA7nJ7oGWO911FuDG`).
                If null, the currently playing playlist uri id value is used.
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.
        
        There is no Spotify Web API endpoint for deleting a playlist.  The notion of deleting a playlist is 
        not relevant within the Spotify playlist system. Even if you are the playlist owner and you choose 
        to manually remove it from your own list of playlists, you are simply unfollowing it. Although this 
        behavior may sound strange, it means that other users who are already following the playlist can keep 
        enjoying it. 
        
        [Manually restoring a deleted playlist](https://www.spotify.com/us/account/recover-playlists/) through 
        the Spotify Accounts Service is the same thing as following one of your own playlists that you have 
        previously unfollowed.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/RemovePlaylist.py
        ```
        </details>
        """
        apiMethodName:str = 'RemovePlaylist'
        apiMethodParms:SIMethodParmListContext = None
        result:str = None
        
        try:

            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("playlistId", playlistId)
            _logsi.LogMethodParmList(SILevel.Verbose, "Remove (by unfollowing) a user's playlist", apiMethodParms)
            
            # unfollow the playlist for the specified user.
            return self.UnfollowPlaylist(playlistId)
                
        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def RemovePlaylistItems(
        self, 
        playlistId:str, 
        uris:str=None,
        snapshotId:str=None
        ) -> str:
        """
        Remove one or more items from a user's playlist.
        
        This method requires the `playlist-modify-public` and `playlist-modify-private` scope.
        
        Args:
        
            playlistId (str):  
                The Spotify ID of the playlist.
                Example: `5AC9ZXA7nJ7oGWO911FuDG`
            uris (str):  
                A comma-separated list of Spotify URIs to remove; can be track or episode URIs.  
                Example: `spotify:track:4iV5W9uYEdYUVa79Axb7Rh,spotify:episode:26c0zVyOv1lzfYpBXdh1zC`.  
                A maximum of 100 items can be specified in one request.
                If null, the currently playing context uri value is used.
            snapshotId (str):  
                The playlist's snapshot ID against which you want to make the changes.  
                The API will validate that the specified items exist and in the specified positions and 
                make the changes, even if more recent changes have been made to the playlist.
                If null, the current playlist is updated.  
                Example: `MTk3LGEzMjUwZGYwODljNmI5ZjAxZTRjZThiOGI4NzZhM2U5M2IxOWUyMDQ`
                Default is null.
                
        Returns:
            A snapshot ID for the updated playlist.
            
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        The `snapshotId` argument value will be returned if no items were removed; otherwise, a
        new snapshot id value will be returned.
        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/RemovePlaylistItems.py
        ```
        </details>
        """
        apiMethodName:str = 'RemovePlaylistItems'
        apiMethodParms:SIMethodParmListContext = None
        result:str = None
        
        try:

            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("playlistId", playlistId)
            apiMethodParms.AppendKeyValue("uris", uris)
            apiMethodParms.AppendKeyValue("snapshotId", snapshotId)
            _logsi.LogMethodParmList(SILevel.Verbose, "Remove item(s) from a user's playlist", apiMethodParms)
                
            # if uris not specified, then return currently playing uri value.
            if (uris is None) or (len(uris.strip()) == 0):
                uris = self.GetPlayerNowPlayingUri(None)
                if uris is None:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'uris'), logsi=_logsi)

            # build a list of all item uri's.
            # remove any leading / trailing spaces in case user put a space between the items.
            arrUris:list[str] = uris.split(',')
            for idx in range(0, len(arrUris)):
                arrUris[idx] = arrUris[idx].strip()
                
            # build tracks dictionary.
            tracks:list[dict] = []
            for idx in range(0, len(arrUris)):
                tracks.append({'uri': '%s' % arrUris[idx]})
                
            # build spotify web api request parameters.
            reqData:dict = \
            {
                'tracks': tracks
            }
            if snapshotId is not None:
                reqData['snapshot_id'] = snapshotId
                
            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/playlists/{playlist_id}/tracks'.format(playlist_id=playlistId))
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.RequestJson = reqData
            self.MakeRequest('DELETE', msg)

            # process results.
            result = msg.ResponseData.get('snapshot_id','unknown')
        
            # trace.
            _logsi.LogString(SILevel.Verbose, TRACE_METHOD_RESULT % apiMethodName, result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def RemoveShowFavorites(
        self, 
        ids:str=None,
        ) -> None:
        """
        Remove one or more shows from the current user's 'Your Library'.
        
        This method requires the `user-library-modify` scope.
        
        Args:
            ids (str):  
                A comma-separated list of the Spotify IDs for the shows.  
                Maximum: 50 IDs.  
                Example: `6kAsbP8pxwaU2kPibKTuHE,4rOoJ6Egrf8K2IrywzwOMk`
                If null, the currently playing show uri id value is used.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.
                
        No error will be raised if a show id in the list does not exist in the 
        user's 'Your Library'.
        
        An SpotifyWebApiError will be raised if a specified album id does not exist
        in the Spotify music catalog.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/RemoveShowFavorites.py
        ```
        </details>
        """
        apiMethodName:str = 'RemoveShowFavorites'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            _logsi.LogMethodParmList(SILevel.Verbose, "Remove show(s) from user favorites", apiMethodParms)
                
            # if ids not specified, then return currently playing id value.
            if (ids is None) or (len(ids.strip()) == 0):
                uri = self.GetPlayerNowPlayingShowUri()
                if uri is not None:
                    ids = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'ids'), logsi=_logsi)

            # remove any leading / trailing spaces in case user put a space between the items.
            if (ids is not None):
                ids = ids.replace(" ","")
                
            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'ids': ids
            }

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/shows')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('DELETE', msg)
            
            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def RemoveTrackFavorites(
        self, 
        ids:str=None
        ) -> None:
        """
        Remove one or more tracks from the current user's 'Your Library'.
        
        This method requires the `user-library-modify` scope.
        
        Args:
            ids (str):  
                A comma-separated list of the Spotify IDs for the tracks.  
                Maximum: 50 IDs.  
                Example: `1kWUud3vY5ij5r62zxpTRy,4eoYKv2kDwJS7gRGh5q6SK`
                If null, the currently playing track uri id value is used.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.
                
        No error will be raised if a track id in the list does not exist in the 
        user's 'Your Library'.
        
        An SpotifyWebApiError will be raised if a specified album id does not exist
        in the Spotify music catalog.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/RemoveTrackFavorites.py
        ```
        </details>
        """
        apiMethodName:str = 'RemoveTrackFavorites'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            _logsi.LogMethodParmList(SILevel.Verbose, "Remove track(s) from user favorites", apiMethodParms)
                
            # if ids not specified, then return currently playing id value.
            if (ids is None) or (len(ids.strip()) == 0):
                uri = self.GetPlayerNowPlayingUri(SpotifyMediaTypes.TRACK.value)
                if uri is not None:
                    ids = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'ids'), logsi=_logsi)

            # build a list of all item id's.
            # remove any leading / trailing spaces in case user put a space between the items.
            arrIds:list[str] = ids.split(',')
            for idx in range(0, len(arrIds)):
                arrIds[idx] = arrIds[idx].strip()
                
            # build spotify web api request parameters.
            reqData:dict = \
            {
                'ids': arrIds
            }

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/tracks')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.RequestJson = reqData
            self.MakeRequest('DELETE', msg)
            
            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def ReorderPlaylistItems(
        self, 
        playlistId:str, 
        rangeStart:int,
        insertBefore:int,
        rangeLength:int=1,
        snapshotId:str=None
        ) -> str:
        """
        Reorder items in a user's playlist.
        
        This method requires the `playlist-modify-public` and `playlist-modify-private` scope.
        
        Args:
        
            playlistId (str):  
                The Spotify ID of the playlist.
                Example: `5AC9ZXA7nJ7oGWO911FuDG`
            rangeStart (int):
                The position of the first item to be reordered.  
                This is a one-offset integer (NOT zero-offset).
            insertBefore (int):
                The position where the items should be inserted.
                To reorder the items to the end of the playlist, simply set `insertBefore` 
                to the position after the last item.  
                This is a one-offset integer (NOT zero-offset).
            rangeLength (int):
                The amount of items to be reordered; defaults to 1 if not set.  
                The range of items to be reordered begins from the `rangeStart` position, and includes 
                the `rangeLength` subsequent items.  
            snapshotId (str):  
                The playlist's snapshot ID against which you want to make the changes.  
                If null, the current playlist is updated.  
                Example: `MTk3LGEzMjUwZGYwODljNmI5ZjAxZTRjZThiOGI4NzZhM2U5M2IxOWUyMDQ`
                Default is null.
                
        Returns:
            A snapshot ID for the updated playlist.
            
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        The `rangeStart` and `insertBefore` arguments are one-offset values; the underlying Spotify
        Web API utilizes zero-based offsets for these values.  The one-offset values make it much 
        easier (IMHO) to compare the results with the Spotify Web UI, which uses a one-offset track 
        numbering scheme (e.g. the first track is #1, then #2, etc).  See the examples below for
        the various ways to reorder tracks.
                
        The `snapshotId` argument value will be returned if no items were reordered; otherwise, a
        new snapshot id value will be returned.
        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/ReorderPlaylistItems.py
        ```
        </details>
        """
        apiMethodName:str = 'ReorderPlaylistItems'
        apiMethodParms:SIMethodParmListContext = None
        result:str = None
        
        try:

            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("playlistId", playlistId)
            apiMethodParms.AppendKeyValue("rangeStart", rangeStart)
            apiMethodParms.AppendKeyValue("insertBefore", insertBefore)
            apiMethodParms.AppendKeyValue("rangeLength", rangeLength)
            apiMethodParms.AppendKeyValue("snapshotId", snapshotId)
            _logsi.LogMethodParmList(SILevel.Verbose, "Reorder items in a user's playlist", apiMethodParms)

            # validations.
            if (rangeStart is None):
                rangeStart = 1
            if (insertBefore is None):
                insertBefore = 1
            if (rangeLength is None):
                rangeLength = 1
                
            # build spotify web api request parameters.
            reqData:dict = \
            {
                'range_start': rangeStart - 1,      # account for api zero-offset position
                'insert_before': insertBefore - 1,  # account for api zero-offset position
                'range_length': rangeLength
            }
            if snapshotId is not None:
                reqData['snapshot_id'] = snapshotId
                
            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/playlists/{playlist_id}/tracks'.format(playlist_id=playlistId))
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.RequestJson = reqData
            self.MakeRequest('PUT', msg)

            # process results.
            result = msg.ResponseData.get('snapshot_id','unknown')
        
            # trace.
            _logsi.LogString(SILevel.Verbose, TRACE_METHOD_RESULT % apiMethodName, result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def ReplacePlaylistItems(
        self, 
        playlistId:str, 
        uris:str=None,
        ) -> str:
        """
        Replace one or more items in a user's playlist. Replacing items in a playlist will 
        overwrite its existing items. 
        
        This method can also be used to clear a playlist.
        
        This method requires the `playlist-modify-public` and `playlist-modify-private` scope.
        
        Args:
        
            playlistId (str):  
                The Spotify ID of the playlist.
                Example: `5AC9ZXA7nJ7oGWO911FuDG`
            uris (str):  
                A comma-separated list of Spotify URIs to replace; can be track or episode URIs.  
                Example: `spotify:track:4iV5W9uYEdYUVa79Axb7Rh,spotify:episode:26c0zVyOv1lzfYpBXdh1zC`.  
                A maximum of 100 items can be specified in one request.
                
        Returns:
            A snapshot ID for the updated playlist.
            
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/ReplacePlaylistItems.py
        ```
        </details>
        """
        apiMethodName:str = 'ReplacePlaylistItems'
        apiMethodParms:SIMethodParmListContext = None
        result:str = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("playlistId", playlistId)
            apiMethodParms.AppendKeyValue("uris", uris)
            _logsi.LogMethodParmList(SILevel.Verbose, "Replace one or more items in a user's playlist", apiMethodParms)
            
            # validations.
            if (uris is None):
                uris = ""
            uris = uris.strip();
                
            # build a list of all item uri's.
            # remove any leading / trailing spaces in case user put a space between the items.
            arrUris:list[str] = uris.split(',')
            for idx in range(0, len(arrUris)):
                arrUris[idx] = arrUris[idx].strip()
                
            # if no items are present, then clear the array (can't have empty string items).
            if (len(arrUris) == 1) and (arrUris[0] == ""):
                arrUris = []

            # build spotify web api request parameters.
            reqData:dict = \
            {
                'uris': arrUris
            }
                
            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/playlists/{playlist_id}/tracks'.format(playlist_id=playlistId))
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.RequestJson = reqData
            self.MakeRequest('PUT', msg)

            # process results.
            result = msg.ResponseData.get('snapshot_id','unknown')
        
            # trace.
            _logsi.LogString(SILevel.Verbose, TRACE_METHOD_RESULT % apiMethodName, result)
            return result

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def SaveAlbumFavorites(
        self, 
        ids:str=None
        ) -> None:
        """
        Save one or more albums to the current user's 'Your Library'.
        
        This method requires the `user-library-modify` scope.
        
        Args:
            ids (str):  
                A comma-separated list of the Spotify IDs for the albums.  
                Maximum: 50 IDs.  
                Example: `6vc9OTcyd3hyzabCmsdnwE,382ObEPsp2rxGrnsizN5TX,2noRn2Aes5aoNVsU6iWThc`
                If null, the currently playing track album uri id value is used.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.
                
        No error will be raised if an album id in the list already exists in the 
        user's 'Your Library'.
        
        An SpotifyWebApiError will be raised if a specified album id does not exist
        in the Spotify music catalog.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/SaveAlbumFavorites.py
        ```
        </details>
        """
        apiMethodName:str = 'SaveAlbumFavorites'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            _logsi.LogMethodParmList(SILevel.Verbose, "Save album(s) to user favorites", apiMethodParms)
                
            # if ids not specified, then return currently playing album id value.
            if (ids is None) or (len(ids.strip()) == 0):
                uri = self.GetPlayerNowPlayingAlbumUri()
                if uri is not None:
                    ids = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'ids'), logsi=_logsi)

            # build a list of all item id's.
            # remove any leading / trailing spaces in case user put a space between the items.
            arrIds:list[str] = ids.split(',')
            for idx in range(0, len(arrIds)):
                arrIds[idx] = arrIds[idx].strip()
                
            # build spotify web api request parameters.
            reqData:dict = \
            {
                'ids': arrIds
            }

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/albums')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.RequestJson = reqData
            self.MakeRequest('PUT', msg)
            
            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def SaveAudiobookFavorites(
        self, 
        ids:str=None,
        ) -> None:
        """
        Save one or more audiobooks to the current user's 'Your Library'.
        
        This method requires the `user-library-modify` scope.
        
        Args:
            ids (str):  
                A comma-separated list of the Spotify IDs for the audiobooks.  
                Maximum: 50 IDs.  
                Example: `3PFyizE2tGCSRLusl2Qizf,7iHfbu1YPACw6oZPAFJtqe`
                If null, the currently playing audiobook uri id value is used.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.
                
        No error will be raised if an audiobook id in the list already exists in the 
        user's 'Your Library'.
        
        An SpotifyWebApiError will be raised if a specified album id does not exist
        in the Spotify music catalog.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/SaveAudiobookFavorites.py
        ```
        </details>
        """
        apiMethodName:str = 'SaveAudiobookFavorites'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            _logsi.LogMethodParmList(SILevel.Verbose, "Save audiobook(s) to user favorites", apiMethodParms)
                
            # if ids not specified, then return currently playing id value.
            if (ids is None) or (len(ids.strip()) == 0):
                uri = self.GetPlayerNowPlayingAudiobookUri()
                if uri is not None:
                    ids = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'ids'), logsi=_logsi)

            # build a list of all item id's.
            # remove any leading / trailing spaces in case user put a space between the items.
            arrIds:list[str] = ids.split(',')
            for idx in range(0, len(arrIds)):
                arrIds[idx] = arrIds[idx].strip()
                
            # build spotify web api request parameters.
            reqData:dict = \
            {
                'ids': arrIds
            }

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/audiobooks')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.RequestJson = reqData
            self.MakeRequest('PUT', msg)
            
            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def SaveEpisodeFavorites(
        self, 
        ids:str=None,
        ) -> None:
        """
        Save one or more episodes to the current user's 'Your Library'.
        
        This method requires the `user-library-modify` scope.
        
        Args:
            ids (str):  
                A comma-separated list of the Spotify IDs for the episodes.  
                Maximum: 50 IDs.  
                Example: `6kAsbP8pxwaU2kPibKTuHE,4rOoJ6Egrf8K2IrywzwOMk`
                If null, the currently playing episode uri id value is used.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.
                
        No error will be raised if an episode id in the list already exists in the 
        user's 'Your Library'.
        
        An SpotifyWebApiError will be raised if a specified album id does not exist
        in the Spotify music catalog.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/SaveEpisodeFavorites.py
        ```
        </details>
        """
        apiMethodName:str = 'SaveEpisodeFavorites'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            _logsi.LogMethodParmList(SILevel.Verbose, "Save episode(s) to user favorites", apiMethodParms)
                
            # if ids not specified, then return currently playing id value.
            if (ids is None) or (len(ids.strip()) == 0):
                uri = self.GetPlayerNowPlayingUri(SpotifyMediaTypes.EPISODE.value)
                if uri is not None:
                    ids = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'ids'), logsi=_logsi)

            # build a list of all item id's.
            # remove any leading / trailing spaces in case user put a space between the items.
            arrIds:list[str] = ids.split(',')
            for idx in range(0, len(arrIds)):
                arrIds[idx] = arrIds[idx].strip()
                
            # build spotify web api request parameters.
            reqData:dict = \
            {
                'ids': arrIds
            }

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/episodes')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.RequestJson = reqData
            self.MakeRequest('PUT', msg)
            
            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def SaveShowFavorites(
        self, 
        ids:str=None,
        ) -> None:
        """
        Save one or more shows to the current user's 'Your Library'.
        
        This method requires the `user-library-modify` scope.
        
        Args:
            ids (str):  
                A comma-separated list of the Spotify IDs for the shows.  
                Maximum: 50 IDs.  
                Example: `6kAsbP8pxwaU2kPibKTuHE,4rOoJ6Egrf8K2IrywzwOMk`
                If null, the currently playing show uri id value is used.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.
                
        No error will be raised if an show id in the list already exists in the 
        user's 'Your Library'.
        
        An SpotifyWebApiError will be raised if a specified album id does not exist
        in the Spotify music catalog.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/SaveShowFavorites.py
        ```
        </details>
        """
        apiMethodName:str = 'SaveShowFavorites'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            _logsi.LogMethodParmList(SILevel.Verbose, "Save show(s) to user favorites", apiMethodParms)
                
            # if ids not specified, then return currently playing id value.
            if (ids is None) or (len(ids.strip()) == 0):
                uri = self.GetPlayerNowPlayingShowUri()
                if uri is not None:
                    ids = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'ids'), logsi=_logsi)

            # remove any leading / trailing spaces in case user put a space between the items.
            if (ids is not None):
                ids = ids.replace(" ","")
                
            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'ids': ids
            }

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/shows')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.UrlParameters = urlParms
            self.MakeRequest('PUT', msg)
            
            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def SaveTrackFavorites(
        self, 
        ids:str=None
        ) -> None:
        """
        Save one or more tracks to the current user's 'Your Library'.
        
        This method requires the `user-library-modify` scope.
        
        Args:
            ids (str):  
                A comma-separated list of the Spotify IDs for the tracks.  
                Maximum: 50 IDs.  
                Example: `6vc9OTcyd3hyzabCmsdnwE,382ObEPsp2rxGrnsizN5TX,2noRn2Aes5aoNVsU6iWThc`
                If null, the currently playing track uri id value is used.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.
                
        No error will be raised if a track id in the list already exists in the 
        user's 'Your Library'.
        
        An SpotifyWebApiError will be raised if a specified album id does not exist
        in the Spotify music catalog.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/SaveTrackFavorites.py
        ```
        </details>
        """
        apiMethodName:str = 'SaveTrackFavorites'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            _logsi.LogMethodParmList(SILevel.Verbose, "Save track(s) to user favorites", apiMethodParms)
                
            # if ids not specified, then return currently playing id value.
            if (ids is None) or (len(ids.strip()) == 0):
                uri = self.GetPlayerNowPlayingUri(SpotifyMediaTypes.TRACK.value)
                if uri is not None:
                    ids = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'ids'), logsi=_logsi)

            # build a list of all item id's.
            # remove any leading / trailing spaces in case user put a space between the items.
            arrIds:list[str] = ids.split(',')
            for idx in range(0, len(arrIds)):
                arrIds[idx] = arrIds[idx].strip()
                
            # build spotify web api request parameters.
            reqData:dict = \
            {
                'ids': arrIds
            }

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/tracks')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.RequestJson = reqData
            self.MakeRequest('PUT', msg)
            
            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def Search(
        self, 
        criteria:str,
        criteriaType:str=None,
        market:str=None,
        includeExternal:str=None,
        limitTotal:int=None
        ) -> SearchResponse:
        """
        Get Spotify catalog information about albums, artists, playlists, tracks, shows, episodes 
        or audiobooks that match a keyword string. Audiobooks are only available within the US, UK, 
        Canada, Ireland, New Zealand and Australia markets.
        
        Args:
            criteria (str):
                Your search query.  
                You can narrow down your search using field filters.  
                The available filters are album, artist, track, year, upc, tag:hipster, tag:new, 
                isrc, and genre. Each field filter only applies to certain result types.  
                The artist and year filters can be used while searching albums, artists and tracks.
                You can filter on a single year or a range (e.g. 1955-1960).  
                The album filter can be used while searching albums and tracks.  
                The genre filter can be used while searching artists and tracks.  
                The isrc and track filters can be used while searching tracks.  
                The upc, tag:new and tag:hipster filters can only be used while searching albums. 
                The tag:new filter will return albums released in the past two weeks and tag:hipster 
                can be used to return only albums with the lowest 10% popularity.
            criteriaType (str):
                A comma-separated list of item types to search across.  
                Search results include hits from all the specified item types.  
                For example: "album,track" returns both albums and tracks matching criteria argument.  
                Allowed values: "album", "artist", "playlist", "track", "show", "episode", "audiobook".
                Default: "track"
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
            includeExternal (str):
                If "audio" is specified it signals that the client can play externally hosted audio content, and 
                marks the content as playable in the response. By default externally hosted audio content is marked 
                as unplayable in the response.  
                Allowed values: "audio"
            limitTotal (int):
                The maximum number of items to return for the request, per criteria type.
                Paging is automatically used to retrieve all available items up to the
                maximum number specified per type.
                Default: 20
                
        Returns:
            A `SearchResponse` object that contains the search results.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        Note that limit and offset arguments are not supplied to this method, as limitTotal is
        used instead.  Use the individual search type methods if you want to employ pagination
        techniques for searching.

        </details>
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/Search_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'Search'
        apiMethodParms:SIMethodParmListContext = None
        result:SearchResponse = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("criteria", criteria)
            apiMethodParms.AppendKeyValue("criteriaType", criteriaType)
            apiMethodParms.AppendKeyValue("market", market)
            apiMethodParms.AppendKeyValue("includeExternal", includeExternal)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            _logsi.LogMethodParmList(SILevel.Verbose, "Searching Spotify catalog for all information.", apiMethodParms)
                
            # validations.
            if criteriaType is None: 
                criteriaType = SpotifyMediaTypes.TRACK.value
            if isinstance(criteriaType, str):
                criteriaType = criteriaType.lower()
            if isinstance(criteriaType, SpotifyMediaTypes):
                criteriaType = SpotifyMediaTypes.value
            if limitTotal is None: 
                limitTotal = 20
            if not isinstance(limitTotal, int):
                limitTotal = 20
                
            # are we auto-paging?  if so, then use max limit.
            limit:int = 50
            if limit > limitTotal:
                limit = limitTotal

            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market)

            # initialize search response objects.
            searchResponse:SearchResponse = None
            searchResponseAll:SearchResponse = SearchResponse(criteria, criteriaType)

            # rather than calling the Spotify Web API `/search` entry point with ALL criteria
            # types, we will call the search subtypes individually so that we handle pagination
            # more easily per type; combine the individual results as we go.

            if (criteriaType.find(SpotifyMediaTypes.ALBUM) > -1):
                searchResponse = self.SearchAlbums(criteria, limit=limit, market=market, includeExternal=includeExternal, limitTotal=limitTotal)
                searchResponseAll.Albums = searchResponse.Albums

            if (criteriaType.find(SpotifyMediaTypes.ARTIST) > -1):
                searchResponse = self.SearchArtists(criteria, limit=limit, market=market, includeExternal=includeExternal, limitTotal=limitTotal)
                searchResponseAll.Artists = searchResponse.Artists

            if (criteriaType.find(SpotifyMediaTypes.AUDIOBOOK) > -1):
                searchResponse = self.SearchAudiobooks(criteria, limit=limit, market=market, includeExternal=includeExternal, limitTotal=limitTotal)
                searchResponseAll.Audiobooks = searchResponse.Audiobooks

            if (criteriaType.find(SpotifyMediaTypes.EPISODE) > -1):
                searchResponse = self.SearchEpisodes(criteria, limit=limit, market=market, includeExternal=includeExternal, limitTotal=limitTotal)
                searchResponseAll.Episodes = searchResponse.Episodes

            if (criteriaType.find(SpotifyMediaTypes.PLAYLIST) > -1):
                searchResponse = self.SearchPlaylists(criteria, limit=limit, market=market, includeExternal=includeExternal, limitTotal=limitTotal)
                searchResponseAll.Playlists = searchResponse.Playlists

            if (criteriaType.find(SpotifyMediaTypes.SHOW) > -1):
                searchResponse = self.SearchShows(criteria, limit=limit, market=market, includeExternal=includeExternal, limitTotal=limitTotal)
                searchResponseAll.Shows = searchResponse.Shows

            if (criteriaType.find(SpotifyMediaTypes.TRACK) > -1):
                searchResponse = self.SearchTracks(criteria, limit=limit, market=market, includeExternal=includeExternal, limitTotal=limitTotal)
                searchResponseAll.Tracks = searchResponse.Tracks

            # do not sort, as spotify uses intelligent AI to return results in its order.

            # trace.
            _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE + criteriaType) % (apiMethodName, type(searchResponseAll).__name__), searchResponseAll, excludeNonPublic=True)
            
            # return a search response object.
            return searchResponseAll

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def SearchAlbums(
        self, 
        criteria:str,
        limit:int=20, 
        offset:int=0,
        market:str=None,
        includeExternal:str=None,
        limitTotal:int=None
        ) -> SearchResponse:
        """
        Get Spotify catalog information about Albums that match a keyword string. 
        
        Args:
            criteria (str):
                Your search query.  
                You can narrow down your search using field filters.  
                The available filters are album, artist, track, year, upc, tag:hipster, tag:new, 
                isrc, and genre. Each field filter only applies to certain result types.  
                The artist and year filters can be used while searching albums, artists and tracks.
                You can filter on a single year or a range (e.g. 1955-1960).  
                The album filter can be used while searching albums and tracks.  
                The genre filter can be used while searching artists and tracks.  
                The isrc and track filters can be used while searching tracks.  
                The upc, tag:new and tag:hipster filters can only be used while searching albums. 
                The tag:new filter will return albums released in the past two weeks and tag:hipster 
                can be used to return only albums with the lowest 10% popularity.
            limit (int):
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            offset (int):
                The page index offset of the first item to return.  
                Use with limit to get the next set of items.  
                Default: 0 (the first item).  Range: 0 to 1000.  
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
            includeExternal (str):
                If "audio" is specified it signals that the client can play externally hosted audio content, and 
                marks the content as playable in the response. By default externally hosted audio content is marked 
                as unplayable in the response.  
                Allowed values: "audio"
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
                
        Returns:
            A `SearchResponse` object that contains the search results.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        Note that Spotify Web API automatically limits you to 1,000 max entries per type that can
        be returned with a search.
        
        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/SearchAlbums.py
        ```
        </details>
        <details>
          <summary>Sample Code - Auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/SearchAlbums_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'SearchAlbums'
        apiMethodParms:SIMethodParmListContext = None
        criteriaType:str = SpotifyMediaTypes.ALBUM.value
        result:AlbumPageSimplified = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("criteria", criteria)
            apiMethodParms.AppendKeyValue("criteriaType", criteriaType)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("offset", offset)
            apiMethodParms.AppendKeyValue("market", market)
            apiMethodParms.AppendKeyValue("includeExternal", includeExternal)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            _logsi.LogMethodParmList(SILevel.Verbose, "Searching Spotify catalog for %s information" % criteriaType, apiMethodParms)
                
            # validations.
            if limit is None: 
                limit = 20
            if offset is None: 
                offset = 0
            if not isinstance(limitTotal, int):
                limitTotal = 0
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = AlbumPageSimplified()

            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'q': criteria,
                'type': criteriaType,
                'limit': limit,
                'offset': offset,
            }
            if market is not None:
                urlParms['market'] = market
            if includeExternal is not None:
                urlParms['include_external'] = includeExternal
                
            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/search')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                searchResponse:SearchResponse = SearchResponse(criteria, criteriaType, root=msg.ResponseData)
                pageObj = searchResponse.Albums
            
                # trace.
                _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:AlbumSimplified
                    for item in pageObj.Items:
                        result.Items.append(item)
                        result.Limit = result.ItemsCount
                        if result.ItemsCount >= limitTotal:
                            break
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithOffset(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break

            # update result object with final paging details.
            result.Total = pageObj.Total
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # do not sort, as spotify uses intelligent AI to return results in its order.

            # trace.
            _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE + result.PagingInfo) % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            
            # return a search response object.
            response:SearchResponse = SearchResponse(criteria, criteriaType)
            response.Albums = result
            return response

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def SearchArtists(
        self, 
        criteria:str,
        limit:int=20, 
        offset:int=0,
        market:str=None,
        includeExternal:str=None,
        limitTotal:int=None
        ) -> SearchResponse:
        """
        Get Spotify catalog information about Artists that match a keyword string. 
        
        Args:
            criteria (str):
                Your search query.  
                You can narrow down your search using field filters.  
                The available filters are album, artist, track, year, upc, tag:hipster, tag:new, 
                isrc, and genre. Each field filter only applies to certain result types.  
                The artist and year filters can be used while searching albums, artists and tracks.
                You can filter on a single year or a range (e.g. 1955-1960).  
                The album filter can be used while searching albums and tracks.  
                The genre filter can be used while searching artists and tracks.  
                The isrc and track filters can be used while searching tracks.  
                The upc, tag:new and tag:hipster filters can only be used while searching albums. 
                The tag:new filter will return albums released in the past two weeks and tag:hipster 
                can be used to return only albums with the lowest 10% popularity.
            limit (int):
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            offset (int):
                The page index offset of the first item to return.  
                Use with limit to get the next set of items.  
                Default: 0 (the first item).  Range: 0 to 1000.  
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
            includeExternal (str):
                If "audio" is specified it signals that the client can play externally hosted audio content, and 
                marks the content as playable in the response. By default externally hosted audio content is marked 
                as unplayable in the response.  
                Allowed values: "audio"
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
                
        Returns:
            A `SearchResponse` object that contains the search results.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        Note that Spotify Web API automatically limits you to 1,000 max entries per type that can
        be returned with a search.
        
        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/SearchArtists.py
        ```
        </details>
        <details>
          <summary>Sample Code - Auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/SearchArtists_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'SearchArtists'
        apiMethodParms:SIMethodParmListContext = None
        criteriaType:str = SpotifyMediaTypes.ARTIST.value
        result:ArtistPage = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("criteria", criteria)
            apiMethodParms.AppendKeyValue("criteriaType", criteriaType)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("offset", offset)
            apiMethodParms.AppendKeyValue("market", market)
            apiMethodParms.AppendKeyValue("includeExternal", includeExternal)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            _logsi.LogMethodParmList(SILevel.Verbose, "Searching Spotify catalog for %s information" % criteriaType, apiMethodParms)
                
            # validations.
            if limit is None: 
                limit = 20
            if offset is None: 
                offset = 0
            if not isinstance(limitTotal, int):
                limitTotal = 0
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = ArtistPage()

            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'q': criteria,
                'type': criteriaType,
                'limit': limit,
                'offset': offset,
            }
            if market is not None:
                urlParms['market'] = market
            if includeExternal is not None:
                urlParms['include_external'] = includeExternal
                
            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/search')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                searchResponse:SearchResponse = SearchResponse(criteria, criteriaType, root=msg.ResponseData)
                pageObj = searchResponse.Artists
            
                # trace.
                _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:Artist
                    for item in pageObj.Items:
                        result.Items.append(item)
                        result.Limit = result.ItemsCount
                        if result.ItemsCount >= limitTotal:
                            break
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithOffset(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break

            # update result object with final paging details.
            result.Total = pageObj.Total
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # do not sort, as spotify uses intelligent AI to return results in its order.

            # trace.
            _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE + result.PagingInfo) % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            
            # return a search response object.
            response:SearchResponse = SearchResponse(criteria, criteriaType)
            response.Artists = result
            return response

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def SearchAudiobooks(
        self, 
        criteria:str,
        limit:int=20, 
        offset:int=0,
        market:str=None,
        includeExternal:str=None,
        limitTotal:int=None
        ) -> SearchResponse:
        """
        Get Spotify catalog information about Audiobooks that match a keyword string. 
        
        Args:
            criteria (str):
                Your search query.  
                You can narrow down your search using field filters.  
                The available filters are album, artist, track, year, upc, tag:hipster, tag:new, 
                isrc, and genre. Each field filter only applies to certain result types.  
                The artist and year filters can be used while searching albums, artists and tracks.
                You can filter on a single year or a range (e.g. 1955-1960).  
                The album filter can be used while searching albums and tracks.  
                The genre filter can be used while searching artists and tracks.  
                The isrc and track filters can be used while searching tracks.  
                The upc, tag:new and tag:hipster filters can only be used while searching albums. 
                The tag:new filter will return albums released in the past two weeks and tag:hipster 
                can be used to return only albums with the lowest 10% popularity.
            limit (int):
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            offset (int):
                The page index offset of the first item to return.  
                Use with limit to get the next set of items.  
                Default: 0 (the first item).  Range: 0 to 1000.  
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
            includeExternal (str):
                If "audio" is specified it signals that the client can play externally hosted audio content, and 
                marks the content as playable in the response. By default externally hosted audio content is marked 
                as unplayable in the response.  
                Allowed values: "audio"
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
                
        Returns:
            A `SearchResponse` object that contains the search results.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        Audiobooks are only available within the US, UK, Canada, Ireland, New Zealand and Australia markets.
        
        Note that Spotify Web API automatically limits you to 1,000 max entries per type that can
        be returned with a search.
        
        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/SearchAudiobooks.py
        ```
        </details>
        <details>
          <summary>Sample Code - Auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/SearchAudiobooks_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'SearchAudiobooks'
        apiMethodParms:SIMethodParmListContext = None
        criteriaType:str = SpotifyMediaTypes.AUDIOBOOK.value
        result:AudiobookPageSimplified = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("criteria", criteria)
            apiMethodParms.AppendKeyValue("criteriaType", criteriaType)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("offset", offset)
            apiMethodParms.AppendKeyValue("market", market)
            apiMethodParms.AppendKeyValue("includeExternal", includeExternal)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            _logsi.LogMethodParmList(SILevel.Verbose, "Searching Spotify catalog for %s information" % criteriaType, apiMethodParms)
                
            # validations.
            if limit is None: 
                limit = 20
            if offset is None: 
                offset = 0
            if not isinstance(limitTotal, int):
                limitTotal = 0
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = AudiobookPageSimplified()

            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'q': criteria,
                'type': criteriaType,
                'limit': limit,
                'offset': offset,
            }
            if market is not None:
                urlParms['market'] = market
            if includeExternal is not None:
                urlParms['include_external'] = includeExternal
                
            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/search')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                searchResponse:SearchResponse = SearchResponse(criteria, criteriaType, root=msg.ResponseData)
                pageObj = searchResponse.Audiobooks
            
                # trace.
                _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:AudiobookSimplified
                    for item in pageObj.Items:
                        result.Items.append(item)
                        result.Limit = result.ItemsCount
                        if result.ItemsCount >= limitTotal:
                            break
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithOffset(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break

            # update result object with final paging details.
            result.Total = pageObj.Total
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # do not sort, as spotify uses intelligent AI to return results in its order.

            # trace.
            _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE + result.PagingInfo) % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            
            # return a search response object.
            response:SearchResponse = SearchResponse(criteria, criteriaType)
            response.Audiobooks = result
            return response

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def SearchEpisodes(
        self, 
        criteria:str,
        limit:int=20, 
        offset:int=0,
        market:str=None,
        includeExternal:str=None,
        limitTotal:int=None
        ) -> SearchResponse:
        """
        Get Spotify catalog information about Episodes that match a keyword string. 
        
        Args:
            criteria (str):
                Your search query.  
                You can narrow down your search using field filters.  
                The available filters are album, artist, track, year, upc, tag:hipster, tag:new, 
                isrc, and genre. Each field filter only applies to certain result types.  
                The artist and year filters can be used while searching albums, artists and tracks.
                You can filter on a single year or a range (e.g. 1955-1960).  
                The album filter can be used while searching albums and tracks.  
                The genre filter can be used while searching artists and tracks.  
                The isrc and track filters can be used while searching tracks.  
                The upc, tag:new and tag:hipster filters can only be used while searching albums. 
                The tag:new filter will return albums released in the past two weeks and tag:hipster 
                can be used to return only albums with the lowest 10% popularity.
            limit (int):
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            offset (int):
                The page index offset of the first item to return.  
                Use with limit to get the next set of items.  
                Default: 0 (the first item).  Range: 0 to 1000.  
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
            includeExternal (str):
                If "audio" is specified it signals that the client can play externally hosted audio content, and 
                marks the content as playable in the response. By default externally hosted audio content is marked 
                as unplayable in the response.  
                Allowed values: "audio"
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
                
        Returns:
            A `SearchResponse` object that contains the search results.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        Note that Spotify Web API automatically limits you to 1,000 max entries per type that can
        be returned with a search.
        
        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/SearchEpisodes.py
        ```
        </details>
        <details>
          <summary>Sample Code - Auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/SearchEpisodes_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'SearchEpisodes'
        apiMethodParms:SIMethodParmListContext = None
        criteriaType:str = SpotifyMediaTypes.EPISODE.value
        result:EpisodePageSimplified = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("criteria", criteria)
            apiMethodParms.AppendKeyValue("criteriaType", criteriaType)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("offset", offset)
            apiMethodParms.AppendKeyValue("market", market)
            apiMethodParms.AppendKeyValue("includeExternal", includeExternal)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            _logsi.LogMethodParmList(SILevel.Verbose, "Searching Spotify catalog for %s information" % criteriaType, apiMethodParms)
            
            # validations.
            if limit is None: 
                limit = 20
            if offset is None: 
                offset = 0
            if not isinstance(limitTotal, int):
                limitTotal = 0
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = EpisodePageSimplified()

            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'q': criteria,
                'type': criteriaType,
                'limit': limit,
                'offset': offset,
            }
            if market is not None:
                urlParms['market'] = market
            if includeExternal is not None:
                urlParms['include_external'] = includeExternal
                
            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/search')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                searchResponse:SearchResponse = SearchResponse(criteria, criteriaType, root=msg.ResponseData)
                pageObj = searchResponse.Episodes
            
                # trace.
                _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:EpisodeSimplified
                    for item in pageObj.Items:
                        result.Items.append(item)
                        result.Limit = result.ItemsCount
                        if result.ItemsCount >= limitTotal:
                            break
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithOffset(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break

            # update result object with final paging details.
            result.Total = pageObj.Total
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # do not sort, as spotify uses intelligent AI to return results in its order.

            # trace.
            _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE + result.PagingInfo) % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            
            # return a search response object.
            response:SearchResponse = SearchResponse(criteria, criteriaType)
            response.Episodes = result
            return response

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def SearchPlaylists(
        self, 
        criteria:str,
        limit:int=20, 
        offset:int=0,
        market:str=None,
        includeExternal:str=None,
        limitTotal:int=None,
        ) -> SearchResponse:
        """
        Get Spotify catalog information about Playlists that match a keyword string. 
        
        Args:
            criteria (str):
                Your search query.  
                You can narrow down your search using field filters.  
                The available filters are album, artist, track, year, upc, tag:hipster, tag:new, 
                isrc, and genre. Each field filter only applies to certain result types.  
                The artist and year filters can be used while searching albums, artists and tracks.
                You can filter on a single year or a range (e.g. 1955-1960).  
                The album filter can be used while searching albums and tracks.  
                The genre filter can be used while searching artists and tracks.  
                The isrc and track filters can be used while searching tracks.  
                The upc, tag:new and tag:hipster filters can only be used while searching albums. 
                The tag:new filter will return albums released in the past two weeks and tag:hipster 
                can be used to return only albums with the lowest 10% popularity.
            limit (int):
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            offset (int):
                The page index offset of the first item to return.  
                Use with limit to get the next set of items.  
                Default: 0 (the first item).  Range: 0 to 1000.  
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
            includeExternal (str):
                If "audio" is specified it signals that the client can play externally hosted audio content, and 
                marks the content as playable in the response. By default externally hosted audio content is marked 
                as unplayable in the response.  
                Allowed values: "audio"
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
                
        Returns:
            A `SearchResponse` object that contains the search results.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        Note that Spotify Web API automatically limits you to 1,000 max entries per type that can
        be returned with a search.
        
        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/SearchPlaylists.py
        ```
        </details>
        <details>
          <summary>Sample Code - Auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/SearchPlaylists_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'SearchPlaylists'
        apiMethodParms:SIMethodParmListContext = None
        criteriaType:str = SpotifyMediaTypes.PLAYLIST.value
        result:PlaylistPageSimplified = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("criteria", criteria)
            apiMethodParms.AppendKeyValue("criteriaType", criteriaType)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("offset", offset)
            apiMethodParms.AppendKeyValue("market", market)
            apiMethodParms.AppendKeyValue("includeExternal", includeExternal)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            _logsi.LogMethodParmList(SILevel.Verbose, "Searching Spotify catalog for %s information" % criteriaType, apiMethodParms)
                
            # validations.
            if limit is None: 
                limit = 20
            if offset is None: 
                offset = 0
            if not isinstance(limitTotal, int):
                limitTotal = 0
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = PlaylistPageSimplified()

            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'q': criteria,
                'type': criteriaType,
                'limit': limit,
                'offset': offset,
            }
            if market is not None:
                urlParms['market'] = market
            if includeExternal is not None:
                urlParms['include_external'] = includeExternal
                
            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/search')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                searchResponse:SearchResponse = SearchResponse(criteria, criteriaType, root=msg.ResponseData)
                pageObj = searchResponse.Playlists
            
                # trace.
                _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:PlaylistSimplified
                    for item in pageObj.Items:
                        result.Items.append(item)
                        result.Limit = result.ItemsCount
                        if result.ItemsCount >= limitTotal:
                            break
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithOffset(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break

            # update result object with final paging details.
            result.Total = pageObj.Total
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # do not sort, as spotify uses intelligent AI to return results in its order.

            # trace.
            _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE + result.PagingInfo) % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            
            # return a search response object.
            response:SearchResponse = SearchResponse(criteria, criteriaType)
            response.Playlists = result
            return response

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def SearchShows(
        self, 
        criteria:str,
        limit:int=20, 
        offset:int=0,
        market:str=None,
        includeExternal:str=None,
        limitTotal:int=None
        ) -> SearchResponse:
        """
        Get Spotify catalog information about Shows that match a keyword string. 
        
        Args:
            criteria (str):
                Your search query.  
                You can narrow down your search using field filters.  
                The available filters are album, artist, track, year, upc, tag:hipster, tag:new, 
                isrc, and genre. Each field filter only applies to certain result types.  
                The artist and year filters can be used while searching albums, artists and tracks.
                You can filter on a single year or a range (e.g. 1955-1960).  
                The album filter can be used while searching albums and tracks.  
                The genre filter can be used while searching artists and tracks.  
                The isrc and track filters can be used while searching tracks.  
                The upc, tag:new and tag:hipster filters can only be used while searching albums. 
                The tag:new filter will return albums released in the past two weeks and tag:hipster 
                can be used to return only albums with the lowest 10% popularity.
            limit (int):
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            offset (int):
                The page index offset of the first item to return.  
                Use with limit to get the next set of items.  
                Default: 0 (the first item).  Range: 0 to 1000.  
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
            includeExternal (str):
                If "audio" is specified it signals that the client can play externally hosted audio content, and 
                marks the content as playable in the response. By default externally hosted audio content is marked 
                as unplayable in the response.  
                Allowed values: "audio"
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
                
        Returns:
            A `SearchResponse` object that contains the search results.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        Note that Spotify Web API automatically limits you to 1,000 max entries per type that can
        be returned with a search.
        
        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/SearchShows.py
        ```
        </details>
        <details>
          <summary>Sample Code - Auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/SearchShows_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'SearchShows'
        apiMethodParms:SIMethodParmListContext = None
        criteriaType:str = SpotifyMediaTypes.SHOW.value
        result:ShowPageSimplified = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("criteria", criteria)
            apiMethodParms.AppendKeyValue("criteriaType", criteriaType)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("offset", offset)
            apiMethodParms.AppendKeyValue("market", market)
            apiMethodParms.AppendKeyValue("includeExternal", includeExternal)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            _logsi.LogMethodParmList(SILevel.Verbose, "Searching Spotify catalog for %s information" % criteriaType, apiMethodParms)
                
            # validations.
            if limit is None: 
                limit = 20
            if offset is None: 
                offset = 0
            if not isinstance(limitTotal, int):
                limitTotal = 0
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = ShowPageSimplified()

            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'q': criteria,
                'type': criteriaType,
                'limit': limit,
                'offset': offset,
            }
            if market is not None:
                urlParms['market'] = market
            if includeExternal is not None:
                urlParms['include_external'] = includeExternal
                
            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/search')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                searchResponse:SearchResponse = SearchResponse(criteria, criteriaType, root=msg.ResponseData)
                pageObj = searchResponse.Shows
            
                # trace.
                _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:ShowSimplified
                    for item in pageObj.Items:
                        result.Items.append(item)
                        result.Limit = result.ItemsCount
                        if result.ItemsCount >= limitTotal:
                            break
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithOffset(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break

            # update result object with final paging details.
            result.Total = pageObj.Total
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # do not sort, as spotify uses intelligent AI to return results in its order.

            # trace.
            _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE + result.PagingInfo) % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            
            # return a search response object.
            response:SearchResponse = SearchResponse(criteria, criteriaType)
            response.Shows = result
            return response

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def SearchTracks(
        self, 
        criteria:str,
        limit:int=20, 
        offset:int=0,
        market:str=None,
        includeExternal:str=None,
        limitTotal:int=None
        ) -> SearchResponse:
        """
        Get Spotify catalog information about Tracks that match a keyword string. 
        
        Args:
            criteria (str):
                Your search query.  
                You can narrow down your search using field filters.  
                The available filters are album, artist, track, year, upc, tag:hipster, tag:new, 
                isrc, and genre. Each field filter only applies to certain result types.  
                The artist and year filters can be used while searching albums, artists and tracks.
                You can filter on a single year or a range (e.g. 1955-1960).  
                The album filter can be used while searching albums and tracks.  
                The genre filter can be used while searching artists and tracks.  
                The isrc and track filters can be used while searching tracks.  
                The upc, tag:new and tag:hipster filters can only be used while searching albums. 
                The tag:new filter will return albums released in the past two weeks and tag:hipster 
                can be used to return only albums with the lowest 10% popularity.
            limit (int):
                The maximum number of items to return in a page of items when manual paging is used.  
                Default: 20, Range: 1 to 50.  
                See the `limitTotal` argument for automatic paging option.  
            offset (int):
                The page index offset of the first item to return.  
                Use with limit to get the next set of items.  
                Default: 0 (the first item).  Range: 0 to 1000.  
            market (str):
                An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that 
                is available in that market will be returned.  If a valid user access token is specified 
                in the request header, the country associated with the user account will take priority over 
                this parameter.  
                Note: If neither market or user country are provided, the content is considered unavailable for the client.  
                Users can view the country that is associated with their account in the account settings.  
                Example: `ES`
            includeExternal (str):
                If "audio" is specified it signals that the client can play externally hosted audio content, and 
                marks the content as playable in the response. By default externally hosted audio content is marked 
                as unplayable in the response.  
                Allowed values: "audio"
            limitTotal (int):
                The maximum number of items to return for the request.  
                If specified, this argument overrides the limit and offset argument values
                and paging is automatically used to retrieve all available items up to the
                maximum number specified.  
                Default: None (disabled)
                
        Returns:
            A `SearchResponse` object that contains the search results.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.

        Note that Spotify Web API automatically limits you to 1,000 max entries per type that can
        be returned with a search.
        
        <details>
          <summary>Sample Code - Manual Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/SearchTracks.py
        ```
        </details>
        <details>
          <summary>Sample Code - Auto Paging</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/SearchTracks_AutoPaging.py
        ```
        </details>
        """
        apiMethodName:str = 'SearchTracks'
        apiMethodParms:SIMethodParmListContext = None
        criteriaType:str = SpotifyMediaTypes.TRACK.value
        result:TrackPage = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("criteria", criteria)
            apiMethodParms.AppendKeyValue("criteriaType", criteriaType)
            apiMethodParms.AppendKeyValue("limit", limit)
            apiMethodParms.AppendKeyValue("offset", offset)
            apiMethodParms.AppendKeyValue("market", market)
            apiMethodParms.AppendKeyValue("includeExternal", includeExternal)
            apiMethodParms.AppendKeyValue("limitTotal", limitTotal)
            _logsi.LogMethodParmList(SILevel.Verbose, "Searching Spotify catalog for %s information" % criteriaType, apiMethodParms)
                
            # validations.
            if limit is None: 
                limit = 20
            if offset is None: 
                offset = 0
            if not isinstance(limitTotal, int):
                limitTotal = 0
                
            # are we auto-paging?  if so, then use max limit.
            if limitTotal > 0: 
                limit = 50
                if limit > limitTotal:
                    limit = limitTotal
                result = TrackPage()

            # ensure market was either supplied or implied; default if neither.
            market = self._ValidateMarket(market)

            # build spotify web api request parameters.
            urlParms:dict = \
            {
                'q': criteria,
                'type': criteriaType,
                'limit': limit,
                'offset': offset,
            }
            if market is not None:
                urlParms['market'] = market
            if includeExternal is not None:
                urlParms['include_external'] = includeExternal
                
            # handle pagination, as spotify limits us to a set # of items returned per response.
            while True:

                # execute spotify web api request.
                msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/search')
                msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
                msg.UrlParameters = urlParms
                self.MakeRequest('GET', msg)

                # process results.
                searchResponse:SearchResponse = SearchResponse(criteria, criteriaType, root=msg.ResponseData)
                pageObj = searchResponse.Tracks
            
                # trace.
                _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE_PAGE + pageObj.PagingInfo) % (apiMethodName, type(pageObj).__name__), pageObj, excludeNonPublic=True)

                # was limit total argument specified?
                if (limitTotal <= 0):
                
                    # no - just return the initial page of results.
                    result = pageObj
                    break

                else:
                
                    # append page of items to final results.
                    item:Track
                    for item in pageObj.Items:
                        result.Items.append(item)
                        result.Limit = result.ItemsCount
                        if result.ItemsCount >= limitTotal:
                            break
                    
                    # anymore pages to process?  if not, then exit the loop.
                    if not self._CheckForNextPageWithOffset(pageObj, result.ItemsCount, limit, limitTotal, urlParms):
                        break

            # update result object with final paging details.
            result.Total = pageObj.Total
            result.DateLastRefreshed = datetime.utcnow().timestamp()

            # do not sort, as spotify uses intelligent AI to return results in its order.

            # trace.
            _logsi.LogObject(SILevel.Verbose, (TRACE_METHOD_RESULT_TYPE + result.PagingInfo) % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
            
            # return a search response object.
            response:SearchResponse = SearchResponse(criteria, criteriaType)
            response.Tracks = result
            return response

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def SetAuthTokenAuthorizationCode(
        self, 
        clientId:str, 
        clientSecret:str, 
        scope:str=None, 
        tokenProfileId:str=None,
        forceAuthorize:bool=False,
        redirectUriHost:str='127.0.0.1', 
        redirectUriPort:int=8080,
        redirectUriPath:str='/',
        ) -> None:
        """
        Generates a new Authorization Code type of authorization token used to access 
        the Spotify Web API.
        
        Args:
            clientId (str):
                The unique identifier of the application.
            clientSecret (str):
                The client secret, which is the key you will use to authorize your Web API or SDK calls.
            scope (str | list[str]):
                A space-delimited list of scope identifiers you wish to request access to.  
                If no scope is specified, authorization will be granted only to access publicly 
                available information; that is, only information normally visible in the Spotify 
                desktop, web, and mobile players.  
                Default is None.
            tokenProfileId (str):
                Profile identifier used when loading / storing the token to disk.  
                A null value will default to `Shared`.  
                Default: `Shared`               
            forceAuthorize (bool):
                True to force authorization, even if we already have a token.  
                This can be useful if dynamically changing scope.  
                Default is False.
            redirectUriHost (str):
                The value to use for the host portion of the redirect URI.  
                Default is '127.0.0.1'.
            redirectUriPort (int):
                The value to use for the port portion of the redirect URI.  You can specify a
                single port as an integer, or a port range as a list (e.g. [8080,8090]).  If a 
                port range is specified, then the logic will loop through the port range looking
                for an available port to use.  
                Default is 8080.
            redirectUriPath (str):  
                Path value to add when constructing the redirect_uri; otherwise,
                None to not add a path value.  
                Default value is '/'.
                
        Raises:
            SpotifyApiError: 
                If the method fails for any reason.
                
        The authorization code flow is suitable for long-running applications (e.g. web and mobile 
        apps) where the user grants permission only once.  If you are using the authorization code 
        flow in a mobile app, or any other type of application where the client secret can't be safely 
        stored, then you should use the `SetAuthTokenAuthorizationCode` method. 

        This allows you to specify scope values, which allow more granular access to data that
        is not public (e.g. a user's email, playlist, profile, etc).  The user gets final approval
        for the requested scope(s) when they login to approve the access, as the login form will
        show what scope they are about to approve.  The user also has the ability to remove the
        application access at any time, in the event that the client is abusing the given scope
        privileges.
        
        The authorization flow will attempt to automatically open the Spotify authorization URL
        in a new browser tab (using the default browser).  This will force the user to login to
        Spotify, if not already logged in.  Spotify then displays to the user the requested access 
        (scope) that your application is requesting, and allows them to accept / reject it.
        The flow will start a local web server to listen for the user response to the authorization 
        request. Once authorization is complete, the Spotify authorization server will redirect the 
        user's browser to the local web server with the response. The web server will get the 
        authorization code from the response and shutdown. The authorization code is then exchanged 
        for a Spotify authorization token.

        Note that you must have 'http://127.0.0.1:8080/' in the Redirect URI allowlist that you 
        specified when you registered your application in the Spotify Developer Portal.  The
        redirect URI is case-sensitive, and must contain the trailing slash.  You will need to
        adjust the redirect URI value if you specify custom values using the `redirectUriHost`,
        `redirectUriPort`, and `redirectUriPath` arguments.
        """
        apiMethodName:str = 'SetAuthTokenAuthorizationCode'
        apiMethodParms:SIMethodParmListContext = None
        authorizationType:str = 'Authorization Code'
        
        try:

            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("clientId", clientId)
            apiMethodParms.AppendKeyValue("clientSecret", clientSecret)
            apiMethodParms.AppendKeyValue("scope", scope)
            apiMethodParms.AppendKeyValue("tokenProfileId", tokenProfileId)
            apiMethodParms.AppendKeyValue("forceAuthorize", forceAuthorize)
            apiMethodParms.AppendKeyValue("redirectUriHost", redirectUriHost)
            apiMethodParms.AppendKeyValue("redirectUriPort", redirectUriPort)
            apiMethodParms.AppendKeyValue("redirectUriPath", redirectUriPath)
            _logsi.LogMethodParmList(SILevel.Verbose, TRACE_MSG_AUTHTOKEN_CREATE % authorizationType, apiMethodParms)
                        
            # validation.
            if redirectUriHost is None or len(redirectUriHost.strip()) == 0:
                redirectUriHost = '127.0.0.1'
            if redirectUriPort is None:
                redirectUriPort = 8080
            if scope is not None:
                if (not isinstance(scope, list)) and (not isinstance(scope, str)):
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_TYPE_ERROR % (apiMethodName, 'scope', 'list', type(scope).__name__), logsi=_logsi)
            if (forceAuthorize is None):
                forceAuthorize = False

            # create oauth provider for spotify authentication code with pkce.
            self._AuthClient:AuthClient = AuthClient(
                authorizationType=authorizationType,
                authorizationUrl=self.SpotifyApiAuthorizeUrl,
                tokenUrl=self.SpotifyApiTokenUrl,
                scope=scope,
                clientId=clientId,
                clientSecret=clientSecret,
                oauth2Client=WebApplicationClient(client_id=clientId),  # required for grant_type = authorization_code
                tokenStorageDir=self._TokenStorageDir,
                tokenStorageFile=self._TokenStorageFile,
                tokenProviderId='SpotifyWebApiAuthCode',
                tokenProfileId=tokenProfileId,
                tokenUpdater=self._TokenUpdater
            )
           
            # force the user to logon to spotify to authorize the application access if we 
            # do not have an authorized access token, or if the calling application requested 
            # us (by force) to re-authorize, or if the scope has changed.
            isAuthorized = self._AuthClient.IsAuthorized
            _logsi.LogVerbose('Checking OAuth2 authorization status: IsAuthorized=%s, Force=%s' % (isAuthorized, forceAuthorize))

            if (isAuthorized == False) or (forceAuthorize == True):
                
                # at this point, we need a new authorization token.
                _logsi.LogVerbose('Preparing to retrieve a new OAuth2 authorization access token')
                self._AuthClient.AuthorizeWithServer(
                    host=redirectUriHost, 
                    port=redirectUriPort, 
                    redirect_uri_path=redirectUriPath,
                    open_browser=True, 
                    force=forceAuthorize,
                    timeout_seconds=120
                )
                
            else:
                
                _logsi.LogVerbose('OAuth2 authorization token is authorized')

            # process results.
            oauth2token:dict = self._AuthClient.Session.token
            self._AuthToken = SpotifyAuthToken(self._AuthClient.AuthorizationType, self._AuthClient.TokenProfileId, root=oauth2token)
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT % apiMethodName, self._AuthToken, excludeNonPublic=True)
            
            # does token need to be refreshed?
            if self._AuthToken.IsExpired:

                # refresh the token.  
                # this will also store the refreshed token to disk to be used later if required.
                _logsi.LogVerbose("OAuth2 authorization token has expired, or is about to; token will be refreshed")
                oauth2token:dict = self._AuthClient.RefreshToken()
                self._AuthToken = SpotifyAuthToken(self._AuthClient.AuthorizationType, self._AuthClient.TokenProfileId, root=oauth2token)
                _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT % apiMethodName, self._AuthToken, excludeNonPublic=True)
            
            else:
                
                _logsi.LogVerbose('OAuth2 authorization token has not expired')

            # retrieve spotify user basic details.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            self.MakeRequest('GET', msg)

            # process results.
            self._UserProfile = UserProfile(root=msg.ResponseData)

            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_MSG_USERPROFILE % (self._UserProfile.DisplayName, self._UserProfile.EMail), self._UserProfile, excludeNonPublic=True)

            # start / restart Zeroconf Directory task.
            self._RestartSpotifyConnectDirectoryTask()

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # trace.
            _logsi.LogException(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logToSystemLogger=False)
            raise

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def SetAuthTokenAuthorizationCodePKCE(
        self, 
        clientId:str, 
        scope:str=None, 
        tokenProfileId:str=None,
        forceAuthorize:bool=False,
        redirectUriHost:str='127.0.0.1', 
        redirectUriPort:int=8080, 
        redirectUriPath:str='/'
        ) -> None:
        """
        Generates a new Authorization Code PKCE type of authorization token used to access 
        the Spotify Web API.
        
        Args:
            clientId (str):
                The unique identifier of the application.
            scope (str | list[str]):
                A space-delimited list of scope identifiers you wish to request access to.  
                If no scope is specified, authorization will be granted only to access publicly 
                available information; that is, only information normally visible in the Spotify 
                desktop, web, and mobile players.  
                Default is None.
            tokenProfileId (str):
                Profile identifier used when loading / storing the token to disk.  
                A null value will default to `Shared`.  
                Default: `Shared`               
            forceAuthorize (bool):
                True to force authorization, even if we already have a token.  
                This can be useful if dynamically changing scope.  
                Default is False.
            redirectUriHost (str):
                The value to use for the host portion of the redirect URI.  
                Default is '127.0.0.1'.
            redirectUriPort (int):
                The value to use for the port portion of the redirect URI.  You can specify a
                single port as an integer, or a port range as a list (e.g. [8080,8090]).  If a 
                port range is specified, then the logic will loop through the port range looking
                for an available port to use.  
                Default is 8080.
            redirectUriPath (str):  
                Path value to add when constructing the redirect_uri; otherwise,
                None to not add a path value.  
                Default value is '/'.
                
        Raises:
            SpotifyApiError: 
                If the method fails for any reason.
                
        The authorization code with PKCE is the recommended authorization type if you are 
        implementing authorization in a mobile app, single page web app, or any other type of 
        application where the client secret can't be safely stored.
        
        This allows you to specify scope values, which allow more granular access to data that
        is not public (e.g. a user's email, playlist, profile, etc).  The user gets final approval
        for the requested scope(s) when they login to approve the access, as the login form will
        show what scope they are about to approve.  The user also has the ability to remove the
        application access at any time, in the event that the client is abusing the given scope
        privileges.
        
        The authorization flow will attempt to automatically open the Spotify authorization URL
        in a new browser tab (using the default browser).  This will force the user to login to
        Spotify, if not already logged in.  Spotify then displays to the user the requested access 
        (scope) that your application is requesting, and allows them to accept / reject it.
        The flow will start a local web server to listen for the user response to the authorization 
        request. Once authorization is complete, the Spotify authorization server will redirect the 
        user's browser to the local web server with the response. The web server will get the 
        authorization code from the response and shutdown. The authorization code is then exchanged 
        for a Spotify authorization token.

        Note that you must have 'http://127.0.0.1:8080/' in the Redirect URI allowlist that you 
        specified when you registered your application in the Spotify Developer Portal.  The
        redirect URI is case-sensitive, and must contain the trailing slash.  You will need to
        adjust the redirect URI value if you specify custom values using the `redirectUriHost`,
        `redirectUriPort`, and `redirectUriPath` arguments.
        """
        apiMethodName:str = 'SetAuthTokenAuthorizationCodePKCE'
        apiMethodParms:SIMethodParmListContext = None
        authorizationType:str = 'Authorization Code PKCE'
        
        try:

            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("clientId", clientId)
            apiMethodParms.AppendKeyValue("scope", scope)
            apiMethodParms.AppendKeyValue("tokenProfileId", tokenProfileId)
            apiMethodParms.AppendKeyValue("forceAuthorize", forceAuthorize)
            apiMethodParms.AppendKeyValue("redirectUriHost", redirectUriHost)
            apiMethodParms.AppendKeyValue("redirectUriPort", redirectUriPort)
            apiMethodParms.AppendKeyValue("redirectUriPath", redirectUriPath)
            _logsi.LogMethodParmList(SILevel.Verbose, TRACE_MSG_AUTHTOKEN_CREATE % authorizationType, apiMethodParms)
                
            # validation.
            if redirectUriHost is None or len(redirectUriHost.strip()) == 0:
                redirectUriHost = '127.0.0.1'
            if redirectUriPort is None:
                redirectUriPort = 8080
            if scope is not None:
                if (not isinstance(scope, list)) and (not isinstance(scope, str)):
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_TYPE_ERROR % (apiMethodName, 'scope', 'list', type(scope).__name__), logsi=_logsi)
            if (forceAuthorize is None):
                forceAuthorize = False

            # create oauth provider for spotify authentication code with pkce.
            self._AuthClient:AuthClient = AuthClient(
                authorizationType=authorizationType,
                authorizationUrl=self.SpotifyApiAuthorizeUrl,
                tokenUrl=self.SpotifyApiTokenUrl,
                scope=scope,
                clientId=clientId,
                clientSecret=None,  # client_secret not used for authorization code with pkce type
                oauth2Client=WebApplicationClient(client_id=clientId),  # required for grant_type = authorization_code
                tokenStorageDir=self._TokenStorageDir,
                tokenStorageFile=self._TokenStorageFile,
                tokenProviderId='SpotifyWebApiAuthCodePkce',
                tokenProfileId=tokenProfileId,
                tokenUpdater=self._TokenUpdater
            )
           
            # force the user to logon to spotify to authorize the application access if we 
            # do not have an authorized access token, or if the calling application requested 
            # us (by force) to re-authorize, or if the scope has changed.
            isAuthorized = self._AuthClient.IsAuthorized
            _logsi.LogVerbose('Checking OAuth2 authorization status: IsAuthorized=%s, Force=%s' % (isAuthorized, forceAuthorize))

            if (isAuthorized == False) or (forceAuthorize == True):
                
                # at this point, we need a new authorization token.
                _logsi.LogVerbose('Preparing to retrieve a new OAuth2 authorization access token')
                self._AuthClient.AuthorizeWithServer(
                    host=redirectUriHost, 
                    port=redirectUriPort, 
                    redirect_uri_path=redirectUriPath,
                    open_browser=True, 
                    force=forceAuthorize,
                    timeout_seconds=120
                )
                
            else:
                
                _logsi.LogVerbose('OAuth2 authorization token is authorized')

            # process results.
            oauth2token:dict = self._AuthClient.Session.token
            self._AuthToken = SpotifyAuthToken(self._AuthClient.AuthorizationType, self._AuthClient.TokenProfileId, root=oauth2token)
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT % apiMethodName, self._AuthToken, excludeNonPublic=True)
            
            # does token need to be refreshed?
            if self._AuthToken.IsExpired:

                # refresh the token.  
                # this will also store the refreshed token to disk to be used later if required.
                _logsi.LogVerbose("OAuth2 authorization token has expired, or is about to; token will be refreshed")
                oauth2token:dict = self._AuthClient.RefreshToken()
                self._AuthToken = SpotifyAuthToken(self._AuthClient.AuthorizationType, self._AuthClient.TokenProfileId, root=oauth2token)
                _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT % apiMethodName, self._AuthToken, excludeNonPublic=True)
            
            else:
                
                _logsi.LogVerbose('OAuth2 authorization token has not expired')

            # retrieve spotify user basic details.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            self.MakeRequest('GET', msg)

            # process results.
            self._UserProfile = UserProfile(root=msg.ResponseData)

            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_MSG_USERPROFILE % (self._UserProfile.DisplayName, self._UserProfile.EMail), self._UserProfile, excludeNonPublic=True)

            # start / restart Zeroconf Directory task.
            self._RestartSpotifyConnectDirectoryTask()

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # trace.
            _logsi.LogException(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logToSystemLogger=False)
            raise

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def SetAuthTokenClientCredentials(
        self, 
        clientId:str, 
        clientSecret:str,
        tokenProfileId:str=None
        ) -> None:
        """
        Generates a new client credentials type of authorization token used to access 
        the Spotify Web API.
        
        Args:
            clientId (str):
                The unique identifier of the application.
            clientSecret (str):
                The application's secret key, used to authorize your Web API or SDK calls.
            tokenProfileId (str):
                Profile identifier used when loading / storing the token to disk.  
                A null value will default to `Shared`.  
                Default: `Shared`               
                
        The Client Credentials flow is used in server-to-server authentication. Since this flow does
        not include authorization, only endpoints that do not access user information can be accessed.
        
        There is also no persistant token storage, as a new token is retrieved when this method
        is called initially, and when the token needs to be refreshed.
        """
        apiMethodName:str = 'SetAuthTokenClientCredentials'
        apiMethodParms:SIMethodParmListContext = None
        authorizationType:str = 'Client Credentials'
        
        try:

            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("clientId", clientId)
            apiMethodParms.AppendKeyValue("clientSecret", clientSecret)
            apiMethodParms.AppendKeyValue("tokenProfileId", tokenProfileId)
            _logsi.LogMethodParmList(SILevel.Verbose, TRACE_MSG_AUTHTOKEN_CREATE % authorizationType, apiMethodParms)
                                
            # create oauth provider for spotify authentication code with pkce.
            self._AuthClient:AuthClient = AuthClient(
                authorizationType=authorizationType,
                tokenUrl=self.SpotifyApiTokenUrl,
                clientId=clientId,
                clientSecret=clientSecret,
                oauth2Client=BackendApplicationClient(client_id=clientId),  # required for grant_type = client_credentials
                tokenStorageDir=self._TokenStorageDir,
                tokenStorageFile=self._TokenStorageFile,
                tokenProviderId='SpotifyWebApiClientCredentials',
                tokenProfileId=tokenProfileId,
                tokenUpdater=self._TokenUpdater
            )

            # fetch a new access token.
            self._AuthClient.FetchToken()
                
            # process results.
            oauth2token:dict = self._AuthClient.Session.token
            self._AuthToken = SpotifyAuthToken(self._AuthClient.AuthorizationType, self._AuthClient.TokenProfileId, root=oauth2token)
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT % apiMethodName, self._AuthToken, excludeNonPublic=True)
            
            # note that we cannot retrieve spotify user basic details, as the client credentials
            # authentication type does not utilize an authorization token.  in this case, we will
            # build a "public access" user profile, just so we have something there.  
            # 
            # also note that we do not set a value for Country, as some endpoints require a country
            # (or market) code in order to work properly (e.g. any of the Search... methods).
            userProfile:UserProfile = UserProfile()
            userProfile._DisplayName = 'Public Access'
            userProfile._Followers = Followers()
            userProfile._Followers._Total = 0
            userProfile._Id = 'unknown'
            userProfile._Uri = 'spotify.user.' + userProfile._Id
            self._UserProfile = userProfile

            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_MSG_USERPROFILE % (self._UserProfile.DisplayName, self._UserProfile.EMail), self._UserProfile, excludeNonPublic=True)

            # start / restart Zeroconf Directory task.
            self._RestartSpotifyConnectDirectoryTask()

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # trace.
            _logsi.LogException(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logToSystemLogger=False)
            raise

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def SetAuthTokenFromToken(
        self, 
        clientId:str,
        token:dict, 
        tokenProfileId:str=None
        ) -> None:
        """
        Uses an OAuth2 authorization token that was generated from an external provider to access 
        the Spotify Web API.

        Args:
            clientId (str):
                The unique identifier of the application.
            token (dict):
                A dictionary object that contains OAuth2 token data.
            tokenProfileId (str):
                Profile identifier used when loading / storing the token to disk.  
                A null value will default to `Shared`.  
                Default: `Shared`               
                
        Raises:
            SpotifyApiError: 
                If the method fails for any reason.  
                
        Make sure you have the `tokenUpdater` argument supplied on the class constructor so that
        token updates are passed on to the external provider.
        """
        apiMethodName:str = 'SetAuthTokenFromToken'
        apiMethodParms:SIMethodParmListContext = None
        authorizationType:str = 'OAuth2Token'
        
        try:

            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("clientId", clientId)
            apiMethodParms.AppendKeyValue("token", token)
            apiMethodParms.AppendKeyValue("tokenProfileId", tokenProfileId)
            _logsi.LogMethodParmList(SILevel.Verbose, TRACE_MSG_AUTHTOKEN_CREATE % authorizationType, apiMethodParms)
            _logsi.LogDictionary(SILevel.Verbose, "token (pretty print)", token, prettyPrint=True)
        
            # validation.
            if token is None:
                raise SpotifyApiError(SAAppMessages.ARGUMENT_TYPE_ERROR % (apiMethodName, 'token', 'dict', type(token).__name__), logsi=_logsi)

            # create oauth provider for existing oauth2 session.
            # the client secret is not needed, as the OAuth2 Session has already been established externally
            # and the initial token generated.  after this, we will only need to REFRESH the token, which 
            # does not require knowing the secret.
            self._AuthClient:AuthClient = AuthClient(
                authorizationType=authorizationType,
                tokenUrl=self.SpotifyApiTokenUrl,
                scope=token.get('scope'),
                clientId=clientId,
                tokenStorageDir=self._TokenStorageDir,
                tokenStorageFile=self._TokenStorageFile,
                tokenProviderId='SpotifyWebApiOAuth2Token',
                tokenProfileId=tokenProfileId,
                tokenUpdater=self._TokenUpdater
            )
            
            # assign the token if one is not present.
            if self._AuthClient.Session.token is None or len(self._AuthClient.Session.token) == 0:
                self._AuthClient.Session.token = token
           
            # process the oauth2 session token.
            oauth2token:dict = self._AuthClient.Session.token
            self._AuthToken = SpotifyAuthToken(self._AuthClient.AuthorizationType, self._AuthClient.TokenProfileId, root=oauth2token)
            _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT % apiMethodName, self._AuthToken, excludeNonPublic=True)
            
            # does token need to be refreshed?
            if self._AuthToken.IsExpired:

                # refresh the token.  
                # this will also store the refreshed token to disk to be used later if required.
                _logsi.LogVerbose("OAuth2 authorization token has expired, or is about to; token will be refreshed")
                oauth2token:dict = self._AuthClient.RefreshToken()
                self._AuthToken = SpotifyAuthToken(self._AuthClient.AuthorizationType, self._AuthClient.TokenProfileId, root=oauth2token)
                _logsi.LogObject(SILevel.Verbose, TRACE_METHOD_RESULT % apiMethodName, self._AuthToken, excludeNonPublic=True)
            
            else:
                
                _logsi.LogVerbose('OAuth2 authorization token has not expired')

            # retrieve spotify user basic details.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            self.MakeRequest('GET', msg)

            # process results.
            self._UserProfile = UserProfile(root=msg.ResponseData)

            # trace.
            _logsi.LogObject(SILevel.Verbose, TRACE_MSG_USERPROFILE % (self._UserProfile.DisplayName, self._UserProfile.EMail), self._UserProfile, excludeNonPublic=True)

            # start / restart Zeroconf Directory task, if there was no exception.
            self._RestartSpotifyConnectDirectoryTask()

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # trace.
            _logsi.LogException(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logToSystemLogger=False)
            raise

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'SpotifyClient:'
        msg = "%s\n ConfigurationCache key count=%d" % (msg, len(self._ConfigurationCache))
        msg = "%s\n TokenStorageDir='%s'" % (msg, self._TokenStorageDir)
        msg = "%s\n TokenStorageFile='%s'" % (msg, self._TokenStorageFile)
        if self._UserProfile is not None:
            msg = "%s\n User DisplayName='%s' (%s)" % (msg, self._UserProfile.DisplayName, self._UserProfile.Id)
        return msg


    def UnfollowArtists(
        self, 
        ids:str=None,
        ) -> None:
        """
        Remove the current user as a follower of one or more artists.

        This method requires the `user-follow-modify` scope.
        
        Args:
            ids (str):  
                A comma-separated list of Spotify artist IDs.  
                A maximum of 50 IDs can be sent in one request.
                Example: `2CIMQHirSU0MQqyYHq0eOx,1IQ2e1buppatiN1bxUVkrk`
                If null, the currently playing track artist uri id value is used.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.
                
        No exception is raised if a specified artist id is not being followed.
                
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/UnfollowArtists.py
        ```
        </details>
        """
        apiMethodName:str = 'UnfollowArtists'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            _logsi.LogMethodParmList(SILevel.Verbose, "Remove the current user as a follower of one or more artists", apiMethodParms)
                
            # if ids not specified, then return currently playing artist id value.
            if (ids is None) or (len(ids.strip()) == 0):
                uri = self.GetPlayerNowPlayingArtistUri()
                if uri is not None:
                    ids = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'ids'), logsi=_logsi)

            # build a list of all item id's.
            # remove any leading / trailing spaces in case user put a space between the items.
            arrIds:list[str] = ids.split(',')
            for idx in range(0, len(arrIds)):
                arrIds[idx] = arrIds[idx].strip()
                
            # build spotify web api request parameters.
            reqData:dict = \
            {
                'ids': arrIds
            }

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/following?type=artist')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.RequestJson = reqData
            self.MakeRequest('DELETE', msg)
            
            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def UnfollowPlaylist(
        self, 
        playlistId:str=None,
        ) -> None:
        """
        Remove the current user as a follower of a playlist.

        This method requires the `playlist-modify-public` and `playlist-modify-private` scope.
        
        Args:
            playlistId (str):  
                The Spotify ID of the playlist.  
                Example: `3cEYpjA9oz9GiPac4AsH4n`
                If null, the currently playing playlist uri id value is used.
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.
                
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/UnfollowPlaylist.py
        ```
        </details>
        """
        apiMethodName:str = 'UnfollowPlaylist'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("playlistId", playlistId)
            _logsi.LogMethodParmList(SILevel.Verbose, "Remove the current user as a follower of a playlist", apiMethodParms)
                
            # if playlistId not specified, then return currently playing playlist id value.
            if (playlistId is None) or (len(playlistId.strip()) == 0):
                uri = self.GetPlayerNowPlayingPlaylistUri()
                if uri is not None:
                    playlistId = SpotifyClient.GetIdFromUri(uri)
                else:
                    raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'playlistId'), logsi=_logsi)

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/playlists/{playlist_id}/followers'.format(playlist_id=playlistId))
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            self.MakeRequest('DELETE', msg)
            
            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def UnfollowUsers(
        self, 
        ids:str,
        ) -> None:
        """
        Remove the current user as a follower of one or more users.

        This method requires the `user-follow-modify` scope.
        
        Args:
            ids (str):  
                A comma-separated list of Spotify user IDs.  
                A maximum of 50 IDs can be sent in one request.
                Example: `smedjan`
                
        Raises:
            SpotifyWebApiError: 
                If the Spotify Web API request was for a non-authorization service 
                and the response contains error information.
            SpotifyApiError: 
                If the method fails for any other reason.
                
        No exception is raised if a specified user id is not being followed.
                
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyClient/UnfollowUsers.py
        ```
        </details>
        """
        apiMethodName:str = 'UnfollowUsers'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("ids", ids)
            _logsi.LogMethodParmList(SILevel.Verbose, "Remove current user as a follower of one or more users", apiMethodParms)
                
            # build a list of all item id's.
            # remove any leading / trailing spaces in case user put a space between the items.
            arrIds:list[str] = ids.split(',')
            for idx in range(0, len(arrIds)):
                arrIds[idx] = arrIds[idx].strip()
                
            # build spotify web api request parameters.
            reqData:dict = \
            {
                'ids': arrIds
            }

            # execute spotify web api request.
            msg:SpotifyApiMessage = SpotifyApiMessage(apiMethodName, '/me/following?type=user')
            msg.RequestHeaders[self.AuthToken.HeaderKey] = self.AuthToken.HeaderValue
            msg.RequestJson = reqData
            self.MakeRequest('DELETE', msg)
            
            # process results.
            # no results to process - this is pass or fail.
            return

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiError: raise  # pass handled exceptions on thru
        except SpotifyWebApiAuthenticationError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)
