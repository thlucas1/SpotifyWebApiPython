# external package imports.
from __future__ import annotations
import hashlib
import json
import pychromecast
from pychromecast import Chromecast
from pychromecast.controllers import BaseController
import requests
import threading

# our package imports.
from .spotifyconnectzeroconfexceptions import SpotifyConnectZeroconfLaunchError
from spotifywebapipython import SpotifyApiError
from spotifywebapipython.saappmessages import SAAppMessages
from spotifywebapipython.zeroconfapi import SpotifyZeroconfApiError, ZeroconfGetInfo, ZeroconfResponse
from spotifywebapipython.const import (
    SPOTIFY_API_AUTHORIZE_URL,
    SPOTIFY_API_TOKEN_URL,
    SPOTIFY_DESKTOP_APP_CLIENT_ID,
    TRACE_METHOD_RESULT,
)

# get smartinspect logger reference; create a new session for this module name.
from smartinspectpython.siauto import SIAuto, SILevel, SISession, SIMethodParmListContext
import logging

_logsi:SISession = SIAuto.Si.GetSession(__name__)
if (_logsi == None):
    _logsi = SIAuto.Si.AddSession(__name__, True)
_logsi.SystemLogger = logging.getLogger(__name__)

# constants.
APP_SPOTIFY = "CC32E753"
APP_NAMESPACE = "urn:x-cast:com.spotify.chromecast.secure.v1"
TYPE_GET_INFO = "getInfo"
TYPE_GET_INFO_ERROR = "getInfoError"
TYPE_GET_INFO_RESPONSE = "getInfoResponse"
TYPE_ADD_USER = "addUser"
TYPE_ADD_USER_RESPONSE = "addUserResponse"
TYPE_ADD_USER_ERROR = "addUserError"
TYPE_TRANSFER_SUCCESS = "transferSuccess"
TYPE_TRANSFER_ERROR = "transferError"
# not an actual Google Cast zeroconf response; used by this api to denote a launch / config error.
TYPE_LAUNCH_ERROR = "launchError"

SPOTIFY_WEB_API_DEVICEAUTH_REFRESH = "https://spclient.wg.spotify.com/device-auth/v1/refresh"


