# external package imports.
import json
import requests
from requests.models import Response
import time

# our package imports.
from .blobbuilder import BlobBuilder
from .credentials import Credentials, AuthenticationTypes
from .helpers import int_to_b64str
from .spotifyzeroconfapierror import SpotifyZeroconfApiError
from .zeroconfresponse import ZeroconfResponse
from .zeroconfgetinfo import ZeroconfGetInfo
from ..saappmessages import SAAppMessages
from ..sautils import export, validateDelay
from ..spotifyapierror import SpotifyApiError
from ..spotifywebapierror import SpotifyWebApiError
from ..const import (
    TRACE_MSG_DELAY_DEVICE,
)
from ..sautils import passwordMaskString

# get smartinspect logger reference; create a new session for this module name.
from smartinspectpython.siauto import SIAuto, SILevel, SISession, SIMethodParmListContext, SISourceId
import logging
_logsi:SISession = SIAuto.Si.GetSession(__name__)
if (_logsi == None):
    _logsi = SIAuto.Si.AddSession(__name__, True)
_logsi.SystemLogger = logging.getLogger(__name__)


@export
class ZeroconfConnect:
    """
    Interfaces with the Spotify Connect Zeroconf API to add and remove a device to / from the
    Spotify Connect active device list.
    
    More information about Spotify Connect Zeroconf API can be found here:  
    https://developer.spotify.com/documentation/commercial-hardware/implementation/guides/zeroconf
    
    Inspiration and some of the blob encryption encoding was derived from the [zerospot](https://github.com/maraid/zerospot) 
    GitHub repository.
    """
    
    SPOTIFY_CONNECT_CLIENT_VERSION_DEFAULT:str = '2.7.1'
    """
    Spotify Connect default version string ('2.7.1').
    """
    

    def __init__(self, 
                 hostIpAddress:str,
                 hostIpPort:int,
                 cpath:str,
                 version:str=None,
                 useSSL:bool=False
                 ) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            hostIpAddress (str):
                IP address or alias at which the Spotify Connect Zeroconf API can be reached
                on the Spotify Connect device (e.g. "192.168.1.81", "Bose-SM2-341513fbeeae.local.", etc).
            hostIpPort (int):
                Port number (as an integer) at which the Spotify Connect Zeroconf API can be reached
                on the Spotify Connect device (e.g. "8200").
            cpath (str):
                Spotify Connect Zeroconf API CPath property value (e.g. "/zc").
            version (str):
                Spotify Connect Zeroconf API version number that the device supports (e.g. "2.10.0").  
                Default is null.
            useSSL (bool):
                True if the host device utilizes HTTPS Secure Sockets Layer (SSL) support; 
                otherwise, False to utilize HTTP.  
                Default is False (HTTP).
        """
        # validations.
        if (useSSL is None) or (not isinstance(useSSL,bool)):
            useSSL = False
        if (version is None) or (not isinstance(version,str)):
            version = ZeroconfConnect.SPOTIFY_CONNECT_CLIENT_VERSION_DEFAULT
            
        # initialize storage.
        self._CPath:str = cpath
        self._HostIpPort:int = hostIpPort
        self._HostIpAddress:str = hostIpAddress
        self._UseSSL:bool = useSSL
        self._Version:str = version

        # get uri used to access the Spotify Zeroconf API for the device.
        self._Uri:str = self.GetEndpointUri()


    @property
    def CPath(self) -> str:
        """ 
        Path that points to the ZeroConf implementation on the server (e.g. "/zc").
        """
        return self._CPath


    @property
    def HostIpAddress(self) -> str:
        """ 
        IP address or alias at which the Spotify Connect Zeroconf API can be reached
        on the Spotify Connect device (e.g. "192.168.1.81", "Bose-SM2-341513fbeeae.local.", etc).
        """
        return self._HostIpAddress
    

    @property
    def HostIpPort(self) -> int:
        """ 
        Port number (as an integer) at which the Spotify Connect Zeroconf API can be reached
        on the Spotify Connect device (e.g. "8200").
        """
        return self._HostIpPort
    

    @property
    def Uri(self) -> str:
        """ 
        Spotify Connect Zeroconf API URI that will be used to access the device (e.g. "http://192.168.1.81:8200/zc").
        """
        return self._Uri


    @property
    def UseSSL(self) -> str:
        """ 
        True if the host device utilizes HTTPS Secure Sockets Layer (SSL) support; 
        otherwise, False to utilize HTTP.  
        
        Default is False (HTTP).
        """
        return self._UseSSL


    @property
    def Version(self) -> str:
        """ 
        Spotify Connect Zeroconf API version number that the device supports (e.g. "", "1.0", "2.10.0", etc.).
        """
        return self._Version or ''


    def _CheckResponseForErrors(self, response:Response, methodName:str, endpoint:str) -> None:
        """
        Checks the Spotify Zeroconf API response for errors.  
        
        If no errors were found, then the request response data is converted to a JSON dictionary 
        and returned to the caller.
        
        If an error result is found, then a `SpotifyZeroconfApiError` is raised to inform the 
        user of the error.
        
        Args:
            response (Response): 
                Spotify Web API http response object.
            methodName (str):
                method name that made the request (for trace purposes).
            endpoint (str):
                Endpoint that was requested (for trace purposes).
                
        Raises:
            SpotifyZeroconfApiError: 
                If the Spotify Zeroconf API request response contains error information.
        """
        responseData:dict = None
        responseUTF8:str = None
        
        try:

            # trace.
            if _logsi.IsOn(SILevel.Debug):
                _logsi.LogObject(SILevel.Debug, 'ZeroconfConnect http response object - type="%s", module="%s"' % (type(response).__name__, type(response).__module__), response)

            # trace.
            if _logsi.IsOn(SILevel.Debug):
                _logsi.LogObject(SILevel.Debug, "ZeroconfConnect http response [%s-%s]: '%s' (response)" % (response.status_code, response.reason, endpoint), response)
                if (response.headers):
                    _logsi.LogCollection(SILevel.Debug, "ZeroconfConnect http response [%s-%s]: '%s' (headers)" % (response.status_code, response.reason, endpoint), response.headers.items())

            # do we have response data?
            if (response.content is not None) and (len(response.content) > 0):
                
                # convert response to JSON object.
                # ALL Spotify Connect Zeroconf API responses SHOULD be JSON format!
                # do not use the "response.json()" method to parse JSON responses, as it is unreliable!
                data = response.content.decode('utf-8')
                responseData = json.loads(data)
                    
                if _logsi.IsOn(SILevel.Verbose):
                    if isinstance(responseData, dict):
                        _logsi.LogDictionary(SILevel.Verbose, "ZeroconfConnect http response [%s-%s]: '%s' (json dict)" % (response.status_code, response.reason, endpoint), responseData, prettyPrint=True)
                    elif isinstance(responseData, list):
                        _logsi.LogArray(SILevel.Verbose, "ZeroconfConnect http response [%s-%s]: '%s' (json array)" % (response.status_code, response.reason, endpoint), responseData)
                    else:
                        _logsi.LogObject(SILevel.Verbose, "ZeroconfConnect http response [%s-%s]: '%s' (json object)" % (response.status_code, response.reason, endpoint), responseData)
                
            else:
                
                # raise an exception, as we are expecting a JSON-formatted response!
                errMessage = response.content.decode('utf-8')                       
                raise SpotifyWebApiError(response.status_code, errMessage, methodName, response.reason, _logsi)
                
        except SpotifyZeroconfApiError: raise  # pass handled exceptions on thru
        except SpotifyApiError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            _logsi.LogException("ZeroconfConnect http response could not be converted to JSON and will be converted to utf-8.\nConversion exception returned was:\n{ex}".format(ex=str(ex)), ex, logToSystemLogger=False)

            # if json conversion failed, then convert to utf-8 response.
            if response.content is not None:
                responseUTF8 = response.content.decode('utf-8')
                _logsi.LogText(SILevel.Error, "ZeroconfConnect http response [%s-%s]: '%s' (utf-8)" % (response.status_code, response.reason, endpoint), responseUTF8)
            
            # at this point we don't know what Spotify Web Api returned!
            # it's been found that some devices (Sonos, etc) do not return a proper JSON response.
            # raise a new exception with the non-JSON response data if the http status is not 200 (OK).
            if (response.status_code != 200):
                raise SpotifyZeroconfApiError(response.status_code, responseUTF8, methodName, response.reason, _logsi)

            # trace.
            _logsi.LogVerbose("Spotify Connect Device (ip=%s) returned an invalid JSON response, but the http status code was 200 so we will ignore it" % (self._HostIpAddress))

        # at this point we know that the response contains JSON data, as
        # we would have raised an exception before this if we could not
        # convert the response to JSON!

        # now it's a matter of interpreting the JSON `Status` response to determine
        # if the request failed or not.  the following documents the Spotify
        # Zeroconf API http status codes and JSON status codes.
        
        # taken from:  https://developer.spotify.com/documentation/commercial-hardware/implementation/guides/zeroconf
        # HTTP Status codes
        # Note It is permissible to send HTTP status code 200 in all cases, as long as a valid JSON reply is returned that contains the status, statusString, and spotifyError strings.
        # The following table shows the different responses returned by the HTTP server to a client's request:
        # Status name	    Status	HTTP Status Status string	        Response to	    Usage
        # Ok	            101	    200	        OK or ERROR-OK          All	            Successful operation
        # Bad	            102	    400	        ERROR-BAD-REQUEST	    All	            Web server problem or critically malformed request
        # Unknown	        103	    500	        ERROR-UNKNOWN	        All	            Fallback when no other error applies
        # NotImplemented	104	    501	        ERROR-NOT-IMPLEMENTED	All	            Server does not implement this feature
        # LoginFailed	    202	    200	        ERROR-LOGIN-FAILED	    addUser	        Spotify returned error when trying to login
        # InvalidPublicKey  203     xxx         ERROR-INVALID-PUBLICKEY addUser         ZeroConf login failed due to an invalid public key
        # MissingAction	    301	    400	        ERROR-MISSING-ACTION	All	            Web request has no action parameter
        # InvalidAction	    302	    400	        ERROR-INVALID-ACTION	All	            Web request has unrecognized action parameter
        # InvalidArguments	303	    400	        ERROR-INVALID-ARGUMENTS	All	            Incorrect or insufficient arguments supplied for requested action
        # SpotifyError	    402	    200	        ERROR-SPOTIFY-ERROR	    All	            A Spotify API call returned an error not covered by other error messages

        # let the calling function process the returned status.
        return responseData


    def Connect(
            self,
            username:str, 
            password:str, 
            loginId:str=None, 
            delay:float=0.50
            ) -> ZeroconfResponse:
        """
        Calls the `addUser` Spotify Zeroconf API endpoint to issue a call to SpConnectionLoginBlob.  If successful,
        the associated device id is added to the Spotify Connect active device list for the specified user account.
        
        
        Args:
            username (str):
                Spotify Connect user name to login with (e.g. "yourspotifyusername").  
                This MUST match the account name (or one of them) that was used to configure Spotify Connect 
                on the manufacturer device.               
            password (str):
                Spotify Connect user password to login with.  
            loginId (str):
                Spotify Connect login id to login with (e.g. "31l77fd87g8h9j00k89f07jf87ge").  
                This is also known as the canonical user id value.  
                This MUST be the value that relates to the `username` argument.  
            delay (float):
                Time delay (in seconds) to wait AFTER issuing the command to the device.  
                This delay will give the spotify zeroconf api time to process the change before 
                another command is issued.  
                Default is 0.50; value range is 0 - 10.

        Returns:
            A `ZeroconfResponse` object that indicates success or failure (see notes below).
            
        Raises:
            SpotifyWebApiError: 
                If the Spotify Zeroconf API request response contains error information.
            
        This will first issue a call to the `getInfo` Spotify Zeroconf API endpoint to retrieve the Spotify
        Connect device id associated with the device.  It will then issue a call to the `addUser` Spotify Zeroconf 
        API endpoint to add the user to the device.

        Some Spotify Connect device types will be "woken up" with the initial `addUser` request; when this happens,
        the initial request will return a 203 status (ERROR-INVALID-PUBLICKEY), and return a valid public key in the 
        response.  This public key is then used to submit another `addUser` request to connect to the device with the
        newly returned public key.  When this happens, a `ZeroconfResponse` object is returned with the result of
        the final `addUser` request.  If only one `addUser` request is processed, then a `ZeroconfGetInfo` object is
        returned with the result of the `addUser` request.  Note that `ZeroconfGetInfo` inherits from `ZeroconfResponse`,
        so you can always treat the result of this method as a `ZeroconfResponse` object.
          
        The login (on the device) is performed asynchronously, so the return result only indicates whether the library 
        is able to perform the login attempt.  You should issue a call to the Spotify Web API `Get Available Devices` 
        endpoint to check the current device list to ensure that the device id was successfully added or not.

        Note that if you don't have a password setup for your Spotify account (e.g. you utilize the "Continue with Google" 
        or other non-password methods for login), then you will need to define a "device password" in order to use the 
        ZeroConf Connect service; use the [Spotify Set Device Password](https://www.spotify.com/uk/account/set-device-password/) 
        page to define a device password.  You will then use your Spotify username and the device password to Connect 
        to the device.
        
        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../../docs/include/samplecode/ZeroconfConnect/Connect.py
        ```
        </details>
        """
        apiMethodName:str = 'Connect'
        apiMethodParms:SIMethodParmListContext = None
        result:ZeroconfResponse = None
        response:Response = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("HostIpAddress", self._HostIpAddress)
            apiMethodParms.AppendKeyValue("HostIpPort", self._HostIpPort)
            apiMethodParms.AppendKeyValue("CPath", self._CPath)
            apiMethodParms.AppendKeyValue("Version", self._Version)
            apiMethodParms.AppendKeyValue("Uri", self._Uri)
            apiMethodParms.AppendKeyValue("loginId", loginId)
            apiMethodParms.AppendKeyValue("username", username)
            apiMethodParms.AppendKeyValue("password (with mask)", passwordMaskString(password))
            apiMethodParms.AppendKeyValue("delay", delay)
            _logsi.LogMethodParmList(SILevel.Verbose, "Connecting device to Spotify Connect using specified Username and Password (ip=%s)" % self._HostIpAddress, apiMethodParms)

            # validations.
            if (username is None) or (not isinstance(username,str)):
                raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'username'), logsi=_logsi)
            if (password is None) or (not isinstance(password,str)):
                raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'password'), logsi=_logsi)
            delay = validateDelay(delay, 0.50, 10)

            # get the current device id from the device via Spotify ZeroConf API `getInfo` endpoint.
            info:ZeroconfGetInfo = self.GetInformation()

            # execute the Spotify Zeroconf API addUser request.
            responseData:dict = self._ConnectAddUser(
                info,
                username,
                password,
                loginId,
                apiMethodName,
                )

            # process results.
            # we will process the results with a `ZeroconfGetInfo` object, in case a publicKey was returned.
            result = ZeroconfGetInfo(root=responseData)

            # is the device fully available?  The info.Availability property can be used to determine this.
            # if the device is fully available (Availability=""), then the addUser request should return
            # immediately - hopefully with a 0 status (OK) to denote the request was successul.
            # if the device is not fully available (Availability="NOT-LOADED"), then the addUser request will 
            # probably return a 203 status (ERROR-INVALID-PUBLICKEY) along with a new PublicKey value.  
            # when this happens, we need to wait for the device to become fully available before we retry the 
            # addUser request again with the new public key.
            
            # did we get a new PublicKey value?
            if (result.Status == 203) and (result.StatusString == "ERROR-INVALID-PUBLICKEY"):

                # trace.
                _logsi.LogObject(SILevel.Verbose, '%s result (%s)' % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
                _logsi.LogVerbose("Spotify Connect addUser request returned an ERROR-INVALID-PUBLICKEY response for Device id '%s'; addUser will be retried with the returned publicKey" % (info.DeviceId))

                # wait for the device to be fully loaded.
                # once this happens, the device Availability state will change from "NOT-LOADED" to "".
                loopTotalDelay:float = 0
                LOOP_DELAY:float = 0.25
                LOOP_TIMEOUT:float = 5.0
                while True:
                        
                    # wait just a bit between device info queries.
                    _logsi.LogVerbose("Delaying for %s seconds to allow Spotify Connect device id '%s' to become available (currently '%s')" % (LOOP_DELAY, info.DeviceId, info.Availability))
                    time.sleep(LOOP_DELAY)
                    loopTotalDelay = loopTotalDelay + LOOP_DELAY

                    # get device information; if availability status changes then we are done.
                    info = self.GetInformation()
                    if info.Availability != "NOT-LOADED":
                        _logsi.LogVerbose("Spotify Connect Device id '%s' availability status changed to '%s' within %f seconds of initial addUser request" % (info.DeviceId, info.Availability, loopTotalDelay))
                        break
                        
                    # only check so many times before we give up;
                    if (loopTotalDelay > LOOP_TIMEOUT):
                        _logsi.LogWarning("Timed out waiting for Spotify Connect device id '%s' availability to change from '%s'; gave up after %f seconds from initial addUser request" % (info.DeviceId, info.Availability, loopTotalDelay))
                        break

                # now that the device is (hopefully) fully available, try the addUser request again.
                responseData = self._ConnectAddUser(
                    info,
                    username,
                    password,
                    loginId,
                    apiMethodName,
                    )

                # process results.
                result = ZeroconfResponse(root=responseData)

            # trace.
            _logsi.LogObject(SILevel.Verbose, '%s result (%s)' % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)

            # if result status is not ok, then raise an exception.
            if (result.Status != 101):
                raise SpotifyZeroconfApiError(result.Status, result.ToString(), apiMethodName, result.StatusString, _logsi)

            # give spotify zeroconf api time to process the change.
            if delay > 0:
                _logsi.LogVerbose(TRACE_MSG_DELAY_DEVICE % delay)
                time.sleep(delay)
                        
            # return result to caller.
            return result

        except SpotifyZeroconfApiError: raise  # pass handled exceptions on thru
        except SpotifyApiError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # close the response (if needed).
            if response is not None:
                response.close()

            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def _ConnectAddUser(
            self,    
            info:ZeroconfGetInfo,
            username:str,
            password:str,
            loginId:str,
            apiMethodName:str,
            ) -> dict:
        """
        Execute the `addUser` request.
        """
        apiMethodName:str = '_ConnectAddUser'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("info.Availability", info.Availability)
            apiMethodParms.AppendKeyValue("info.PublicKey", info.PublicKey)
            apiMethodParms.AppendKeyValue("info.DeviceId", info.DeviceId)
            apiMethodParms.AppendKeyValue("info.RemoteName", info.RemoteName)
            _logsi.LogMethodParmList(SILevel.Verbose, "Issuing Spotify Connect Zeroconf addUser request (ip=%s)" % self._HostIpAddress, apiMethodParms)
        
            # formulate the blob.
            credentials:Credentials = Credentials(username, password, AuthenticationTypes.USER_PASS)
            builder = BlobBuilder(credentials, info.DeviceId, info.PublicKey)
            blob = builder.build()
        
            # set request endpoint.
            endpoint:str = self.GetEndpoint('addUser')
            
            # set request headers.
            reqHeaders:dict = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Connection': 'close'
            }
            _logsi.LogDictionary(SILevel.Debug, "ZeroconfConnect http request: '%s' (headers)" % (endpoint), reqHeaders)

            # set defaults used by most manufacturers - we will tailor these in the
            # logic below for specific manufacturers / devices as required:
            # - clientKey should be the getInfo response PublicKey (base64 encoded).
            # - exclude origin device information from the addUser request.
            # - tokenType should be set to 'default'.
            clientKey:str = builder.dh_keys.PublicKeyBase64String
            includeOriginDeviceInfo:bool = False
            tokenType:str = 'default'
            
            # include the origin device information if PublicKey="INVALID" (base64 encoded) and availability="NOT-LOADED".
            if (info.PublicKey == 'SU5WQUxJRA==') and (info.Availability == 'NOT-LOADED'):
                includeOriginDeviceInfo = True

            # special processing for tokenType "authorization_code":
            # - include origin device information in the addUser request.
            # - set the tokenType to 'authorization_code'.
            # - set the clientKey value to null, as it is contained in the token.
            if info.TokenType == 'authorization_code':                
                clientKey = ''
                includeOriginDeviceInfo = True
                tokenType = info.TokenType
                
                # TODO - not sure of the blob credentials layout for AuthenticationTypes.SPOTIFY_TOKEN requests.
                # get a Spotify WebServices API auth token that the Sonos device can use.
                #credentials:Credentials = Credentials(username, authToken, AuthenticationTypes.SPOTIFY_TOKEN)  # authToken is the password
                #credentials:Credentials = Credentials('', authToken, AuthenticationTypes.SPOTIFY_TOKEN)  # authToken is the password
                #builder = BlobBuilder(credentials, info.DeviceId, info.PublicKey)
                #blob = builder.build()

            # set request parameters.
            reqData={
                'action': 'addUser',
                'version': info.Version,
                'tokenType': tokenType,
                'clientKey': clientKey,
                'loginId': loginId or '',                                   # canonical login id (e.g. "31l77fd87g8h9j00k89f07jf87ge")
                'userName': credentials.username.decode('ascii'),           # user name (e.g. "youremail@mail.com")
                'blob': blob,
            }

            # are we including origin device information (e.g. deviceName, deviceId)?
            # the `deviceName` and `deviceId` keys are specified by some manufacturers for the
            # `addUser` action.  I am not sure if they are required or not, as they are not part
            # of the Spotify Zeroconf API specification for the `addUser` action.
            if (includeOriginDeviceInfo):
                _logsi.LogVerbose("Origin deviceName and deviceId will be included with the addUser request for deviceId '%s'" % (info.DeviceId))
                reqData['deviceName'] = builder._OriginDeviceName
                reqData['deviceId'] = builder._OriginDeviceId
        
            # if PublicKey="INVALID" and availability="NOT-LOADED" then adjust the addUser 
            # request to remove the blob and clientKey values.  this will inform the device to
            # send us back a PublicKey value, which can be used on a subsequent addUser request.
            if (info.PublicKey == 'SU5WQUxJRA==') and (info.Availability == 'NOT-LOADED'):
                _logsi.LogVerbose("Spotify Connect PublicKey='INVALID' and Availability='NOT-LOADED' detected for Device id '%s'; removing blob and clientKey values" % (info.DeviceId))
                reqData['blob'] = ''
                reqData['clientKey'] = ''

            # trace.
            _logsi.LogDictionary(SILevel.Verbose, "ZeroconfConnect http request: '%s' (data)" % (endpoint), reqData)

            # execute spotify zeroconf api request.
            response = requests.post(
                self._Uri,
                timeout=10,
                headers=reqHeaders,
                data=reqData   # send data in POST request body
            )
        
            # check response for initial errors, and return json response.
            responseData:dict = self._CheckResponseForErrors(response, apiMethodName, endpoint)
            return responseData
        
        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def Disconnect(
            self,
            delay:float=0.50,
            ignoreStatusResult:bool=False
            ) -> ZeroconfResponse:
        """
        Calls the `resetUsers` Spotify Zeroconf API endpoint to issue a call to SpConnectionLogout.
        
        Args:
            delay (float):
                Time delay (in seconds) to wait AFTER issuing the command to the device.  
                This delay will give the spotify zeroconf api time to process the change before 
                another command is issued.  
                Default is 0.50; value range is 0 - 10.
            ignoreStatusResult (bool):
                True to ignore processing of result status code;
                otherwise, False to check the result status code for errors and raise an 
                exception if needed.  
                Default is
                
        Returns:
            A `ZeroconfResponse` object that indicates success or failure (see notes below).

        Raises:
            SpotifyWebApiError: 
                If the Spotify Zeroconf API request response contains error information.

        The currently logged in user (if any) will be logged out of Spotify Connect, and the 
        device id removed from the active Spotify Connect device list.  

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../../docs/include/samplecode/ZeroconfConnect/Disconnect.py
        ```
        </details>
        """
        apiMethodName:str = 'Disconnect'
        apiMethodParms:SIMethodParmListContext = None
        result:ZeroconfResponse = None
        response:Response = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("HostIpAddress", self._HostIpAddress)
            apiMethodParms.AppendKeyValue("HostIpPort", self._HostIpPort)
            apiMethodParms.AppendKeyValue("CPath", self._CPath)
            apiMethodParms.AppendKeyValue("Version", self._Version)
            apiMethodParms.AppendKeyValue("Uri", self._Uri)
            apiMethodParms.AppendKeyValue("delay", delay)
            apiMethodParms.AppendKeyValue("ignoreStatusResult", ignoreStatusResult)
            _logsi.LogMethodParmList(SILevel.Verbose, "Disconnecting device from Spotify Connect (ip=%s)" % self._HostIpAddress, apiMethodParms)
            
            # validations.
            delay = validateDelay(delay, 0.50, 10)
            
            # set request endpoint.
            endpoint:str = self.GetEndpoint('resetUsers')
            if ignoreStatusResult is None:
                ignoreStatusResult = False
            
            # set request headers.
            reqHeaders:dict = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Connection': 'close'
            }
            _logsi.LogDictionary(SILevel.Debug, "ZeroconfConnect http request: '%s' (headers)" % (endpoint), reqHeaders)
            
            # set request parameters.
            reqData={
                'action': 'resetUsers',
                'version': self.Version,
            }
            _logsi.LogDictionary(SILevel.Verbose, "ZeroconfConnect http request: '%s' (data)" % (endpoint), reqData)

            # execute spotify zeroconf api request.
            response = requests.post(
                self._Uri,
                timeout=10,
                headers=reqHeaders,
                data=reqData   # send data in POST request body
            )

            # check response for initial errors, and return json response.
            responseData:dict = self._CheckResponseForErrors(response, apiMethodName, endpoint)

            # process results.
            result = ZeroconfResponse(root=responseData)

            # trace.
            _logsi.LogObject(SILevel.Verbose, '%s result (%s)' % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)

            # was a status value returned?
            # it's been found that some devices (Sonos, etc) do not return a proper JSON response.
            # for these cases, we will rely on the http status code for the response code.
            if (result.Status is None):

                # was a good http status code returned?
                if response.status_code == 200:
                    
                    # yes - default status results if they are not set.
                    result.Status = 101
                    if result.StatusString is None:
                        result.StatusString = "OK"
                    if result.SpotifyError is None:
                        result.SpotifyError = 0

            # are we processing result status?
            if (not ignoreStatusResult):
                
                if (result.Status is None) and (response.status_code != 200):
                    # if status value was not returned and http status is not 200, then 
                    # raise an exception with http status details.
                    raise SpotifyZeroconfApiError(response.status_code, responseData, apiMethodName, response.reason, _logsi)
                        
                elif (result.Status != 101):
                    # if status was returned and it's not ok, then raise an exception
                    # with JSON response details.
                    raise SpotifyZeroconfApiError(result.Status, result.ToString(), apiMethodName, result.StatusString, _logsi)

            # give spotify zeroconf api time to process the change.
            if delay > 0:
                _logsi.LogVerbose(TRACE_MSG_DELAY_DEVICE % delay)
                time.sleep(delay)
                        
            # return result to caller.
            return result

        except SpotifyZeroconfApiError: raise  # pass handled exceptions on thru
        except SpotifyApiError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # close the response (if needed).
            if response is not None:
                response.close()

            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetEndpointUri(self) -> str:
        """
        Gets a Spotify Zeroconf API endpoint uri.
        
        Returns:
            A string containing the endpoint uri.
        """
        protocol:str = 'http'
        if (self._UseSSL):
            protocol = 'https'
            
        return "{protocol}://{ip}:{port}{cpath}".format(
            protocol=protocol,
            ip=self._HostIpAddress, 
            port=self._HostIpPort, 
            cpath=self._CPath, 
            )


    def GetEndpoint(
            self,
            action:str
            ) -> str:
        """
        Gets a Spotify Zeroconf API endpoint uri.
        
        Args:
            action (str):
                Action parameter value (e.g. "getInfo", "addUser", "resetUsers", etc).
        
        Returns:
            A string containing the endpoint.
        """
        return "{uri}?action={action}&version={version}".format(
            uri=self._Uri,
            action=action,
            version=self.Version, 
            )


    def GetInformation(self) -> ZeroconfGetInfo:
        """
        Calls the `getInfo` Spotify Zeroconf API endpoint to return information about the device.
        
        Returns:
            A `ZeroconfGetInfo` object that indicates success or failure (see notes below), as well
            as the device information.

        Raises:
            SpotifyWebApiError: 
                If the Spotify Zeroconf API request response contains error information.
                
        The request will timeout after 5 seconds and an exception raised if the device cannot be reached 
        or does not respond within that time frame.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../../docs/include/samplecode/ZeroconfConnect/GetInformation.py
        ```
        </details>
        """
        apiMethodName:str = 'GetInformation'
        apiMethodParms:SIMethodParmListContext = None
        result:ZeroconfGetInfo = None
        response:Response = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("HostIpAddress", self._HostIpAddress)
            apiMethodParms.AppendKeyValue("HostIpPort", self._HostIpPort)
            apiMethodParms.AppendKeyValue("CPath", self._CPath)
            apiMethodParms.AppendKeyValue("Version", self._Version)
            apiMethodParms.AppendKeyValue("Uri", self._Uri)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get information from Spotify Connect Zeroconf API (ip=%s)" % self._HostIpAddress, apiMethodParms)
            
            # set request endpoint.
            endpoint:str = self.GetEndpoint('getInfo')
            
            # set request headers.
            reqHeaders:dict = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Connection': 'close'
            }
            _logsi.LogDictionary(SILevel.Debug, "ZeroconfConnect http request: '%s' (headers)" % (endpoint), reqHeaders)
            
            # set request parameters.
            reqParams={
                'action': 'getInfo',
                'version': self.Version,
            }
            _logsi.LogDictionary(SILevel.Verbose, "ZeroconfConnect http request: '%s' (params)" % (endpoint), reqParams)

            # execute spotify zeroconf api request.
            response = requests.get(
                self._Uri, 
                timeout=5,
                headers=reqHeaders,
                params=reqParams
            )
        
            # check response for initial errors, and return json response.
            responseData:dict = self._CheckResponseForErrors(response, apiMethodName, endpoint)

            # process results.
            result = ZeroconfGetInfo(root=responseData)

            # trace.
            _logsi.LogObject(SILevel.Verbose, '%s result (%s) - "%s" (%s)' % (apiMethodName, type(result).__name__, result.RemoteName, result.DeviceId), result, excludeNonPublic=True)

            # if result status is not ok, then raise an exception.
            if (result.Status != 101):
                raise SpotifyZeroconfApiError(result.Status, result.ToString(), apiMethodName, result.StatusString, _logsi)

            # return result to caller.
            return result

        except SpotifyZeroconfApiError: raise  # pass handled exceptions on thru
        except SpotifyApiError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # close the response (if needed).
            if response is not None:
                response.close()

            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def ToString(self, includeTitle:bool=False) -> str:
        """
        Returns a displayable string representation of the class.
        
        Args:
            includeTitle (str):
                True to include the class name title prefix.
        """
        msg:str = ''
        if includeTitle: 
            msg = 'ZeroconfConnect:'
        
        msg = '%s\n URI="%s"' % (msg, str(self._Uri))
        if self._CPath is not None: msg = '%s\n CPath="%s"' % (msg, str(self._CPath))
        if self._Version is not None: msg = '%s\n Version="%s"' % (msg, str(self.Version))
        return msg 
