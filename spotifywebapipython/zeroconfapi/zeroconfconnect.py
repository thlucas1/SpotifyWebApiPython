# external package imports.
import json
import requests
from requests.models import Response
import time

# our package imports.
from .blobbuilder import BlobBuilder
from .credentials import Credentials
from .helpers import int_to_b64str
from .spotifyzeroconfapierror import SpotifyZeroconfApiError
from .zeroconfresponse import ZeroconfResponse
from .zeroconfgetinfo import ZeroconfGetInfo
from ..saappmessages import SAAppMessages
from ..sautils import export
from ..spotifyapierror import SpotifyApiError

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
    
    def __init__(self, 
                 hostIpv4Address:str,
                 hostIpPort:str,
                 cpath:str,
                 version:str='1.0',
                 useSSL:bool=False
                 ) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            hostIpv4Address (str):
                IPV4 address (as a string) at which the Spotify Connect Zeroconf API can be reached
                on the Spotify Connect device (e.g. "192.168.1.81").
            hostIpPort (int):
                Port number (as an integer) at which the Spotify Connect Zeroconf API can be reached
                on the Spotify Connect device (e.g. "8200").
            cpath (str):
                Spotify Connect Zeroconf API CPath property value (e.g. "/zc").
            version (str):
                Spotify Connect Zeroconf API version number that the device supports (e.g. "2.10.0").  
                Default is '1.0'.
            useSSL (bool):
                True if the host device utilizes HTTPS Secure Sockets Layer (SSL) support; 
                otherwise, False to utilize HTTP.  
                Default is False (HTTP).

        The URI value consists of an IP Address, port, CPath, and version value that are used to send
        requests to / receive responses from a headless Spotify Connect device.  These values can be
        obtained from a Zeroconf discovery process.
        """
        # validations.
        if (version is None):
            version = '1.0'
            
        # initialize storage.
        self._CPath:str = cpath
        self._HostIpPort:int = hostIpPort
        self._HostIpv4Address:str = hostIpv4Address
        self._UseSSL:bool = useSSL
        self._Version:str = version

        # get uri used to access the Spotify Zeroconf API for the device.
        self._Uri:str = self.GetEndpointUri()


    @property
    def CPath(self) -> str:
        """ 
        Spotify Connect Zeroconf API CPath property value (e.g. "/zc").
        """
        return self._CPath


    @property
    def HostIpv4Address(self) -> str:
        """ 
        IPV4 address (as a string) at which the Spotify Connect Zeroconf API can be reached
        on the Spotify Connect device (e.g. "192.168.1.81").
        """
        return self._HostIpv4Address
    

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
        Spotify Connect Zeroconf API version number that the device supports (e.g. "2.10.0").
        """
        return self._Version


    def _CheckResponseForErrors(self, response:Response, methodName:str) -> None:
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
                
        Raises:
            SpotifyZeroconfApiError: 
                If the Spotify Zeroconf API request response contains error information.
        """
        responseData:dict = None
        responseUTF8:str = None
        contentType:str = None
        
        try:

            # trace.
            if _logsi.IsOn(SILevel.Debug):
                _logsi.LogObject(SILevel.Debug, 'ZeroconfConnect http response object - type="%s", module="%s"' % (type(response).__name__, type(response).__module__), response)

            # safely get the response url value.
            # for some reason, the 'url' attribute is not present sometimes if a redirect occurs on the request.
            responseUrl:str = None
            if hasattr(response, 'url'):
                responseUrl = response.url
            elif hasattr(response, '_request_url'):
                responseUrl = response._request_url
            else:
                try:
                    responseUrl = response.geturl()
                except Exception:
                    _logsi.LogWarning('HTTPResponse method "geturl()" could not be called - defaulting to "unknown response url"')
                    responseUrl = 'Unknown response url'
                
            # trace.
            if _logsi.IsOn(SILevel.Debug):
                _logsi.LogObject(SILevel.Debug, "ZeroconfConnect http response [%s-%s]: '%s' (response)" % (response.status_code, response.reason, responseUrl), response)
                if (response.headers):
                    _logsi.LogCollection(SILevel.Debug, "ZeroconfConnect http response [%s-%s]: '%s' (headers)" % (response.status_code, response.reason, responseUrl), response.headers.items())

            if response.content is not None:
                
                # do response headers contain a content-type value?
                # if so, we will use it to determine how to convert the response data.
                if response.headers:
                    if 'content-type' in response.headers:
                        contentType = response.headers['content-type']

                # do we have response data?
                if len(response.content) == 0:
                    
                    # some requests will not return a response, which is ok.
                    responseData = None
                    _logsi.LogVerbose("ZeroconfConnect http response [%s-%s]: '%s' (no data)" % (response.status_code, response.reason, responseUrl))

                elif (contentType is not None) and (contentType.find('json') > -1):
                    
                    # response is json.
                    # do not use the "response.json()" method to parse JSON responses, as it is unreliable!
                    data = response.content.decode('utf-8')
                    responseData = json.loads(data)
                    
                    if _logsi.IsOn(SILevel.Verbose):
                        if isinstance(responseData, dict):
                            _logsi.LogDictionary(SILevel.Verbose, "ZeroconfConnect http response [%s-%s]: '%s' (json dict)" % (response.status_code, response.reason, responseUrl), responseData)
                        elif isinstance(responseData, list):
                            _logsi.LogArray(SILevel.Verbose, "ZeroconfConnect http response [%s-%s]: '%s' (json array)" % (response.status_code, response.reason, responseUrl), responseData)
                        else:
                            _logsi.LogObject(SILevel.Verbose, "ZeroconfConnect http response [%s-%s]: '%s' (json object)" % (response.status_code, response.reason, responseUrl), responseData)
                    
                else:
                    
                    # no - treat it as utf-8 encoded data.
                    responseUTF8 = response.content.decode('utf-8')
                    _logsi.LogText(SILevel.Error, "ZeroconfConnect http response [%s-%s]: '%s' (utf-8)" % (response.status_code, response.reason, responseUrl), responseUTF8)
                    responseData = responseUTF8

        except SpotifyZeroconfApiError: raise  # pass handled exceptions on thru
        except SpotifyApiError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            _logsi.LogException("ZeroconfConnect http response could not be converted to JSON and will be converted to utf-8.\nConversion exception returned was:\n{ex}".format(ex=str(ex)), ex, logToSystemLogger=False)

            # if json conversion failed, then convert to utf-8 response.
            if response.content is not None:
                responseUTF8 = response.content.decode('utf-8')
                _logsi.LogText(SILevel.Error, "ZeroconfConnect http response [%s-%s]: '%s' (utf-8)" % (response.status_code, response.reason, responseUrl), responseUTF8)
            
            # at this point we don't know what Spotify Web Api returned, so let's 
            # just raise a new exception with the non-JSON response data.
            raise SpotifyZeroconfApiError(response.status_code, responseUTF8, methodName, response.reason, _logsi)
            
        errCode:str = None
        errMessage:str = None
        
        # if response is not in the 2xx range then it's an error, even
        # though no json 'error' response body was returned!  this is
        # usually due to a '405 - method not allowed' or '403-Forbidden',
        # or '503 Server Error' response.
        if response.status_code > 299:
                
            errCode = response.status_code
            errMessage = response.reason
                
            if responseUTF8 is not None:
                errMessage = responseUTF8

            raise SpotifyZeroconfApiError(errCode, errMessage, methodName, response.reason, _logsi)
            
        # no errors found - set message object response data.
        return responseData


    def Connect(self,
                username:str, 
                password:str, 
                ) -> ZeroconfResponse:
        """
        Calls the `addUser` Spotify Zeroconf API endpoint to issue a call to SpConnectionLoginBlob.  If successful,
        the associated device id is added to the Spotify Connect active device list for the specified user account.
        
        
        Args:
            username (str):
                Spotify Connect user name to login with.  
            password (str):
                Spotify Connect user password to login with.  

        Returns:
            A `ZeroconfResponse` object that indicates success or failure (see notes below).
            
        Raises:
            SpotifyWebApiError: 
                If the Spotify Zeroconf API request response contains error information.
            
        This will first issue a call to the `getInfo` Spotify Zeroconf API endpoint to retrieve the Spotify
        Connect device id associated with the device.  It will then issue a call to the `addUser` Spotify Zeroconf 
        API endpoint to add the user to the device.
          
        The login (on the device) is performed asynchronously, so the return result only indicates whether the library 
        is able to perform the login attempt.  You should issue a call to the Spotify Web API `Get Available Devices` 
        endpoint to check the current device list to ensure that the device id was successfully added or not.

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
            apiMethodParms.AppendKeyValue("HostIpv4Address", self._HostIpv4Address)
            apiMethodParms.AppendKeyValue("HostIpPort", self._HostIpPort)
            apiMethodParms.AppendKeyValue("CPath", self._CPath)
            apiMethodParms.AppendKeyValue("Version", self._Version)
            apiMethodParms.AppendKeyValue("Uri", self._Uri)
            apiMethodParms.AppendKeyValue("username", username)
            _logsi.LogMethodParmList(SILevel.Verbose, "Connecting device to Spotify Connect using specified Username and Password", apiMethodParms)

            # validations.
            if (username is None) or (not isinstance(username,str)):
                raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'username'), logsi=_logsi)
            if (password is None) or (not isinstance(password,str)):
                raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'password'), logsi=_logsi)

            # get the current device id from the device via Spotify ZeroConf API `getInfo` endpoint.
            info:ZeroconfGetInfo = self.GetInformation()
        
            # formulate the blob.
            credentials:Credentials = Credentials(username, password)
            builder = BlobBuilder(credentials, info.DeviceId, info.PublicKey)
            blob = builder.build()
        
            # execute spotify zeroconf api request.
            response = requests.post(
                self._Uri,
                timeout=10,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                data={
                    'action': 'addUser',
                    'VERSION': self._Version,
                    'userName': credentials.username.decode('ascii'),
                    'clientKey': int_to_b64str(builder.dh_keys.public_key),
                    'blob': blob
                }
            )
        
            # check response for errors, and return json response.
            responseData:dict = self._CheckResponseForErrors(response, apiMethodName)

            # process results.
            result = ZeroconfResponse(root=responseData)

            # trace.
            _logsi.LogObject(SILevel.Verbose, '%s result - type="%s"' % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
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


    def Disconnect(self) -> ZeroconfResponse:
        """
        Calls the `resetUsers` Spotify Zeroconf API endpoint to issue a call to SpConnectionLogout.
        
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
            apiMethodParms.AppendKeyValue("HostIpv4Address", self._HostIpv4Address)
            apiMethodParms.AppendKeyValue("HostIpPort", self._HostIpPort)
            apiMethodParms.AppendKeyValue("CPath", self._CPath)
            apiMethodParms.AppendKeyValue("Version", self._Version)
            apiMethodParms.AppendKeyValue("Uri", self._Uri)
            _logsi.LogMethodParmList(SILevel.Verbose, "Disconnecting device from Spotify Connect", apiMethodParms)
            
            # execute spotify zeroconf api request.
            response = requests.post(
                self._Uri,
                timeout=10,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                data={
                    'action': 'resetUsers',
                    'VERSION': self._Version,
                }
            )

            # check response for errors, and return json response.
            responseData:dict = self._CheckResponseForErrors(response, apiMethodName)

            # process results.
            result = ZeroconfResponse(root=responseData)

            # just in case user tries to issue a connect immediately after this, give the device
            # a little time to reset the connection so the subsequent connect does not fail.
            time.sleep(0.5)

            # trace.
            _logsi.LogObject(SILevel.Verbose, '%s result - type="%s"' % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
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
            ip=self._HostIpv4Address, 
            port=self._HostIpPort, 
            cpath=self._CPath, 
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
            apiMethodParms.AppendKeyValue("HostIpv4Address", self._HostIpv4Address)
            apiMethodParms.AppendKeyValue("HostIpPort", self._HostIpPort)
            apiMethodParms.AppendKeyValue("CPath", self._CPath)
            apiMethodParms.AppendKeyValue("Version", self._Version)
            apiMethodParms.AppendKeyValue("Uri", self._Uri)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get information from Spotify Connect for device", apiMethodParms)
            
            # execute spotify zeroconf api request.
            response = requests.get(
                self._Uri, 
                timeout=10,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                params={
                    'action': 'getInfo',
                    'VERSION': self._Version,
                })
        
            # check response for errors, and return json response.
            responseData:dict = self._CheckResponseForErrors(response, apiMethodName)

            # process results.
            result = ZeroconfGetInfo(root=responseData)

            # trace.
            _logsi.LogObject(SILevel.Verbose, '%s result - type="%s"' % (apiMethodName, type(result).__name__), result, excludeNonPublic=True)
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
        if self._Version is not None: msg = '%s\n Version="%s"' % (msg, str(self._Version))
        return msg 