class SpotifyConnectZeroconfCastController(BaseController):
    """
    Controller to interact with Spotify Connect Zeroconf API.
    """

    def __init__(
        self, 
        castDevice:Chromecast, 
        accessToken:str=None, 
        expiresAt:int=None
        ) -> None:
        """
        Initializes a new instance of the class.

        Args:
            castDevice (CastDevice):
                Chromecast device target.
            accessToken (str):
                Access token provided to the Spotify Web Player application.
            expiresAt (int):
                DateTime (in epoch seconds) that the authorization token will expire.
        """

        # invoke base class method.
        super().__init__(APP_NAMESPACE, APP_SPOTIFY)

        # initialize storage.
        self.accessToken:str = accessToken
        self.castDevice:Chromecast = castDevice
        self.clientId:str = None
        self.expiresAt:int = expiresAt
        self.deviceId:str = None
        self.isAddUserError:bool = False
        self.isGetInfoError:bool = False
        self.isLaunched:bool = False
        self.isPlaybackTransferError:bool = False
        self.isMessageException:bool = False
        self.waitAddUser:threading.Event = threading.Event()
        self.waitGetInfo:threading.Event = threading.Event()
        self.waitPlaybackTransfer:threading.Event = threading.Event()
        self.zeroconfGetInfo:ZeroconfGetInfo = None     # for GetInformation response
        self.zeroconfResponse:ZeroconfResponse = None   # for non-GetInformation responses.

        # clear wait events.
        self.waitAddUser.clear()
        self.waitGetInfo.clear()
        self.waitPlaybackTransfer.clear()


    def launch_app(self, 
                   timeout:int=15,
                   timeoutTransfer:int=20):
        """
        Launch Spotify Cast Application on the remote cast device.

        Args:
            timeout (int):
                Number of seconds to wait for the Spotify cast app to be
                launched on the Chromecast device.
            timeoutTransfer (int):
                Number of seconds to wait for the Spotify cast app to receive
                playback control on the Chromecast device.

        Launches the spotify controller and returns when it's ready.
        To actually play media, another application using spotify
        connect is required.

        Will raise a SpotifyConnectZeroconfLaunchError exception if there is no 
        response from the Spotify app within timeout seconds.

        Will raise a SpotifyConnectZeroconfLaunchError exception if player transfer 
        has not been completed to the Spotify app within timeoutTransfer seconds.

        """
        # validations.
        if self.accessToken is None or self.expiresAt is None:
            raise ValueError("accessToken and expiresAt cannot be empty")
        
        # initialize launch variables.
        self.deviceId = None
        self.isLaunched = False
        self.isAddUserError = False
        self.isGetInfoError = False
        self.isPlaybackTransferError = False
        self.isMessageException = False
        self.waitAddUser.clear()
        self.waitGetInfo.clear()
        self.waitPlaybackTransfer.clear()

        def callback(*_):
            """
            Callback function
            """
            # send the initial getInfo request after launching the app.
            # this will trigger an `addUser` request if the getInfo Response was successful.
            self.GetInformation()

        # launch the spotify app on the device.
        # this will perform the following steps, initiated via the callback function:
        # - issues a Spotify Connect Zeroconf `getInfo` request to retrieve info about the device.
        # - waits for a `getInfoResponse` (or `getInfoError`) message and processes the results.
        # - issues a Spotify Connect Zeroconf `addUser` request to login the user to Spotify Connect.
        # - waits for a `addUserResponse` (or `addUserError`) message and processes the results.
        self.launch(callback_function=callback)

        # wait for the launched spotify app to fully initialize.  this occurs when we receive one
        # of the following messages: `addUserResponse`, `addUserError`, `getInfoError`, `launchError`.
        counter = 0
        while counter < (timeout + 1):
            if (self.waitAddUser.wait(1)):
                break
            if (counter >= timeout):
                raise SpotifyZeroconfApiError(0, "Timed out while waiting for a response", "launch_app", "timeout")
            counter += 1

        # check for error conditions.
        if (self.isAddUserError):
            raise SpotifyZeroconfApiError(self.zeroconfResponse.Status, "AddUser request failed", "launch_app", self.zeroconfResponse.StatusString)
        if (self.isGetInfoError):
            raise SpotifyZeroconfApiError(self.zeroconfResponse.Status, "GetInformation request failed", "launch_app", self.zeroconfResponse.StatusString)
        if (not self.isLaunched):
            raise SpotifyConnectZeroconfLaunchError("Spotify Cast App could not be launched")


    def receive_message(
        self, 
        message, 
        data: dict
        ) -> None:
        """
        Called when a message is received from the Spotify cast app.

        Args:
            message (str):
                Message header values; typical keys are:
                - "protocol_version": cast protocol version (e.g. "CASTV2_1_0").
                - "source_id": source application uuid (e.g. "a23351 ... 82ff84").
                - "destination_id": destination id (e.g. "sender-0").
                - "namespace": cast app namespace (e.g. "urn:x-cast:com.spotify.chromecast.secure.v1").
                - "payload_type": payload type (e.g. "STRING").
            data (dict):
                Message payload dictionary; the important keys are:
                - "type": type of payload (e.g. "getInfoResponse", "addUserResponse", "addUserError", etc).
                - "payload": contains specific fields related to the "type" of message. 

        Handle the auth flow and active player selection.
        """
        payloadDataType:str = None
        payloadData:dict = {}

        try:

            # trace.
            _logsi.LogDictionary(SILevel.Verbose, "Chromecast Message received: %s" % message, data, prettyPrint=True)
            
            # message argument example: "getInfoResponse"
            #     protocol_version: CASTV2_1_0
            #     source_id: "a233518a-505f-4d23-abcb-dfce4a82ff84"
            #     destination_id: "sender-0"
            #     namespace: "urn:x-cast:com.spotify.chromecast.secure.v1"
            #     payload_type: STRING
            #     payload_utf8: "{\"type\":\"getInfoResponse\",\"payload\":{\"remoteName\":\"Nest Audio 01\",\"deviceID\":\"bddc ... a3de\",\"deviceAPI_isGroup\":false,\"version\":\"2.9.0\",\"publicKey\":\"empty\",\"deviceType\":\"cast_audio\",\"brandDisplayName\":\"google\",\"modelDisplayName\":\"Google_Home\",\"libraryVersion\":\"5.44.1\",\"resolverVersion\":\"1\",\"groupStatus\":\"NONE\",\"tokenType\":\"accesstoken\",\"clientID\":\"d7d ... eae7\",\"productID\":0,\"scope\":\"streaming\",\"availability\":\"\",\"spotifyError\":0,\"status\":101,\"statusString\":\"OK\"}}"

            # safely get the message payload structure type.
            if (isinstance(data, dict)):
                payloadDataType = data.get("type", None)
                payloadData:dict = data.get("payload", {})

            # process message payload.

            # did getInfo succeed?
            if payloadDataType == TYPE_GET_INFO_RESPONSE:

                # example payload response (Nest Speaker):
                # { 'type': 'getInfoResponse',
                #   'payload': { 'remoteName': 'Nest Audio 01',
                #                'deviceID': 'bddc7 ...',
                #                'deviceAPI_isGroup': False,
                #                'version': '2.9.0',
                #                'publicKey': 'empty',
                #                'deviceType': 'cast_audio',
                #                'brandDisplayName': 'google',
                #                'modelDisplayName': 'Google_Home',
                #                'libraryVersion': '5.44.1',
                #                'resolverVersion': '1',
                #                'groupStatus': 'NONE',
                #                'tokenType': 'accesstoken',
                #                'clientID': 'd7df0 ...',
                #                'productID': 0,
                #                'scope': 'streaming',
                #                'availability': '',
                #                'spotifyError': 0,
                #                'status': 101,
                #                'statusString': 'OK'}}

                # example payload response (Cast Group):
                # { 'type': 'getInfoResponse',
                #   'payload': { 'remoteName': 'Nest Group 01',
                #                'deviceID': 'c40cf ...',
                #                'deviceAPI_isGroup': True,
                #                'version': '2.9.0',
                #                'publicKey': 'empty',
                #                'deviceType': 'cast_audio',
                #                'brandDisplayName': 'google',
                #                'modelDisplayName': 'Google_Home',
                #                'libraryVersion': '5.48.2',
                #                'resolverVersion': '1',
                #                'groupStatus': 'GROUP',
                #                'tokenType': 'accesstoken',
                #                'clientID': 'd7df0 ...',
                #                'productID': 0,
                #                'scope': 'streaming',
                #                'availability': '',
                #                'spotifyError': 0,
                #                'status': 101,
                #                'statusString': 'OK'}}

                # process message payload data.
                self.zeroconfGetInfo = ZeroconfGetInfo(payloadData)
                if (self.zeroconfGetInfo.PublicKey == 'empty'):
                    self.zeroconfGetInfo.PublicKey = None
                self.zeroconfGetInfo.ResponseSource = payloadDataType

                # trace.
                _logsi.LogObject(SILevel.Verbose, "GetInformation result (ZeroconfGetInfo) - \"%s\" (%s)" % (self.zeroconfGetInfo.RemoteName, self.zeroconfGetInfo.DeviceId), self.zeroconfGetInfo, excludeNonPublic=True)

                # getInfo response received from the initial launch.
                self.deviceId = self.zeroconfGetInfo.DeviceId
                self.clientId = self.zeroconfGetInfo.ClientId

                # set status indicators and events.
                self.isGetInfoError = False
                self.waitGetInfo.set()

                # if cast app is already launched, then we are done.
                if (self.isLaunched):
                    return True
                
                # otherwise, we are still in the process of launching the cast app via the callback.
                # we will now send the initial addUser request to login to Spotify Connect, and
                # we will wait for a response in the post-launch code.
                self.AddUser()
                return True

            # did getInfo fail?
            if payloadDataType == TYPE_GET_INFO_ERROR:

                # example payload response (Nest Speaker):
                # { 'type': 'getInfoError',
                #   'payload': { 'status': 303,
                #                'statusString': 'ERROR-INVALID-ARGUMENTS',
                #                'spotifyError': 0}}

                # process message payload data.
                self.zeroconfResponse = ZeroconfResponse(payloadData)
                self.zeroconfResponse.ResponseSource = payloadDataType

                # set status indicators and events.
                self.isGetInfoError = True
                self.deviceId = None
                self.waitGetInfo.set()
                if (not self.isLaunched):
                    # if app is not launched, then init is waiting on the `waitAddUser` event!
                    self.waitAddUser.set()
                return True

            # did addUser succeed?
            if payloadDataType == TYPE_ADD_USER_RESPONSE:

                # example payload response (Nest Speaker):
                # { 'type': 'addUserResponse',
                #   'payload': { 'status': 101,
                #                'statusString': 'OK',
                #                'spotifyError': 0,
                #                'user': {'id': '31l77 ...'},
                #                'deviceId': 'bddc ...'}}

                # process message payload data.
                self.zeroconfResponse = ZeroconfResponse(payloadData)
                self.zeroconfResponse.ResponseSource = payloadDataType

                try:
                    # stash the `user` value into the getInfo `ActiveUser` property as well.
                    if (self.zeroconfGetInfo.ActiveUser is None) or (self.zeroconfGetInfo.ActiveUser == ""):
                        self.zeroconfGetInfo.ActiveUser = payloadData["user"]["id"]
                except:
                    pass  # ignore errors.

                # set status indicators and events.
                self.isAddUserError = False
                self.isLaunched = True
                self.waitAddUser.set()
                return True

            # did addUser fail?
            if payloadDataType == TYPE_ADD_USER_ERROR:

                # example payload response (Nest Speaker):
                # { 'type': 'addUserError',
                #   'payload': { 'status': 303,
                #                'statusString': 'ERROR-INVALID-ARGUMENTS',
                #                'spotifyError': 0}}

                # process message payload data.
                self.zeroconfResponse = ZeroconfResponse(payloadData)
                self.zeroconfResponse.ResponseSource = payloadDataType

                # set status indicators and events.
                self.isAddUserError = True
                self.deviceId = None
                self.waitAddUser.set()
                return True

            # was playback transferred to the device?
            if payloadDataType == TYPE_TRANSFER_SUCCESS:

                # example payload response (Nest Speaker):
                # { 'type': 'transferSuccess',
                #   'payload': { 'status': 101,
                #                'statusString': 'OK',
                #                'spotifyError': 0}}

                # process message payload data.
                self.zeroconfResponse = ZeroconfResponse(payloadData)
                self.zeroconfResponse.ResponseSource = payloadDataType

                # set status indicators and events.
                self.isPlaybackTransferError = False
                self.waitPlaybackTransfer.set()
                return True

            # did an error occur transferring playback to the device?
            if payloadDataType == TYPE_TRANSFER_ERROR:

                # example payload response (Nest Speaker):
                # { 'type': 'transferError',
                #   'payload': { 'status': 402,
                #                'statusString': 'ERROR-SPOTIFY-ERROR',
                #                'spotifyError': 408}}

                # process message payload data.
                self.zeroconfResponse = ZeroconfResponse(payloadData)
                self.zeroconfResponse.ResponseSource = payloadDataType

                # set status indicators and events.
                self.isPlaybackTransferError = True
                self.waitPlaybackTransfer.set()
                return True

            # trace.
            _logsi.LogDictionary(SILevel.Verbose, "Chromecast Message ignored - payload type value not recognized: \"%s\"" % (payloadDataType), message, prettyPrint=True)

            return True

        except Exception as ex:

            # load zeroconfResponse instance with exception information.
            response: ZeroconfResponse = ZeroconfResponse()
            response.SpotifyError = 0
            response.Status = 1000
            response.StatusString = "ERROR-CHROMECAST-RECEIVE-MESSAGE"
            response.ResponseSource = "SpotifyConnectZeroconfCastController"
            self.zeroconfResponse = response

            # trace.
            _logsi.LogException(SAAppMessages.UNHANDLED_EXCEPTION.format("receive_message", str(ex)), ex, logToSystemLogger=False)

            # ignore exceptions, as there is nothing we can do at this point.


    def getSpotifyDeviceID(self) -> str:
        """
        Retrieve the Spotify deviceID from provided chromecast info
        """
        deviceId:str = hashlib.md5(self.castDevice.cast_info.friendly_name.encode()).hexdigest()
        return deviceId


    def AddUser(
        self,
        timeout:int=10,
        ) -> None:
        """
        Calls the `addUser` Spotify Zeroconf API endpoint to login the user to Spotify Connect.
        
        Args:
            timeout (int):
                Max time to wait (in seconds) for a response to the request.  
                Only applies if the `isLaunched=False`.

        Raises:
            SpotifyZeroconfApiError: 
                If the Spotify Zeroconf API request response contains error information.
                
        The request will timeout after the specified `timeout` value, and an exception raised if the 
        device cannot be reached or does not respond within that time frame.
        </details>
        """
        apiMethodName:str = 'AddUser'
        apiMethodParms:SIMethodParmListContext = None
        tracePrefix:str = 'Spotify Web Player Device Auth Token Refresh'
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("timeout", timeout)
            _logsi.LogMethodParmList(SILevel.Verbose, "Add User to Spotify Connect Chromecast Zeroconf API (ip=%s:%s)" % (self.castDevice.socket_client.host, self.castDevice.socket_client.port), apiMethodParms)

            # validations.
            if (timeout is None):
                timeout=10

            # clear wait event.
            self.waitAddUser.clear()
            self.addUserError = False

            # prepare to refresh the access token.
            reqHeaders = {
                "authority": "spclient.wg.spotify.com",
                "authorization": "Bearer {}".format(self.accessToken),
                "content-type": "text/plain;charset=UTF-8",
            }
            reqParms = json.dumps(
                {
                    "clientId": self.clientId, 
                    "deviceId": self.deviceId
                }
            )

            # trace.
            _logsi.LogVerbose("Refreshing Spotify web player device authorization token")
            _logsi.LogDictionary(SILevel.Debug, "%s http request: \"%s\" (headers)" % (tracePrefix, SPOTIFY_WEB_API_DEVICEAUTH_REFRESH), reqHeaders)
            _logsi.LogText(SILevel.Verbose, "%s http request: \"%s\" (parms)" % (tracePrefix, SPOTIFY_WEB_API_DEVICEAUTH_REFRESH), reqParms)

            # refresh the authorization token.
            response = requests.post(
                SPOTIFY_WEB_API_DEVICEAUTH_REFRESH,
                headers=reqHeaders,
                data=reqParms,
            )

            # trace.
            if _logsi.IsOn(SILevel.Debug):
                _logsi.LogObject(SILevel.Debug, "%s http response object - type=\"%s\", module=\"%s\"" % (tracePrefix, type(response).__name__, type(response).__module__), response)

            # trace.
            if _logsi.IsOn(SILevel.Debug):
                _logsi.LogObject(SILevel.Debug, "%s http response [%s-%s] (response)" % (tracePrefix, response.status_code, response.reason), response)
                if (response.headers):
                    _logsi.LogCollection(SILevel.Debug, "%s http response [%s-%s] (headers)" % (tracePrefix, response.status_code, response.reason), response.headers.items())

            # process json response data.
            json_resp = response.json()

            # send the Spotify Connect Zeroconf `addUser` request.
            # send request to cast app.
            # this will login to the device, which (if successful) will cause the
            # device to be registered to Spotify Connect Zeroconf as well as appear
            # in the Spotify Player device list.
            castMsg:dict = {
                "type": TYPE_ADD_USER,
                "payload": {
                    "blob": json_resp["accessToken"],
                    "tokenType": "accesstoken",
                },
            }
            _logsi.LogDictionary(SILevel.Debug, "Sending Spotify Connect Zeroconf AddUser message to Chromecast device (ip=%s:%s)" % (self.castDevice.socket_client.host, self.castDevice.socket_client.port), castMsg, prettyPrint=True)
            self.send_message(castMsg)

            # if we are in the process of launching, then we will wait for a response in the
            # post-launch code as we are still in the launch callback sequence.
            if (not self.isLaunched):
                return
            
            # if we are NOT in the process of launching, then we will wait for a response here.
            counter = 0
            while counter < (timeout + 1):
                if (self.waitAddUser.wait(1)):
                    if (self.isAddUserError):
                        raise SpotifyZeroconfApiError(self.zeroconfResponse.Status, "AddUser request failed", "AddUser", self.zeroconfResponse.StatusString)
                    break
                if (counter >= timeout):
                    raise SpotifyZeroconfApiError(0, "Timed out while waiting for a response", "AddUser", "timeout")
                counter += 1

            # if we make it here, then addUser request was processed successfully.
            return

        except SpotifyZeroconfApiError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def GetInformation(
        self,
        timeout:int=10,
        ) -> ZeroconfGetInfo:
        """
        Calls the `getInfo` Spotify Zeroconf API endpoint to return information about the device.
        
        Args:
            timeout (int):
                Max time to wait (in seconds) for a response to the request.  
                Only applies if the `isLaunched=False`.

        Returns:
            A `ZeroconfGetInfo` object that indicates success or failure (see notes below), as well
            as the device information.

        Raises:
            SpotifyZeroconfApiError: 
                If the Spotify Zeroconf API request response contains error information.
                
        The request will timeout after the specified `timeout` value, and an exception raised if the 
        device cannot be reached or does not respond within that time frame.
        """
        apiMethodName:str = 'GetInformation'
        apiMethodParms:SIMethodParmListContext = None
        result:ZeroconfGetInfo = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("timeout", timeout)
            _logsi.LogMethodParmList(SILevel.Verbose, "Get information from Spotify Connect Chromecast Zeroconf API (ip=%s:%s)" % (self.castDevice.socket_client.host, self.castDevice.socket_client.port), apiMethodParms)

            # validations.
            if (timeout is None):
                timeout=10

            # clear wait event.
            self.waitGetInfo.clear()
            self.isGetInfoError = False

            # determine if this is a cast group or not.
            isGroup:bool = (self.castDevice.model_name == "Google Cast Group")

            # send request to cast app.
            castMsg:dict = {
                "type": TYPE_GET_INFO,
                "payload": {
                    "remoteName": self.castDevice.cast_info.friendly_name,
                    "deviceID": self.getSpotifyDeviceID(),
                    "deviceAPI_isGroup": isGroup,
                },
            }
            _logsi.LogDictionary(SILevel.Debug, "Sending Spotify Connect Zeroconf Getinformation message to Chromecast device (ip=%s:%s)" % (self.castDevice.socket_client.host, self.castDevice.socket_client.port), castMsg, prettyPrint=True)
            self.send_message(castMsg)

            # if we are in the process of launching, then we will wait for a response in the
            # post-launch code as we are still in the launch callback sequence.
            if (not self.isLaunched):
                return True

            # if we are NOT in the process of launching, then we will wait for a response here.
            counter = 0
            while counter < (timeout + 1):
                if (self.waitGetInfo.wait(1)):
                    if (self.isGetInfoError):
                        raise SpotifyZeroconfApiError(self.zeroconfGetInfo.Status, "GetInformation request failed", "GetInformation", self.zeroconfGetInfo.StatusString)
                    break
                if (counter >= timeout):
                    raise SpotifyZeroconfApiError(0, "Timed out while waiting for a response", "GetInformation", "timeout")
                counter += 1

            # if we make it here, then getInfo request was processed successfully.
            # return response to the caller.
            return self.zeroconfGetInfo

        except SpotifyZeroconfApiError: raise  # pass handled exceptions on thru
        except Exception as ex:
            
            # format unhandled exception.
            raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format(apiMethodName, str(ex)), ex, logsi=_logsi)

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)
