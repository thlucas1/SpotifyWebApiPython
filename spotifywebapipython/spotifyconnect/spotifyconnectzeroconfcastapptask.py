# external package imports.
from pychromecast import Chromecast
import threading
import time

# our package imports.
from .spotifyconnectzeroconfcastcontroller import SpotifyConnectZeroconfCastController, TYPE_LAUNCH_ERROR
from spotifywebapipython.spotifywebplayertoken import SpotifyWebPlayerToken
from spotifywebapipython.zeroconfapi import ZeroconfGetInfo, ZeroconfResponse

# get smartinspect logger reference; create a new session for this module name.
from smartinspectpython.siauto import SIAuto, SILevel, SISession, SIColors
import logging

_logsi:SISession = SIAuto.Si.GetSession(__name__)
if (_logsi == None):
    _logsi = SIAuto.Si.AddSession(__name__, True)
_logsi.SystemLogger = logging.getLogger(__name__)


class SpotifyConnectZeroconfCastAppTask(threading.Thread):
    """
    Spotify Connect Zeroconf Cast Application class.
    
    Represents the Cast Application that is started on the Chromecast device
    when a Spotify Connect connection request is made.
    """

    def __init__(
        self, 
        castDevice:Chromecast, 
        spotifyClientInstance, # :SpotifyClient,
        getInfoResponseReceivedCallback,
        zeroconfResponseReceivedCallback,
        transferPlayback:bool=False,
        ) -> None:
        """
        Initializes a new instance of the class.

        Args:
            castDevice (Chromecast):
                Chromecast device target.
            spotifyClientInstance (SpotifyClient):
                SpotifyClient instance used to transfer playback to the Chromecast device.
            getInfoResponseReceivedCallback (function):
                Function to call when a Spotify Connect GetInfoResponse data structure
                has been received from the cast device.
            zeroconfResponseReceivedCallback (function):
                Function to call when a Spotify Connect ZeroconfResponse data structure
                has been received from the cast device.
            transferPlayback (bool):
                True to transfer playback to the device; otherwise, False to just activate
                the Spotify Cast App on the device.
        """
        # invoke base class method.
        super().__init__()

        # note that the initialization method executes in the parent thread;
        # the code in the `run` method executes on a child (daemon) thread.

        # set thread name before we start logging.
        self.name = "Spotify Connect Zeroconf Cast App Task: \"%s\"" % castDevice.name

        # trace.
        _logsi.LogVerbose("%s - Initializing storage" % (self.name))

        # initialize storage.
        self._CastDevice:Chromecast = castDevice
        self._GetInfoResponseReceivedCallback = getInfoResponseReceivedCallback
        self._IsStopRequested:bool = False
        self._SpotifyConnectZeroconfCastController:SpotifyConnectZeroconfCastController = None
        self._SpotifyClientInstance = spotifyClientInstance
        self._TransferPlayback:bool = transferPlayback
        self._ZeroconfResponseReceivedCallback = zeroconfResponseReceivedCallback


    @property
    def CastDevice(self) -> Chromecast:
        """ 
        Returns the Chromecast device instance if one has been initialized; 
        otherwise, None.
        """
        return self._CastDevice


    @property
    def IsStopRequested(self) -> bool:
        """ 
        Indicator used to denote the task has been asked to stop by the main thread.
        """
        return self._IsStopRequested

    @IsStopRequested.setter
    def IsStopRequested(self, value:bool):
        """ 
        Sets the IsStopRequested property value.
        """
        if isinstance(value, bool):
            self._IsStopRequested = value


    @property
    def SpotifyClientInstance(self) -> object: # SpotifyClient:
        """ 
        SpotifyClient instance used to transfer playback to the Chromecast device.
        """
        return self._SpotifyClientInstance


    @property
    def TransferPlayback(self) -> bool:
        """ 
        True to transfer playback to the device; 
        otherwise, False to just activate the Spotify Cast App on the device.
        """
        return self._TransferPlayback


    def _CallGetInfoResponseReceivedCallback(
        self,
        zcResponse:ZeroconfGetInfo=None,
        ) -> None:
        """
        Executes the callback to process the zeroconf getInfo response from the cast app task.

        Args:
            zcResponse (ZeroconfGetInfo):
                Zeroconf getInfo response object.
        """
        # was the callback defined?
        if (self._GetInfoResponseReceivedCallback):

            try:

                # trace.
                _logsi.LogVerbose("%s - Zeroconf getInfoResponse received; Spotify Connect info: \"%s\" (%s)" % (self.name, zcResponse.RemoteName, zcResponse.DeviceId))

                # invoke callback to process the GetInfoResponse data.
                self._GetInfoResponseReceivedCallback(self._CastDevice.uuid, zcResponse)

            except Exception as ex:

                # trace.
                _logsi.LogException("An unhandled exception occured in GetInfoResponseReceivedCallback: %s" % (str(ex)), ex, logToSystemLogger=False)
                #ignore exceptions, as there is nothing we can do about them!


    def _CallZeroconfResponseReceivedCallback(
        self,
        zcResponse:ZeroconfResponse=None,
        ) -> None:
        """
        Executes the callback to process the various zeroconf responses from the cast app task.

        Args:
            zcResponse (ZeroconfResponse):
                Zeroconf response object.
        """
        # was the callback defined?
        if (self._ZeroconfResponseReceivedCallback):

            try:

                # trace.
                _logsi.LogVerbose("%s - Zeroconf \"%s\" received; Spotify Connect response: \"%s\" (%s)" % (self.name, zcResponse.ResponseSource, zcResponse.StatusString, zcResponse.Status))

                # invoke callback to process the ZeroconfResponse data.
                self._ZeroconfResponseReceivedCallback(self._CastDevice.uuid, zcResponse)

            except Exception as ex:

                # trace.
                _logsi.LogException("An unhandled exception occured in ZeroconfResponseReceivedCallback: %s" % (str(ex)), ex, logToSystemLogger=False)
                #ignore exceptions, as there is nothing we can do about them!


    def run(self):
        """
        The task to perform on a seperate thread.

        Note that any exceptions must be processed via a call to _PostLaunchErrorEvent, if you 
        want the exception to be see by the user; just raising an exception will only log it!
        """
        try:

            # trace.
            _logsi.LogVerbose("%s - Starting thread RUN / TASK method" % (self.name))
            _logsi.LogThread(SILevel.Debug, "%s - Thread information" % (self.name), self)

            # start the connection worker thread, if needed.
            # failure to do this will result in the following exception being thrown when
            # the `launch_app()` method is called:
            # - `pychromecast.error.NotConnected: Chromecast unknown:8009 is connecting...`
            if (self._CastDevice.is_idle):
                if (self._CastDevice.socket_client is not None) and (self._CastDevice.socket_client.first_connection):
                    _logsi.LogVerbose("%s - Starting Chromecast connection worker thread for loginId \"%s\"" % (self.name, self.SpotifyClientInstance.SpotifyConnectLoginId))
                    self._CastDevice.start()
                    self._CastDevice.wait(10)

            # get spotify chromecast app access token info from spotify web player cookie credentials.
            # if token already retrieved and has not expired, then use it; otherwise, retrieve it.
            tokenWP:SpotifyWebPlayerToken = self.SpotifyClientInstance._SpotifyWebPlayerToken
            if (tokenWP is not None) and (not tokenWP.IsExpired):
                _logsi.LogVerbose("%s - Using existing Spotify Web Player authorization token for loginId \"%s\"" % (self.name, self.SpotifyClientInstance.SpotifyConnectLoginId), colorValue=SIColors.Gold)
            else:
                _logsi.LogVerbose("%s - Converting Spotify Web Player cookie credentials to an authorization token for loginId \"%s\"" % (self.name, self.SpotifyClientInstance.SpotifyConnectLoginId), colorValue=SIColors.Gold)
                tokenWP = SpotifyWebPlayerToken(profileId=self.SpotifyClientInstance.SpotifyConnectLoginId,
                                                tokenStorageDir=self.SpotifyClientInstance.TokenStorageDir,
                                                tokenStorageFile=self.SpotifyClientInstance.TokenStorageFile,
                                                spotifyWebPlayerCookieSpdc=self.SpotifyClientInstance.SpotifyWebPlayerCookieSpdc,
                                                spotifyWebPlayerCookieSpkey=self.SpotifyClientInstance.SpotifyWebPlayerCookieSpkey)
                self.SpotifyClientInstance._SpotifyWebPlayerToken = tokenWP

            # launch spotify chromecast app on the device, passing it the spotify web player access token info.
            _logsi.LogVerbose("%s - Launching Spotify Chromecast App for loginId \"%s\"" % (self.name, self.SpotifyClientInstance.SpotifyConnectLoginId))
            self._SpotifyConnectZeroconfCastController = SpotifyConnectZeroconfCastController(self._CastDevice, tokenWP.AccessToken, tokenWP.ExpiresAt)
            self._CastDevice.register_handler(self._SpotifyConnectZeroconfCastController)
            self._SpotifyConnectZeroconfCastController.launch_app(10)

            # at this point the cast app should be either fully launched, or an error
            # occured while trying to launch.

            # did an error occur?
            if (not self._SpotifyConnectZeroconfCastController.isLaunched):

                # was it a launchError or getInfoError?
                if (not self._SpotifyConnectZeroconfCastController.isAddUserError):
                    self._CallZeroconfResponseReceivedCallback(self._SpotifyConnectZeroconfCastController.zeroconfResponse)
                    _logsi.LogException("%s - Failed to launch spotify controller due to timeout" % (self.name), None, logToSystemLogger=False)
                    return

                # if getInfoResponse was received, then execute callback to process the getInfoResponse.
                if (not self._SpotifyConnectZeroconfCastController.isGetInfoError) and (self._SpotifyConnectZeroconfCastController.zeroconfGetInfo is not None):
                    self._CallGetInfoResponseReceivedCallback(self._SpotifyConnectZeroconfCastController.zeroconfGetInfo)

                # was it a addUserError? if so, then sp_dc / sp_key credentials are probably bad.
                if (self._SpotifyConnectZeroconfCastController.isAddUserError):
                    self._CallZeroconfResponseReceivedCallback(self._SpotifyConnectZeroconfCastController.zeroconfResponse)
                    _logsi.LogException("%s - Failed to launch spotify controller due to credentials error" % (self.name), None, logToSystemLogger=False)
                    return

            # at this point the cast app launch was successful; the following steps were performed:
            # - issues a Spotify Connect Zeroconf `getInfo` request to retrieve info about the device.
            # - waits for a `getInfoResponse` message and processes the results.
            # - issues a Spotify Connect Zeroconf `addUser` request to login the user to Spotify Connect.
            # - waits for a `addUserResponse` (or `addUserError`) message and processes the results.

            # at this point, the Spotify Connect `getInfo` has been made and the results
            # populated; note that `getInfo` results are the same BEFORE the call to `addUser` 
            # as well as AFTER the call to `addUser` (no need to call `getInfo` again AFTER addUser).

            # call the callback to process the getInfoResponse.
            self._CallGetInfoResponseReceivedCallback(self._SpotifyConnectZeroconfCastController.zeroconfGetInfo)

            # call the callback to process the addUserResponse.
            self._CallZeroconfResponseReceivedCallback(self._SpotifyConnectZeroconfCastController.zeroconfResponse)

            # trace.
            _logsi.LogVerbose("%s - User is logged in to Spotify Cast App; waiting for transfer playback ..." % (self.name))

            # was transfer playback selected?
            if (self.TransferPlayback == True):

                # transfer playback to the Chromecast device.
                _logsi.LogVerbose("%s - Transferring playback for loginId \"%s\"" % (self.name, self.SpotifyClientInstance.SpotifyConnectLoginId))
                deviceId:str = self._SpotifyConnectZeroconfCastController.zeroconfGetInfo.DeviceId
                self.SpotifyClientInstance.PlayerTransferPlayback(deviceId, play=True, refreshDeviceList=False)

                # the cast device will receive a Chromecast message of payload type `transferSuccess`
                # on successful transfer of playback; this will set the `isPlaybackTransferred` flag to True.

            # wait for the launched spotify app to receive transfer playback control, either
            # through the `PlayerTransferPlayback` executed above OR from another Spotify Connect 
            # capable player.
            timeout:int = 20
            counter = 0
            while counter < (timeout + 1):
                if (self._SpotifyConnectZeroconfCastController.waitPlaybackTransfer.wait(1)):
                    if (self._SpotifyConnectZeroconfCastController.isPlaybackTransferError):
                        self._PostLaunchErrorEvent(1001, "Playback transfer error: %s" % (self._SpotifyConnectZeroconfCastController.zeroconfResponse.StatusString))
                        return
                    break
                if (counter >= timeout):
                    self._PostLaunchErrorEvent(1002, "Playback transfer error - Timed out waiting for playback transfer to device.")
                    return
                counter += 1

            # update task status.
            _logsi.LogVerbose("%s - Transfer Playback complete for loginId \"%s\"" % (self.name, self.SpotifyClientInstance.SpotifyConnectLoginId))

            # call the callback to process the transferSuccess or transferError.
            self._CallZeroconfResponseReceivedCallback(self._SpotifyConnectZeroconfCastController.zeroconfResponse)

            # event loop; we have to keep this thread active in order to keep the 
            # Spotify App on the Chromecast device active and available.
            while True:
                
                # keep going until we are asked to stop.
                if (self.IsStopRequested):
                    _logsi.LogVerbose("%s - Thread task stop requested" % (self.name))
                    break
                time.sleep(0.50)

            # trace.
            _logsi.LogVerbose("%s - Thread task was stopped" % (self.name))
        
        except Exception as ex:

            # post launchError event with exception details.
            # this will also log a trace message.
            self._PostLaunchErrorEvent(1000, str(ex))

            # trace.
            _logsi.LogVerbose("%s - Thread task is ending due to exception" % (self.name))

            #ignore exceptions, as there is nothing we can do about them!

        finally:

            try:
                # stop the cast app on the device.
                # this will logout the current user from Spotify Connect Zeroconf as well.
                if (self._SpotifyConnectZeroconfCastController is not None):
                    _logsi.LogVerbose("%s - Stopping Cast App" % (self.name))
                    self._SpotifyConnectZeroconfCastController.tear_down()
            except:
                pass


    def _PostLaunchErrorEvent(
        self,
        returnCode:int,
        message:str
        ) -> None:
        """
        Formats a `launchError` Zeroconf Response, and executes the callback.
        """
        try:

            # trace.
            _logsi.LogError("%s - LaunchError event; (%s) %s" % (self.name, returnCode, message), logToSystemLogger=False)

            # post launchError event with error details.
            response:ZeroconfResponse = ZeroconfResponse()
            response.ResponseSource = TYPE_LAUNCH_ERROR
            response.Status = returnCode
            response.StatusString = message
            self._CallZeroconfResponseReceivedCallback(response)

        except:

            # ignore exceptions, as there is nothing we can do about them.
            pass
