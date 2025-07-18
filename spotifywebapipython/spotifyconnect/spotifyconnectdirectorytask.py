# external package imports.
from abc import abstractmethod
from collections.abc import Mapping
import copy
from datetime import datetime
import hashlib
from pychromecast import CastBrowser, CastInfo, Chromecast, get_chromecast_from_cast_info, get_chromecast_from_host
from pychromecast.dial import MultizoneInfo, MultizoneStatus, get_multizone_status
#from pychromecast.controllers.multizone import MultizoneController
from pychromecast.const import CAST_TYPE_GROUP
import socket
from soco import SoCo
import threading
import time
from uuid import UUID
from zeroconf import Zeroconf, ServiceBrowser

# our package imports.
from .spotifyconnectzeroconfexceptions import SpotifyConnectDeviceNotFound
from .spotifyconnectzeroconfcastapptask import SpotifyConnectZeroconfCastAppTask
from .spotifyconnectzeroconfcastlistener import SpotifyConnectZeroconfCastListener
#from .spotifyconnectzeroconfcastmultizonelistener import SpotifyConnectZeroconfCastMultiZoneListener
from .spotifyconnectdeviceeventargs import SpotifyConnectDeviceEventArgs
from .spotifyconnectzeroconflistener import ZEROCONF_SERVICETYPE_SPOTIFYCONNECT, SpotifyConnectZeroconfListener
from .spotifyconnectzeroconfcastcontroller import (
    TYPE_ADD_USER_RESPONSE,
    TYPE_ADD_USER_ERROR,
    TYPE_GET_INFO_ERROR,
    TYPE_LAUNCH_ERROR,
    TYPE_TRANSFER_ERROR,
    TYPE_TRANSFER_SUCCESS
    )
# note - cannot reference `SpotifyClient` due to circular import!
# from spotifywebapipython import SpotifyClient
from spotifywebapipython import SpotifyApiError
from spotifywebapipython.models import Device, PlayerPlayState, SpotifyConnectDevices, SpotifyConnectDevice, ZeroconfDiscoveryResult
from spotifywebapipython.saappmessages import SAAppMessages
from spotifywebapipython.sautils import Event, validateDelay
from spotifywebapipython.zeroconfapi import ZeroconfGetInfo, ZeroconfConnect, ZeroconfResponse

# get smartinspect logger reference; create a new session for this module name.
from smartinspectpython.siauto import SIAuto, SILevel, SISession, SIMethodParmListContext, SIColors
import logging

_logsi:SISession = SIAuto.Si.GetSession(__name__)
if (_logsi == None):
    _logsi = SIAuto.Si.AddSession(__name__, True)
_logsi.SystemLogger = logging.getLogger(__name__)


class SpotifyConnectDirectoryTask(threading.Thread):
    """
    Spotify Connect Directory thread task.

    This class discovers available Spotify Connect devices on the local network.
    Discovered devices are then added to an internal list, which can be referenced
    by clients.

    The directory task is started immediately after the authorization token is
    established in the SpotifyClient object.
    """

    def __init__(
        self, 
        spotifyClientInstance, # :SpotifyClient,
        zeroconfInstance:Zeroconf=None,
        initialDiscoveryTimeout:float=3.0,
        ) -> None:
        """
        Initializes a new instance of the class.

        Args:
            spotifyClientInstance (SpotifyClient):
                SpotifyClient instance used to interface with the Spotify Web API.
            zeroconfInstance (Zeroconf):
                Zeroconf instance used to query zeroconf; otherwise, None to
                create a new zeroconf instance.
            initialDiscoveryTimeout (float):
                Time (in seconds) to give child Zeroconf discovery threads time to process
                initial Zeroconf service information changes.
                Default is 3.

        The `initialDiscoveryTimeout` argument gives the child Zeroconf discovery threads 
        time to process initial Zeroconf service information changes prior to setting the 
        `WaitForInitComplete` event as complete.  This gives the directory thread task 
        time to discover all of the Spotify Connect devices currently attached to the 
        local network.
        """
        # invoke base class method.
        super().__init__()

        # note that the initialization method executes in the parent thread;
        # the code in the `run` method executes on a child (daemon) thread.

        # set thread name before we start logging.
        self.name = "Spotify Connect Directory Task"

        # validations.
        if (spotifyClientInstance is None):
            raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % ("__init__", 'spotifyClientInstance'), logsi=_logsi)
        if (spotifyClientInstance.SpotifyConnectLoginId is None) or (spotifyClientInstance.SpotifyConnectLoginId.strip() == ""):
            raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % ("__init__", 'spotifyClientInstance.SpotifyConnectLoginId'), logsi=_logsi)
        if (not isinstance(initialDiscoveryTimeout, float)) and (not isinstance(initialDiscoveryTimeout, int)):
            initialDiscoveryTimeout = 3.0

        # initialize storage.
        self._CastAppTasks:Mapping[str, SpotifyConnectZeroconfCastAppTask] = {}
        self._CastBrowser:CastBrowser = None
        #self._CastMultiZoneControllers:Mapping[str, MultizoneController] = {}
        self._InitialDiscoveryTimeout = initialDiscoveryTimeout
        self._IsStopRequested:bool = False
        self._SonosPlayers:dict = {}
        self._SpotifyClientInstance = spotifyClientInstance
        self._SpotifyConnectBrowser:ServiceBrowser = None
        self._SpotifyConnectDevices:SpotifyConnectDevices = SpotifyConnectDevices()
        self._SpotifyConnectDevices_RLock = threading.RLock()   # re-entrant lock to sync access to devices collection.
        self._ZeroconfInstance:Zeroconf = zeroconfInstance
        self._Zeroconf_RLock = threading.RLock()   # re-entrant lock to sync access to zeroconf service state changes.

        # define all events raised by this class.
        self.DeviceAdded = Event()
        """
        Event raised when a Spotify Connect device entry has been added.
        """

        self.DeviceRemoved = Event()
        """
        Event raised when a Spotify Connect device entry has been removed.
        """

        self.DeviceUpdated = Event()
        """
        Event raised when a Spotify Connect device entry has been updated.
        """

        # define all threading events raised by this class.
        self.WaitForInitComplete = threading.Event()
        """
        Event that will be posted when the task has been initialized, and is
        waiting for commands or device notifications.
        """

        self.WaitForActivationComplete = threading.Event()
        """
        Event that will be posted when the task has completed the activation sequence for 
        the device, which is either a `addUserResponse` or `addUserError` notification.
        """

        self.WaitForTransferComplete = threading.Event()
        """
        Event that will be posted when the task has completed the playback transfer sequence for 
        the device, which is either a `transferSuccess` or `transferError` notification.
        """

        # wire up event handlers.
        self.DeviceAdded += self.OnDeviceAdded
        self.DeviceRemoved += self.OnDeviceRemoved
        self.DeviceUpdated += self.OnDeviceUpdated

        # clear event notifiers.
        self.WaitForInitComplete.clear()
        self.WaitForActivationComplete.set()    # indicate activation is complete (initial state).
        self.WaitForTransferComplete.set()      # indicate transfer is complete (initial state).
      

    @property
    def InitialDiscoveryTimeout(self) -> float:
        """ 
        Time to wait (in seconds) after starting the Zeroconf discovery thread
        tasks before marking the directory task initialization as complete.  
        """
        return self._InitialDiscoveryTimeout


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
    def CastAppTasks(self) -> Mapping[str, SpotifyConnectZeroconfCastAppTask]:
        """ 
        Collection of SpotifyConnectZeroconfCastAppTask objects that have been created
        when transferring playback.
        """
        return self._CastAppTasks


    @property
    def CastBrowser(self) -> CastBrowser:
        """ 
        Returns the internal CastBrowser object.
        """
        return self._CastBrowser


    @property
    def IsZeroconDiscoveryEnabled(self) -> bool:
        """ 
        Returns True if Zeroconf discovery is enabled; otherwise, False.
        """
        # is discovery enabled?
        # is zeroconf discovery enabled?
        if (not self.is_alive()):
            return False
        if (self._InitialDiscoveryTimeout == 0):
            return False
        return True
    

    @property
    def SpotifyClientInstance(self) -> object: # SpotifyClient:
        """ 
        Returns the SpotifyClient instance.
        """
        return self._SpotifyClientInstance


    @property
    def ZeroconfInstance(self) -> Zeroconf:
        """ 
        Returns the zeroconf instance.
        """
        return self._ZeroconfInstance
    

    def run(self):
        """
        The task to perform on a seperate thread.
        """
        try:

            # trace.
            _logsi.LogVerbose("%s - Starting thread RUN / TASK method" % (self.name))
            _logsi.LogThread(SILevel.Debug, "%s - Thread information" % (self.name), self)

            # refresh dynamic device list.
            self.RefreshDynamicDevices()

            # is zeroconf discovery enabled?
            if (not self.IsZeroconDiscoveryEnabled):

                _logsi.LogVerbose("%s - Spotify Connect Zeroconf discovery is disabled; only Spotify Web API player devices will be recognized" % (self.name), colorValue=SIColors.Coral)

            else:

                # create new spotify connect zeroconf discovery browser instance.
                # this will discover spotify connect devices on the local network.
                # when a device is found, cast_listener.add_cast is called.
                # when a deviceost, the cast_listener.remove_cast is called
                # when a devicepdated, cast_listener.update_cast is called.
                _logsi.LogVerbose("%s - Starting Spotify Connect Zeroconf discovery browser" % (self.name))
                handler:SpotifyConnectZeroconfListener = SpotifyConnectZeroconfListener(self, self._Zeroconf_RLock)
                self._SpotifyConnectBrowser = ServiceBrowser(
                    self._ZeroconfInstance,
                    ZEROCONF_SERVICETYPE_SPOTIFYCONNECT,
                    handlers=[handler.OnServiceStateChange]
                    )

                # create new chromecast zeroconf discovery browser instance.
                # this will discover Chromecasts on the local network.
                # when a Chromecast is found, cast_listener.add_cast is called.
                # when a Chromecast is lost, the cast_listener.remove_cast is called
                # when a Chromecast is updated, cast_listener.update_cast is called.
                _logsi.LogVerbose("%s - Starting Chromecast Zeroconf discovery browser" % (self.name))
                self._CastBrowser = CastBrowser(
                    zeroconf_instance=self._ZeroconfInstance,
                    cast_listener=SpotifyConnectZeroconfCastListener(self, self._Zeroconf_RLock), 
                    known_hosts=None
                    )
                self._CastBrowser.start_discovery()

                # give child Zeroconf discovery threads time to process initial service information discovery.
                time.sleep(self._InitialDiscoveryTimeout)

            # trace - dump devices discovered initially.
            if (_logsi.IsOn(SILevel.Verbose)):

                # use lock, as zeroconf tasks could be updating the device list.
                with self._Zeroconf_RLock:

                    # trace.
                    _logsi.LogVerbose("%s - Spotify Connect devices discovered at initialization (%s items)" % (self.name, len(self._SpotifyConnectDevices)), colorValue=SIColors.Coral)

                    # trace - log all devices that were discovered initially to SmartInspect console.
                    for scDevice in self._SpotifyConnectDevices.Items:
                        isActive:str = " (active)" if (scDevice.IsActiveDevice) else ""
                        _logsi.LogObject(SILevel.Verbose, "Spotify Connect device: %s [%s]%s - object" % (scDevice.Title, scDevice.DiscoveryResult.Description, isActive), scDevice, excludeNonPublic=True, colorValue=SIColors.Coral)
                        _logsi.LogObject(SILevel.Verbose, "Spotify Connect device: %s [%s]%s - DiscoveryResult" % (scDevice.Title, scDevice.DiscoveryResult.Description, isActive), scDevice.DiscoveryResult, excludeNonPublic=True, colorValue=SIColors.Coral)
                        _logsi.LogObject(SILevel.Verbose, "Spotify Connect device: %s [%s]%s - DeviceInfo / getInfo" % (scDevice.Title, scDevice.DiscoveryResult.Description, isActive), scDevice.DeviceInfo, excludeNonPublic=True, colorValue=SIColors.Coral)

                    # trace - log all devices that were discovered initially to system logger.
                    # (since LogObject does not log to system logger).
                    for scDevice in self._SpotifyConnectDevices.Items:
                        isActive:str = " (active)" if (scDevice.IsActiveDevice) else ""
                        _logsi.LogVerbose("Spotify Connect device: %s [%s]%s" % (scDevice.Title, scDevice.DiscoveryResult.Description, isActive))

            # indicate we are ready for commands.
            self.WaitForInitComplete.set()

            # event loop.
            # note that the directory task must be kept running in order to control Chromecast devices!
            while True:

                try:
                
                    # keep going until we are asked to stop.
                    if (self.IsStopRequested):
                        _logsi.LogVerbose("%s - Thread task stop requested" % (self.name))
                        break
                    time.sleep(0.50)

                except Exception as ex:

                    # trace.
                    _logsi.LogException("%s - Exception: %s" % (str(ex)), ex, logToSystemLogger=False)
                    # ignore exceptions, as we can't do anything about them.

            # at this point we have been requested to stop;
            # loop through all active cast app tasks and unregister handlers.
            # note that this will not stop the Spotify App Task that is running
            # on the device; we don't stop the app because it would remove the
            # Spotify Connect registration.
            castAppTask:SpotifyConnectZeroconfCastAppTask = None
            for castAppTask in self._CastAppTasks.values():
                if (castAppTask.is_alive()):
                    _logsi.LogVerbose("%s - Stopping %s" % (self.name, castAppTask.name))
                    castAppTask.IsStopRequested = True
                    castAppTask.join()

            # trace.
            _logsi.LogVerbose("%s - Thread task was stopped" % (self.name))
        
        except Exception as ex:

            # trace.
            _logsi.LogException("%s - Exception: %s" % (self.name, str(ex)), ex, logToSystemLogger=False)
            _logsi.LogVerbose("%s - Thread task is ending due to exception" % (self.name))
            # ignore exceptions, since we are shutting down.
            
            # indicate we are ready for commands.
            self.WaitForInitComplete.set()

        finally:

            try:

                # unwire event handlers.
                _logsi.LogVerbose("%s - Unwiring event handlers" % (self.name))
                if (self.DeviceAdded is not None):
                    self.DeviceAdded -= self.OnDeviceAdded
                if (self.DeviceRemoved is not None):
                    self.DeviceRemoved -= self.OnDeviceRemoved
                if (self.DeviceUpdated is not None):
                    self.DeviceUpdated -= self.OnDeviceUpdated

            except:

                # trace.
                _logsi.LogException("%s - An unhandled exception occured while unwiring event handlers: %s" % (self.name, str(ex)), ex, logToSystemLogger=False)
                # ignore exceptions, since we are shutting down.

            try:

                # stop spotify connect zeroconf discovery browser.
                if (self._SpotifyConnectBrowser is not None):
                    _logsi.LogVerbose("%s - Stopping Spotify Connect Zeroconf discovery" % (self.name))
                    self._SpotifyConnectBrowser.cancel()
                    _logsi.LogObject(SILevel.Verbose, "%s - ZeroconfInstance object after ServiceBrowser resources released" % (self.name), self._ZeroconfInstance)

            except:

                # trace.
                _logsi.LogException("%s - An unhandled exception occured while stopping Spotify Connect Zeroconf discovery browser: %s" % (self.name, str(ex)), ex, logToSystemLogger=False)
                # ignore exceptions, since we are shutting down.

            try:

                # stop chromecast zeroconf discovery browser.
                if (self._CastBrowser is not None):
                    _logsi.LogVerbose("%s - Stopping Chromecast Zeroconf discovery" % (self.name))
                    self._CastBrowser.stop_discovery()
                    _logsi.LogObject(SILevel.Verbose, "%s - ZeroconfInstance object after CastBrowser resources released" % (self.name), self._ZeroconfInstance)

            except:

                # trace.
                _logsi.LogException("%s - An unhandled exception occured while stopping Chromecast Zeroconf discovery browser: %s" % (self.name, str(ex)), ex, logToSystemLogger=False)
                # ignore exceptions, since we are shutting down.


    def ActivateCastAppSpotify(
        self,
        deviceName:str,
        transferPlayback:bool=False,
        timeoutActivation:float=15.0,
        timeoutTransfer:float=10.0,
        ) -> None:
        """
        Activates the Spotify Cast Application on the specified Chromecast device.

        It will also call the `OnCastGetInfoResponseReceived` method when the Spotify Cast App
        receives a `GetInfoResponse` block that contains Spotify Connect Zeroconf GetInformation 
        data about the device.

        It will also call the `OnCastZeroconfResponseReceived` method when the Spotify Cast App
        receives any of the following message that contain zeroconf response data: `addUserResponse`,
        `addUserError`,  `transferError`, `transferSuccess`.

        Once activated, you have about 20 seconds to transfer playback to the device.
        The Spotify Cast application will automatically end after 20 seconds if playback
        is not transferred to it within the timeout period.  Note that any application can
        be used to transfer playback to the device (Spotify Mobile / Desktop / Web, spotipy,
        spotifywebapipython, etc).

        Args:
            deviceName (str):
                Chromecast device friendly name (or device id) to activate.
            transferPlayback (bool):
                True to transfer playback to the device; otherwise, False to just activate
                the Spotify Cast App on the device.
            timeoutActivation (float):
                Amount of time to wait (in seconds) for the Spotify Cast App to be fully activated,
                the user logged in, and ready for transfer of playback.  
                Default is 15 seconds.
            timeoutTransfer (float):
                If `transferPlayback` argument is True, the amount of time to wait (in seconds)
                for the transfer to complete; otherwise, argument is ignored.  
                Default is 10 seconds.
        """
        apiMethodName:str = "ActivateCastAppSpotify"
        apiMethodParms:SIMethodParmListContext = None

        try:

            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("deviceName", deviceName)
            apiMethodParms.AppendKeyValue("transferPlayback", transferPlayback)
            apiMethodParms.AppendKeyValue("timeoutActivation", timeoutActivation)
            apiMethodParms.AppendKeyValue("timeoutTransfer", timeoutTransfer)
            _logsi.LogMethodParmList(SILevel.Verbose, "Activating Spotify App on Chromecast device: \"%s\"" % (deviceName), apiMethodParms)

            # validations.
            timeoutActivation = validateDelay(timeoutActivation, 15.0, 30.0)
            timeoutTransfer = validateDelay(timeoutTransfer, 10.0, 20.0)
            if (deviceName is None) or (deviceName.strip() == ""):
                raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'deviceName'), logsi=_logsi)
            if (transferPlayback is None):
                transferPlayback = False

            # validation - Spotify Connect device name / id.
            # syncronize access via lock, as we are accessing the collection.
            with self._SpotifyConnectDevices_RLock:

                # search for device id first; if no matches, then search for name.
                scDevice:SpotifyConnectDevice = self._SpotifyConnectDevices.GetDeviceById(deviceName)
                if (scDevice is None):
                    scDevice = self._SpotifyConnectDevices.GetDeviceByName(deviceName)
                if (scDevice is None):
                    raise SpotifyApiError("Chromecast device \"%s\" could not be found in the SpotifyConnectDevices collection." % (deviceName), logsi=_logsi)

            # is this a chromecast device?
            if (not scDevice.IsChromeCast):
                raise SpotifyApiError("Device %s is not a Chromecast device; use TransferPlayback instead." % (scDevice.Title), logsi=_logsi)

            # is zeroconf discovery disabled?
            if (not self.IsZeroconDiscoveryEnabled):
                raise SpotifyApiError("Zeroconf discovery is disabled; cannot activate Chromecast devices.", logsi=_logsi)

            # has discovery browser been started yet?
            if (self._CastBrowser is None):
                raise SpotifyApiError("Chromecast discovery browser reference not set; the Browser must be started prior to calling this method.", logsi=_logsi)

            # any devices available?
            if (len(self._CastBrowser.devices) == 0):
                raise SpotifyApiError("No available Chromecast devices detected.", logsi=_logsi)

            # are we waiting on a previous request to finish?
            if (not self.WaitForActivationComplete.is_set):
                raise SpotifyApiError("Waiting for previous Chromecast device activation to complete; try again in a few seconds.", logsi=_logsi)
            if (not self.WaitForTransferComplete.is_set):
                raise SpotifyApiError("Waiting for previous Chromecast device playback transfer to complete; try again in a few seconds.", logsi=_logsi)

            # clear event notifiers.
            self.WaitForActivationComplete.clear()
            self.WaitForTransferComplete.clear()

            # if Spotify Cast App is active on a cast device then request that
            # it stop, as we will add a new one below.
            # note that this will not stop the Spotify App Task that is running
            # on the device; we don't stop the app because it would remove the
            # Spotify Connect registration.
            castAppTask:SpotifyConnectZeroconfCastAppTask = self._CastAppTasks.get(scDevice.DiscoveryResult.Key, None)
            if (castAppTask is not None):
                if (not castAppTask.is_alive()):
                    _logsi.LogVerbose("%s - Stopping Spotify Cast App task" % (self.name))
                    castAppTask.IsStopRequested = True
                    castAppTask.join()
                    _logsi.LogVerbose("%s - Spotify Cast App task was stopped successfully" % (self.name))
                self._CastAppTasks.pop(scDevice.DiscoveryResult.Key, None)

            # get CastInfo details of the specified device.
            _logsi.LogVerbose("%s - Getting Chromecast information for device: \"%s\" [%s]" % (self.name, deviceName, scDevice.DiscoveryResult.HostIpTitle))
            castInfo:CastInfo = self._CastBrowser.devices[UUID(scDevice.DiscoveryResult.Key)]
            _logsi.LogObject(SILevel.Verbose, "%s - Chromecast CastInfo details: \"%s\" (ip=%s:%s)" % (self.name, castInfo.friendly_name, castInfo.host, castInfo.port), castInfo) 

            # syncronize access via lock, as we are accessing the collection.
            with self._SpotifyConnectDevices_RLock:

                # reset device zeroconf response, as we are re-using an existing object.
                scDevice.ZeroconfResponseInfo = ZeroconfResponse()

            castDevice:Chromecast = None

            # is this a cast group?
            if (castInfo.cast_type == CAST_TYPE_GROUP):

                # for groups, the SpotifyAppTask must be activated on the group leader (e.g. coordinator).
                # the cast zeroconf info may not contain the group leader host info, as it is constantly 
                # being updated as devices are added / removed from the group.  this can lead to the 
                # SpotifyAppTask being started on a member of the group that is not the leader, which will 
                # cause other devices in the group not to play.
                # 
                # to combat this, we will call the `get_multizone_status` function that gives us the
                # current group leader host info for each group.  we will then create a cast device to
                # the group leader host address, and start the SpotifyCastApp on that specific host.

                # get current multizone status for all groups.
                castMultiZoneStatus:MultizoneStatus = get_multizone_status(castInfo.host, castInfo.services, self.ZeroconfInstance, 5)
                _logsi.LogObject(SILevel.Verbose, "%s - Chromecast group multizone status for device: %s [ip=%s:%s]" % (self.name, scDevice.Title, castInfo.host, castInfo.port), castMultiZoneStatus, colorValue=SIColors.Coral)

                # default host ip and port in case we don't find the group coordinator.
                groupHost:str = scDevice.DiscoveryResult.HostIpAddress
                groupPort:int = scDevice.DiscoveryResult.HostIpPort

                # find the group coordinator for the selected device.
                zoneInfo:MultizoneInfo = None
                for zoneInfo in castMultiZoneStatus.groups:

                    # is this our group?
                    if (str(zoneInfo.uuid) == scDevice.DiscoveryResult.Key):

                        # yes - get host info to use for the device.
                        # we will use the device discovery result HostIpAddress instead of the zoneInfo.host
                        # value here, as the zoneInfo MAY contain an IPV6 formatted address, which was causing 
                        # issues if the device was originally activated using an IPV4 address!
                        groupHost = scDevice.DiscoveryResult.HostIpAddress
                        groupPort = scDevice.DiscoveryResult.HostIpPort
                        break

                # connect to the device and build a Chromecast instance from group coordinator host info.
                castDevice = get_chromecast_from_host(
                    host=(groupHost, groupPort, castInfo.uuid, castInfo.model_name, castInfo.friendly_name),
                    tries=2,
                    retry_wait=0.5,
                    timeout=5)

                # wait for the device to become ready (15 seconds max).
                castDevice.wait(15)

            else:

                # not a group; just use the current CastInfo object.

                # connect to the device and build a Chromecast instance from a CastInfo object.
                castDevice = get_chromecast_from_cast_info(
                    cast_info=castInfo,
                    zconf=self._ZeroconfInstance,
                    tries=2,
                    retry_wait=0.5,
                    timeout=3)

                # wait for the device to become ready (10 seconds max).
                castDevice.wait(10)

            # trace.
            if (_logsi.IsOn(SILevel.Verbose)):
                _logsi.LogObject(SILevel.Verbose, "%s - Chromecast device object: \"%s\" (ip=%s:%s)" % (self.name, castInfo.friendly_name, castDevice.socket_client.host, castDevice.socket_client.port), castDevice) 
                _logsi.LogObject(SILevel.Verbose, "%s - Chromecast device status: %s [ip=%s:%s]" % (self.name, scDevice.Title, castDevice.socket_client.host, castDevice.socket_client.port), castDevice.status, colorValue=SIColors.Coral)

            # start the Spotify Cast application on the Chromecast device.
            # this will start the spotify app on the cast device.
            # it will also call the `OnCastGetInfoResponseReceived` method when the SpotifyConnectZeroconfCastAppTask
            # receives a `GetInfoResponse` block that contains Spotify Connect Zeroconf GetInformation data about the device.
            # it will also call the `OnCastZeroconfResponseReceived` method when the SpotifyConnectZeroconfCastAppTask
            # receives a `ZeroconfResponse` block that contains Spotify Connect Zeroconf Response data about the device.
            _logsi.LogVerbose("%s - Starting Spotify Cast application on Chromecast device: \"%s\" (%s) [%s]" % (self.name, castDevice.name, str(castDevice.uuid), scDevice.DiscoveryResult.HostIpTitle))
            castAppTask:SpotifyConnectZeroconfCastAppTask = SpotifyConnectZeroconfCastAppTask(
                castDevice, 
                self.SpotifyClientInstance, 
                self.OnCastGetInfoResponseReceived, 
                self.OnCastZeroconfResponseReceived, 
                transferPlayback
            )
            castAppTask.daemon = True
            castAppTask.start()

            # add cast app task to active tasks collection.
            self._CastAppTasks[str(castInfo.uuid)] = castAppTask

            # wait for the launched spotify app to activate the user (or fail).
            # this occurs when we receive any of the following zeroconf response 
            # messages: `addUserResponse`, `addUserError`, `getInfoError`, `launchError`.

            counter = 0
            while counter < (timeoutActivation + 1):
                if (self.WaitForActivationComplete.wait(1)):
                    # syncronize access via lock, as we are accessing the collection.
                    with self._SpotifyConnectDevices_RLock:
                        scDevice:SpotifyConnectDevice = self._SpotifyConnectDevices.GetDeviceByDiscoveryKey(str(castDevice.uuid))
                    if (scDevice is not None):
                        response = scDevice.ZeroconfResponseInfo
                        if (response.ResponseSource == TYPE_LAUNCH_ERROR):
                            raise SpotifyApiError("Spotify Cast Application could not be activated on Chromecast device \"%s\": %s" % (deviceName, response.StatusString), logsi=_logsi)
                        elif (response.ResponseSource == TYPE_ADD_USER_RESPONSE):
                            scDevice.WasReConnected = True
                            break
                        raise SpotifyApiError("Spotify Cast App could not be activated on Chromecast device \"%s\": %s" % (deviceName, response.ToString(False)), logsi=_logsi)
                    raise SpotifyApiError("Spotify Cast App could not activated on Chromecast device: unknown error.", logsi=_logsi)
                if (counter >= timeoutActivation):
                    # syncronize access via lock, as we are accessing the collection.
                    with self._SpotifyConnectDevices_RLock:
                        scDevice:SpotifyConnectDevice = self._SpotifyConnectDevices.GetDeviceByDiscoveryKey(str(castDevice.uuid))
                    if (scDevice is not None):
                        raise SpotifyApiError("Spotify Cast App activation timeout (%s seconds) was exceeded while trying to activate Chromecast device \"%s\"." % (timeoutActivation, deviceName), logsi=_logsi)
                counter += 1

            # at this point we have received an `adduserResponse` from the Chromecast device, indicating 
            # that it has launched the Spotify Cast App and that the user is logged in.

            # was transfer playback specified?
            if (transferPlayback == True):

                # note that we only wait if we are transferring playback.

                # wait for the launched spotify app to transfer playback (or fail).
                # this occurs when we receive any of the following zeroconf response 
                # messages: `transferSuccess`, `transferError`.

                counter = 0
                while counter < (timeoutTransfer + 1):
                    if (self.WaitForTransferComplete.wait(1)):
                        # syncronize access via lock, as we are accessing the collection.
                        with self._SpotifyConnectDevices_RLock:
                            scDevice:SpotifyConnectDevice = self._SpotifyConnectDevices.GetDeviceByDiscoveryKey(str(castDevice.uuid))
                        if (scDevice is not None):
                            response = scDevice.ZeroconfResponseInfo
                            if (response.ResponseSource == TYPE_TRANSFER_SUCCESS):
                                break
                            raise SpotifyApiError("Spotify Cast App failed to receive playback transfer on Chromecast device \"%s\": %s" % (deviceName, response.ToString(False)), logsi=_logsi)
                        raise SpotifyApiError("Spotify Cast App failed to receive playback transfer on Chromecast device: unknown error.", logsi=_logsi)
                    if (counter >= timeoutTransfer):
                        # syncronize access via lock, as we are accessing the collection.
                        with self._SpotifyConnectDevices_RLock:
                            scDevice:SpotifyConnectDevice = self._SpotifyConnectDevices.GetDeviceByDiscoveryKey(str(castDevice.uuid))
                        if (scDevice is not None):
                            raise SpotifyApiError("Spotify Cast App transfer playback timeout (%s seconds) was exceeded while waiting for transfer of playback on Chromecast device \"%s\"." % (timeoutTransfer, deviceName), logsi=_logsi)
                    counter += 1

                # at this point we have received an `transferSuccess` from the Chromecast device, indicating 
                # that transfer of playback was a success; it should now be playing a track!

        except SpotifyApiError: raise  # pass handled exceptions on thru
        except Exception as ex:

            # format unhandled exception.
            raise SpotifyApiError("Could not activate Spotify Cast application on Chromecast device \"%s\": %s" % (deviceName, str(ex)), ex, logsi=_logsi)

        finally:

            # reset activation and transfer wait events to initial state for next time;
            # just in case they were not set in the wait logic above (e.g. error condition).
            self.WaitForActivationComplete.set()
            self.WaitForTransferComplete.set()

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def AddDynamicDevice(
        self, 
        device:Device, 
        ) -> None:
        """ 
        Adds a new dynamic SpotifyConnectDevice entry to the devices collection.  
        
        Args:
            device (Device):
                Device information to add.

        Dynamic devices are Spotify Connect devices that are not found in Zeroconf discovery
        process, but still exist in the player device list.  These are usually Spotify Player
        client devices (e.g. mobile / web / desktop players) that utilize temporary device id's.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../../docs/include/samplecode/SpotifyConnectDirectoryTask/AddDynamicDevice.py
        ```
        </details>
        """
        # syncronize access via lock, as we are accessing the collection.
        with self._SpotifyConnectDevices_RLock:

            # validations.
            if (device is None) or (not isinstance(device, Device)):
                return
        
            # build zeroconf discovery result with what we can.
            discoverResult:ZeroconfDiscoveryResult = ZeroconfDiscoveryResult()
            discoverResult.DeviceName = device.Name
            discoverResult.HostIpAddresses.append('127.0.0.1')
            discoverResult.Server = '127.0.0.1'
            discoverResult.HostIpPort = 0
            discoverResult.Name = device.Name
            discoverResult.SpotifyConnectCPath = '/zc'
            discoverResult.SpotifyConnectVersion = '1.0'

            # build zeroconf getinfo result with what we can.
            info:ZeroconfGetInfo = ZeroconfGetInfo()
            info.ActiveUser = self.SpotifyClientInstance.SpotifyConnectLoginId
            info.DeviceId = device.Id
            info.DeviceType = device.Type
            info.RemoteName = device.Name
            info.SpotifyError = 0
            info.Status = 101
            info.StatusString = 'OK'
        
            # populate brand info for popular devices.
            if (device.Name == "Web Player (Chrome)"):
                info.BrandDisplayName = 'Google'
                info.ModelDisplayName = 'Chrome'
                info.ProductId = 'Web Player'
            elif (device.Name == "Web Player (Microsoft Edge)"):
                info.BrandDisplayName = 'Microsoft'
                info.ModelDisplayName = 'Edge'
                info.ProductId = 'Web Player'
            elif (device.Name == "iPhone") and (device.Type == "Smartphone"):
                info.BrandDisplayName = 'Apple'
                info.ModelDisplayName = 'iPhone'
                info.ProductId = 'Mobile Player'
            else:
                info.BrandDisplayName = 'unknown'
                info.ModelDisplayName = 'unknown'
                info.ProductId = 'unknown'
        
            # add the device.
            scDevice:SpotifyConnectDevice = SpotifyConnectDevice()
            scDevice.Id = info.DeviceId
            scDevice.Name = info.RemoteName
            scDevice.DeviceInfo = info
            scDevice.DiscoveryResult = discoverResult
            self._SpotifyConnectDevices.Items.append(scDevice)
            self._SpotifyConnectDevices.DateLastRefreshed = datetime.utcnow().timestamp()

            # sort devices collection by device name.
            if (len(self._SpotifyConnectDevices.Items) > 0):
                self._SpotifyConnectDevices.Items.sort(key=lambda x: (x.Name or "").lower(), reverse=False)

            # trace.
            _logsi.LogVerbose("Added SpotifyConnectDevices collection entry: %s - %s" % (scDevice.Title, scDevice.DiscoveryResult.Description), colorValue=SIColors.ForestGreen)

            # raise event.
            self._RaiseDeviceAdded(scDevice)


    def GetActiveDevice(
        self, 
        refresh:bool=False,
        ) -> SpotifyConnectDevice:
        """ 
        Returns the device currently marked as active if found; otherwise, null.
        
        Args:
            refresh (bool):
                True to retrieve active device from Spotify Web API player state;
                otherwise, False to retrieve active device from devices collection.

        Returns:
            The device currently marked as active if found; otherwise, null.

        The object returned is a copy of the internal master device entry; any changes made
        to the copy do not affect the internal master device entry.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../../docs/include/samplecode/SpotifyConnectDirectoryTask/GetActiveDevice.py
        ```
        </details>
        """
        # syncronize access via lock, as we are accessing the collection.
        with self._SpotifyConnectDevices_RLock:

            result:SpotifyConnectDevice = None

            # if refresh selected then retrieve the active device from playerState.
            if (refresh):
                result = self.UpdateActiveDevice(None)
                if (result is not None):
                    return result

            # find active device in the devices collection.
            for scDevice in self._SpotifyConnectDevices.Items:
                if (scDevice.DeviceInfo is not None):
                    if (scDevice.IsActiveDevice):
                        _logsi.LogVerbose("Spotify Connect active device detected: %s" % (scDevice.Title))
                        result = copy.deepcopy(scDevice)
                        break

            # returns null if no active device found.
            return result


    def GetDevice(
        self,
        value:str,
        refreshDynamicDevices:bool=True,
        raiseExceptionIfNotFound:bool=True,
        ) -> SpotifyConnectDevice:
        """
        Returns a `SpotifyConnectDevice` object for the specified device name / id if found
        in the devices collection. otherwise, returns the currently active player
        `SpotifyConnectDevice` object is returned.  otherwise, null is returned.

        Args:
            value (str | None):
                The target player device identifier.
                This could be an id, name, a default device indicator (e.g. "*"), or null
                to utilize the active player device.  
                Examples are `0d1841b0976bae2a3a310dd74c0f3df354899bc8`, `Office`, `*`, None.  
            refreshDynamicDevices (bool):
                True to refresh the list of dynamically added devices and the active player
                state from real-time Spotify Web API data; otherwise, false to use the
                current cached state and device list.
                Default is True.
            raiseExceptionIfNotFound (bool):
                True to raise an exception if a device could not be resolved;
                otherwise, False to just return a null value.  
                Default is True.

        Returns:
            A `SpotifyConnectDevice` object for the specified device name / id if found;
            otherwise, null.

        Raises:
            SpotifyConnectDeviceNotFound:
                If the `raiseExceptionIfNotFound` argument value is True, and the specified 
                device value was not found or there was no default device found.
            SpotifyApiError: 
                If an error occured while obtaining current Spotify Web API Player device data.

        If a SpotifyConnectDevice object is returned, it will be a copy of the internal master 
        device entry; any changes made to the copy do not affect the internal master device entry.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../../docs/include/samplecode/SpotifyConnectDirectoryTask/GetDevice.py
        ```
        </details>
        """
        # syncronize access via lock, as we are accessing the collection.
        with self._SpotifyConnectDevices_RLock:

            apiMethodName:str = "GetDevice"
            apiMethodParms:SIMethodParmListContext = None
            scDevice:SpotifyConnectDevice = None
            scActiveDevice:SpotifyConnectDevice = None

            try:

                # trace.
                apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
                apiMethodParms.AppendKeyValue("value", value)
                apiMethodParms.AppendKeyValue("refreshDynamicDevices", refreshDynamicDevices)
                apiMethodParms.AppendKeyValue("SpotifyClient.DefaultDeviceId", self.SpotifyClientInstance.DefaultDeviceId)
                _logsi.LogMethodParmList(SILevel.Verbose, "Getting Spotify Connect device instance for value \"%s\"" % (value), apiMethodParms)

                # validations.
                if (value is not None) and (not isinstance(value, str)):
                    value = None
                if (not isinstance(refreshDynamicDevices, bool)):
                    refreshDynamicDevices = True
                if (not isinstance(raiseExceptionIfNotFound, bool)):
                    raiseExceptionIfNotFound = True
                valueOriginal:str = value

                # get currently active player device.
                if (refreshDynamicDevices):
                    scActiveDevice = self.RefreshDynamicDevices()
                else:
                    scActiveDevice = self.UpdateActiveDevice()

                # was the active spotify player device value specified (e.g. null / empty string)?
                if (value is None) or (value.strip() == ""):

                    # is there an active player device?
                    if (scActiveDevice is not None):
                        _logsi.LogObject(SILevel.Verbose, "Spotify Player device \"%s\" (%s) was found in the Spotify Connect Devices collection (by Active PlayerState)" % (scActiveDevice.Name, scActiveDevice.Id), scActiveDevice, excludeNonPublic=True)
                        return scActiveDevice

                    # if no active player device, then let's use the default device value.
                    _logsi.LogVerbose("Spotify Player has no active device; defaulting device selection to use DefaultDeviceId: \"%s\"" % (self.SpotifyClientInstance.DefaultDeviceId))
                    value = self.SpotifyClientInstance.DefaultDeviceId

                # was a default device value specified?
                # if so, then use the `defaultDeviceId` value; if the `defaultDeviceId` value is not in the device list, 
                # then we will catch it with the `GetDeviceById` / `GetDeviceByName` logic.
                # if `defaultDeviceId` was not configured, then use active player device (via playerstate).
                # if `defaultDeviceId` value is not in the device list, then use active player device (via playerstate).
                # if no active player device, then it's an exception!
                if (value == "*"):

                    # get default device id value from the client.
                    defaultDeviceId:str = self.SpotifyClientInstance.DefaultDeviceId

                    # was a default device specified? 
                    if (defaultDeviceId is None) or (defaultDeviceId.strip() == ""):
                        # is there an active player device?
                        if (scActiveDevice is not None):
                            _logsi.LogObject(SILevel.Verbose, "Spotify Player default device (*) was not configured; using active player device: %s" % (scActiveDevice.Title), scActiveDevice, excludeNonPublic=True)
                            return scActiveDevice
                        # if no default device and no active player, then it's an error!
                        #raise SpotifyApiError("Spotify Player default device (*) was not configured, and there is no active Spotify Player device", logsi=_logsi)
                    
                    # assign default device value.
                    _logsi.LogVerbose("Spotify Player device default \"%s\" will be used for selecting a device (by default *)" % (defaultDeviceId))
                    value = defaultDeviceId

                # check for the device id in the devices collection.
                scDevice = self._SpotifyConnectDevices.GetDeviceById(value)
                if (scDevice is not None):
                    _logsi.LogObject(SILevel.Verbose, "Spotify Player device %s was found in the Spotify Connect Devices collection (by Id)" % (scDevice.Title), scDevice, excludeNonPublic=True)
                    return copy.deepcopy(scDevice)
                
                # check for the device name in the devices collection.
                scDevice = self._SpotifyConnectDevices.GetDeviceByName(value)
                if (scDevice is not None):

                    # we have a device match by name!
                    # is there an active player device? 
                    if (scActiveDevice is not None):

                        # does the active device have the same name, but a different device id?
                        if (scActiveDevice.Name == scDevice.Name) and (scActiveDevice.Id != scDevice.Id):
                            # this denotes that we have 2 devices in the device list with the same name
                            # but different id's.  in this case we will use the active device, since it
                            # is already active.
                            _logsi.LogObject(SILevel.Verbose, "Spotify Player device %s was found in the Spotify Connect Devices collection (by Duplicate Name), which denotes that we have 2 devices in the device list with the same name but different id's; in this case we will use the active device (id=%s), since it is already active" % (scDevice.Title, scActiveDevice.Id), scDevice, excludeNonPublic=True)
                            scDevice = scActiveDevice

                    _logsi.LogObject(SILevel.Verbose, "Spotify Player device %s was found in the Spotify Connect Devices collection (by Name)" % (scDevice.Title), scDevice, excludeNonPublic=True)
                    return copy.deepcopy(scDevice)

                # is there an active player device?
                if (scActiveDevice is not None):

                    # check if the active device is restricted; if it is, then it may not show up in the
                    # available device list of devices (common issue with Sonos devices).  in this case,
                    # it WILL show up in the player state device property as the active device.
                    # note that the PlayerPlayState device is a name and not a device id.
                    if (scActiveDevice.IsRestricted):
                        value = ("" + value).lower()
                        if (scActiveDevice.Id.lower() == value) or (scActiveDevice.Name.lower() == value):
                            _logsi.LogObject(SILevel.Verbose, "Spotify Player device %s was found to be a restricted device (by Active PlayerState)" % (scDevice.Title), scDevice, excludeNonPublic=True)
                            return scActiveDevice
                
                    # if `defaultDeviceId` value is not in the device list, then use active player device.
                    if (valueOriginal == "*"):
                        _logsi.LogObject(SILevel.Verbose, "Spotify Player default device \"%s\" was not found in the Spotify Connect Devices collection; using active player device: %s" % (value, scActiveDevice.Title), scActiveDevice, excludeNonPublic=True)
                        return scActiveDevice

                # at this point we could not resolve the device name / id, and there is no active player
                # available; raise exception / return null as requested by the caller.
                if (raiseExceptionIfNotFound):
                    raise SpotifyConnectDeviceNotFound("Spotify Player device \"%s\" was not found, and there is no active Spotify player" % (value), logsi=_logsi)
                else:
                    _logsi.LogVerbose("Spotify Player device \"%s\" was not found, and there is no active Spotify player" % (value))
                    return None

            except SpotifyApiError: raise  # pass handled exceptions on thru
            except Exception as ex:

                # format unhandled exception.
                raise SpotifyApiError("%s - Could not retrieve dynamic device list: %s" % (self.name, str(ex)), ex, logsi=_logsi)

            finally:

                # trace.
                _logsi.LeaveMethod(SILevel.Debug)


    def GetDevices(self,
        ) -> SpotifyConnectDevices:
        """
        Returns a collection of available Spotify Connect devices.

        The object returned is a copy of the internal master device list; any changes made
        to the copy do not affect the internal master device list.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../../docs/include/samplecode/SpotifyConnectDirectoryTask/GetDevices.py
        ```
        </details>
        """
        result:SpotifyConnectDevices

        # DO NOT syncronize access via lock here!
        # doing so can cause thread deadlocks in Home Assistant state machine.
        # with self._SpotifyConnectDevices_RLock:

        # creates a completely independent copy of the devices collection (no references),
        # and return it to the caller.
        result = copy.deepcopy(self._SpotifyConnectDevices)
        return result


    def GetPlayerDevice(
        self, 
        value:str,
        refresh:bool=False,
        ) -> SpotifyConnectDevice:
        """ 
        Returns the device instance if it is currently in the Spotify Web API player device list; 
        otherwise, null.
        
        Args:
            value (str):
                Spotify Connect device name or id value used to identify the device.
            refresh (bool):
                True to refresh player devices from Spotify Web API devices;
                otherwise, False to retrieve player device from devices collection.

        Returns:
            The device instance if it is currently in the Spotify Web API player device list; 
            otherwise, null.

        The object returned is a copy of the internal master device entry; any changes made
        to the copy do not affect the internal master device entry.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../../docs/include/samplecode/SpotifyConnectDirectoryTask/GetPlayerDevice.py
        ```
        </details>
        """
        # syncronize access via lock, as we are accessing the collection.
        with self._SpotifyConnectDevices_RLock:

            result:SpotifyConnectDevice = None

            # validations.
            if (value is None):
                return result

            # if refresh selected then update player devices from Spotify Web API.
            if (refresh):
                self.UpdatePlayerDevices()

            # prepare for compare.
            value = "" + value.strip().lower()

            # find specified player device in the devices collection.
            for scDevice in self._SpotifyConnectDevices._Items:
                if (scDevice.IsInDeviceList):
                    if (scDevice.Id.lower() == value) or (scDevice.Name.lower() == value)  or (scDevice.DiscoveryResult.DeviceName.lower() == value):
                        _logsi.LogVerbose("Spotify Connect player device detected: %s" % (scDevice.Title))
                        result = copy.deepcopy(scDevice)
                        break

            # returns null if no active device found.
            return result


    def GetSonosPlayer(
        self, 
        device:SpotifyConnectDevice,
        returnCoordinator:bool=True,
        ) -> SoCo:
        """ 
        Returns the Sonos Controller instance for the specified Spotify Connect device.
        Returns the Sonos player instance for the specified Spotify Connect Sonos device.
        
        Args:
            device (SpotifyConnectDevice):
                Spotify Connect device instance used to identify the Sonos player.
            returnCoordinator (bool):
                True to return the group coordinator instance if the device is part of a Sonos group;
                otherwise, False to return the found instance;  
                Default is True.

        Returns:
            The Sonos Controller instance for the specified Spotify Connect device.

        Raises:
            SpotifyApiError:
                If a Sonos Controller instance could not be found for the device id.

        You should invoke "if (scDevice.IsSonos):" logic prior to calling this method, as
        a Sonos Controller instance will not be created for non-Sonos devices and an exception
        will be raised!
        """
        apiMethodName:str = "GetSonosPlayer"

        # syncronize access via lock, as we are accessing the collection.
        with self._SpotifyConnectDevices_RLock:

            result:SpotifyConnectDevice = None

            # validations.
            if (device is None):
                raise SpotifyApiError(SAAppMessages.ARGUMENT_REQUIRED_ERROR % (apiMethodName, 'device'), logsi=_logsi)
            if (not isinstance(returnCoordinator, bool)):
                returnCoordinator = True

            # get Sonos Controller instance for device name.
            sonosPlayer:SoCo = self._SonosPlayers.get(device.DiscoveryResult.HostIpAddress, None)

            # if not found then it's an error.
            if (sonosPlayer is None):
                raise SpotifyApiError("Could not find Sonos Controller instance for device: %s" % (device.Title), None, logsi=_logsi)

            # trace.
            _logsi.LogDictionary(SILevel.Verbose, "Sonos Controller instance for device: %s (speaker_info)" % (device.Title), sonosPlayer.speaker_info)

            # does caller want the group coordinator?
            if (returnCoordinator):

                # TEST TODO - use to test Sonos coordinator functionality.
                # _logsi.LogObject(SILevel.Verbose, "Sonos Controller instance for device: %s" % (device.Title), sonosPlayer, colorValue=SIColors.Red)
                #sonosPlayer._is_coordinator = False 

                # is Sonos Controller instance the group coordinator?
                if (sonosPlayer.is_coordinator):

                    # yes - nothing else to do since it's already a group coordinator.
                    _logsi.LogVerbose("Sonos Controller instance is a group coordinator")

                else:

                    # no - try to determine the group coordinator.
                    _logsi.LogVerbose("Sonos Controller instance is NOT a group coordinator for device: %s" % (device.Title))

                    # is the device part of a group? if so, then use the `group.coordinator` value (if present).
                    sonosPlayerCoordinator:SoCo = None
                    if (sonosPlayer.group is not None):
                        if (sonosPlayer.group.coordinator is not None):
                            sonosPlayerCoordinator = sonosPlayer.group.coordinator
                            sonosPlayer = sonosPlayerCoordinator
                            _logsi.LogVerbose("Sonos Controller group coordinator \"%s\" (%s) will be used for device: %s" % (sonosPlayerCoordinator.player_name, sonosPlayerCoordinator.ip_address, device.Title))
                            _logsi.LogDictionary(SILevel.Verbose, "Sonos Controller instance for device: %s (speaker_info)" % (device.Title), sonosPlayerCoordinator.speaker_info)

                    # if group coordinator could not be found, then log a trace message indicating
                    # this and that subsequent Sonos Controller operations will probably fail.
                    # this only seems to happen for "orphaned" Sonos devices (e.g. uid="")
                    # zone_group_state.groups = [ZoneGroup(uid='RINCON_5CAAFDF4E8DE01400:orphan', coordinator=None, members={SoCo("192.168.50.79")}), etc
                    if (sonosPlayerCoordinator is None):
                        _logsi.LogVerbose("Sonos Controller group coordinator could not be determined for device: %s; subsequent Sonos Controller API functions will probably fail!" % (device.Title), colorValue=SIColors.Red)
                        _logsi.LogObject(SILevel.Verbose, "Sonos Controller instance for device: %s (group)" % (device.Title), sonosPlayer.group)

            # return Sonos Controller instance to caller.
            return sonosPlayer


    def GetSpotifyDeviceIDFromName(
        self, 
        name:str
        ) -> str:
        """
        Retrieve the Spotify deviceID from provided user-friendly name.

        DeviceId is just the md5 hash representation of the user-friendly-name.
        """
        if (name is None):
            name = ""

        deviceId:str = hashlib.md5(name.encode()).hexdigest()
        return deviceId
    

    def RefreshDynamicDevices(
        self,
        ) -> SpotifyConnectDevice:
        """
        Refreshes dynamic Spotify Connect devices, and also determines the currently
        active device (if any).

        Returns:
            A SpotifyConnectDevice object that contains the active device if one was found;
            otherwise, null to indicate no active device.

        Dynamic devices are Spotify Connect devices that are not found in Zeroconf discovery
        process, but exist in the player device list.  These are usually Spotify Connect
        web or mobile players with temporary device id's.

        The object returned is a copy of the internal master device entry; any changes made
        to the copy do not affect the internal master device entry.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../../docs/include/samplecode/SpotifyConnectDirectoryTask/RefreshDynamicDevices.py
        ```
        </details>
        """
        # syncronize access via lock, as we are accessing the collection.
        with self._SpotifyConnectDevices_RLock:

            try:

                # trace.
                apiMethodParms:SIMethodParmListContext = _logsi.EnterMethodParmList(SILevel.Debug)
                _logsi.LogMethodParmList(SILevel.Verbose, "Refreshing Spotify Connect dynamic device list", apiMethodParms)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, "Current Spotify Connect device list (before refresh)", self.GetDevices().ToDictionary(), prettyPrint=True)

                # update player devices known to the Spotify Web API (e.g. dynamic devices).
                self.UpdatePlayerDevices()

                # update the currently active device (if any).  
                scDevice:SpotifyConnectDevice = self.UpdateActiveDevice()

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, "Current Spotify Connect device list (after refresh)", self.GetDevices().ToDictionary(), prettyPrint=True)
                    if (scDevice is None):
                        _logsi.LogVerbose("Spotify Player playstate device is not present; no active device")
                    else:
                        _logsi.LogObject(SILevel.Verbose, "Spotify Player playstate active device instance: %s" % (scDevice.Title), scDevice, excludeNonPublic=True)

                # return real-time active Spotify Player device.
                return scDevice

            except SpotifyApiError: raise  # pass handled exceptions on thru
            except Exception as ex:

                # format unhandled exception.
                raise SpotifyApiError("%s - Could not retrieve dynamic device list: %s" % (self.name, str(ex)), ex, logsi=_logsi)

            finally:

                # trace.
                _logsi.LeaveMethod(SILevel.Debug)


    def RemoveDevice(
        self,
        deviceId:str,
        dynamicDeviceOnly:bool=False
        ) -> SpotifyConnectDevice:
        """
        Removes existing device entry(s) from the devices collection by device id value.
        
        Args:
            deviceId (str):
                Device id to remove.
            dynamicDeviceOnly (str):
                True to only remove the device if it's a dynamic device entry;
                otherwise, False to remove the device id regardless.  
                Default is False.

        Returns:
            A SpotifyConnectDevice object that contains the removed device if one was found;
            otherwise, null to indicate no device was removed.

        It's possible to have multiple devices with the same id (e.g. both a dynamic and a
        zeroconf registered device).

        Dynamic devices are Spotify Connect devices that are not found in Zeroconf discovery
        process, but still exist in the player device list.  These are usually Spotify Player
        client devices (e.g. mobile / web / desktop players) that utilize temporary device id's.

        The object returned is a copy of the internal master device entry; any changes made
        to the copy do not affect the internal master device entry.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../../docs/include/samplecode/SpotifyConnectDirectoryTask/AddDynamicDevice.py
        ```
        </details>
        """
        # syncronize access via lock, as we are accessing the collection.
        with self._SpotifyConnectDevices_RLock:

            try:

                # validations.
                if (not isinstance(dynamicDeviceOnly,bool)):
                    dynamicDeviceOnly = False

                # remove device from devices collection;
                # the reversed() function creates an iterator that traverses the list in reverse order. 
                # this ensures that removing an element doesn't affect the indices of the subsequent 
                # elements we're going to iterate over.
                deviceIdCompare:str = (deviceId or "").lower()
                scDevice:SpotifyConnectDevice
                for idx in reversed(range(len(self._SpotifyConnectDevices.Items))):

                    scDevice = self._SpotifyConnectDevices.Items[idx]

                    # did we find a match by device id?
                    if (deviceIdCompare == (scDevice.Id or "").lower()):

                        isFound:bool = True

                        # get dynamic device status.
                        isDynamic:bool = False
                        if (scDevice.DiscoveryResult is not None):
                           isDynamic = scDevice.DiscoveryResult.IsDynamicDevice

                        # are we checking for dynamic device? if so, and it's NOT dynamic, 
                        # then don't delete it!
                        if (dynamicDeviceOnly) and (not isDynamic):
                            isFound = False

                        # are we deleting this device?
                        if (isFound):

                            # remove the device.
                            scDevice:SpotifyConnectDevice = copy.deepcopy(self._SpotifyConnectDevices.Items.pop(idx))
                            _logsi.LogVerbose("Removed SpotifyConnectDevices collection entry: %s - %s" % (scDevice.Title, scDevice.DiscoveryResult.Description), colorValue=SIColors.Orange)

                            # raise event.
                            self._RaiseDeviceRemoved(scDevice)

            except SpotifyApiError: raise  # pass handled exceptions on thru
            except Exception as ex:

                # format unhandled exception.
                raise SpotifyApiError(SAAppMessages.UNHANDLED_EXCEPTION.format("RemoveDevice", str(ex)), ex, logsi=_logsi)


    def UpdatePlayerDevices(
        self, 
        playerDevices:list[Device]=None,
        ) -> None:
        """ 
        Adds a list of dynamic player device entries to the devices collection, and removes any
        existing dynamic devices from the collection that are not in the `playerDevices` list.
        
        Args:
            playerDevices (list[Device]):
                If specified, the list of current player devices obtained via a previous call to
                the Spotify Web API; otherwise, null to call the Spotify Web API to retrieve the list.

        Dynamic devices are Spotify Connect devices that are not found in Zeroconf discovery
        process, but still exist in the player device list.  These are usually Spotify Player
        client devices (e.g. mobile / web / desktop players) that utilize temporary device id's.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../../docs/include/samplecode/SpotifyConnectDirectoryTask/UpdatePlayerDevices.py
        ```
        </details>
        """
        # syncronize access via lock, as we are accessing the collection.
        with self._SpotifyConnectDevices_RLock:

            # validations.
            if (playerDevices is not None) and (not isinstance(playerDevices, list)):
                return

            # if playerDevices object not supplied, then go get them.
            if (playerDevices is None):
                playerDevices:list[Device] = self._SpotifyClientInstance.GetPlayerDevices(refresh=True)

            # reset device list indicators, just in case any were disconnected and are not in the
            # current player device list.
            for scDevice in self._SpotifyConnectDevices.Items:
                scDevice.IsInDeviceList = False

            # add dynamic devices.
            scDevice:SpotifyConnectDevice
            device:Device
            for device in playerDevices:

                # is the player device present in the collection? if not, then add it.
                if (not self._SpotifyConnectDevices.ContainsDeviceId(device.Id)):
                    self.AddDynamicDevice(device)
                        
                # check all registered Spotify Connect device entries.
                for scDevice in self._SpotifyConnectDevices.Items:
        
                    # do we have a match on the device id?
                    if (scDevice.DeviceInfo.DeviceId == device.Id) and ((device.Id or "") != ""):

                        # indicate the device is in the available device list.
                        scDevice.IsInDeviceList = True

                        # is the device an alias entry?
                        # if Spotify Web API device entry is an alias, then the device id and device name
                        # values will USUALLY be the same (e.g. a device id value) and the SpotifyConnectDevices
                        # collection entry's DeviceInfo.RemoteName value will be an empty string (e.g. "").
                        if (scDevice.DeviceInfo.HasAliases) and (device.Id == device.Name):

                            # yes - DO NOT change the RemoteName value, as an alias is in use.
                            _logsi.LogVerbose("Detected Spotify Connect Alias in use for SpotifyConnectDevices collection entry %s [%s]; first Alias name is \"%s\"; RemoteName is \"%s\"" % (scDevice.Title, scDevice.DiscoveryResult.Description, scDevice.DeviceInfo.Aliases[0].Name, scDevice.DeviceInfo.RemoteName), colorValue=SIColors.Coral)

                        else:

                            # did the player device remote name change?
                            # if so, then update the collection RemoteName as well as the Name.
                            # this can happen for devices that are added to / removed from groups
                            # and do not correctly inform interested parties via a zeroconf 
                            # OnServiceStateChange event that the name has changed (e.g. Denon HEOS devices, etc).
                            if (scDevice.DeviceInfo.RemoteName != device.Name) and ((device.Name or "") != ""):
                                _logsi.LogVerbose("Detected Spotify Connect RemoteName change for SpotifyConnectDevices collection entry %s [%s]; updated Spotify Web API PlayerDevice Name is \"%s\" - this is usually caused by a Speaker Group membership change" % (scDevice.Title, scDevice.DiscoveryResult.Description, device.Name), colorValue=SIColors.Coral)
                                scDevice.DeviceInfo.RemoteName = device.Name
                                scDevice.Name = device.Name
                                self._SpotifyConnectDevices.DateLastRefreshed = datetime.utcnow().timestamp()
                                # ???? - we should probably call getInfo again to update DeviceInfo since GroupStatus has 
                                # probably changed from "NONE" to "GROUP" or vice versa!
                                # we will start with this to see how it goes.
                                self._RaiseDeviceUpdated(scDevice)

                        # don't need to search any more devices since we found the device id.
                        break

            # remove stale dynamic devices from results collection;
            # the reversed() function creates an iterator that traverses the list in reverse order. 
            # this ensures that removing an element doesn't affect the indices of the subsequent 
            # elements we're going to iterate over.
            for idx in reversed(range(len(self._SpotifyConnectDevices.Items))):

                # only process dynamic devices.
                scDevice = self._SpotifyConnectDevices.Items[idx]
                if (scDevice.DiscoveryResult.IsDynamicDevice):

                    # process all player devices.
                    wasFound:bool = False
                    playerDevice:Device
                    for playerDevice in playerDevices:
                        if (scDevice.Id == playerDevice.Id):
                            wasFound = True
                            break

                    # if collection entry was not found in the player device list then remove it.
                    if (not wasFound):

                        # remove the device.
                        scDevice:SpotifyConnectDevice = copy.deepcopy(self._SpotifyConnectDevices.Items.pop(idx))
                        _logsi.LogVerbose("Removed SpotifyConnectDevices collection entry: %s - %s" % (scDevice.Title, scDevice.DiscoveryResult.Description), colorValue=SIColors.Orange)

                        # raise event.
                        self._RaiseDeviceRemoved(scDevice)


    def UpdateActiveDevice(
        self, 
        playerState:PlayerPlayState=None
        ) -> SpotifyConnectDevice:
        """ 
        Updates the currently active device based on playerState.
        
        Args:
            playerState (PlayerPlayState):
                Current player state obtained via a call to `GetPlayerPlaybackState` method
                which will be used to set the active device in the `Items` collection;
                otherwise, null to bypass active device set.

        Returns:
            The currently active Spotify Player device instance if one was found; otherwise, null.
            
        The Spotify Web API GetPlayerPlaybackState method is called to retrieve the active device
        information.

        The object returned is a copy of the internal master device entry; any changes made
        to the copy do not affect the internal master device entry.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../../docs/include/samplecode/SpotifyConnectDirectoryTask/UpdateActiveDevice.py
        ```
        </details>
        """
        # syncronize access via lock, as we are accessing the collection.
        with self._SpotifyConnectDevices_RLock:

            result:SpotifyConnectDevice = None

            # if playerState object not supplied, then go get it.
            if (playerState is None):
                playerState:PlayerPlayState = self._SpotifyClientInstance.GetPlayerPlaybackState(additionalTypes='episode')

            # if valid object then process it.
            if (isinstance(playerState, PlayerPlayState)):

                # we do this in case the active device is a "restricted" device; if it is, then it may 
                # not show up as the active device (common issue with Sonos devices).  
                # in this case, it WILL show up in the player state device property as the active device.
                # if it IS active, then we will set the active flag.        
                # note that the PlayerPlayState device is a name and not a device id; it's device id 
                # could also be set to null if it's a restricted device (e.g. Sonos).
                if playerState.Device is not None:

                    # reset active device status for all devices; set active device status if found.
                    device = playerState.Device
                    for scDevice in self._SpotifyConnectDevices.Items:
                        scDevice.IsActiveDevice = False

                        # is a device id present?
                        if ((device.Id or "") != ""):

                            # yes - compare on the device id.
                            if (device.Id == scDevice.Id):
                                _logsi.LogVerbose("Spotify Connect active device detected (By Id): %s" % (scDevice.Title))
                                scDevice.IsActiveDevice = True
                                scDevice.IsRestricted = playerState.Device.IsRestricted
                                result = copy.deepcopy(scDevice)

                        # no - compare on the device name.
                        elif (device.Name == scDevice.Name):
                            _logsi.LogVerbose("Spotify Connect active device detected (By Name): %s" % (scDevice.Title))
                            scDevice.IsActiveDevice = True
                            scDevice.IsRestricted = playerState.Device.IsRestricted
                            result = copy.deepcopy(scDevice)

            # returns null if the `playerState` argument was not specified; 
            # otherwise, the currently active Spotify Player device instance as determined by
            # the Spotify Player PlayState (could be null if no active device).
            return result


    def OnServiceInfoAddedUpdatedChromecast(
        self, 
        zeroconfDiscoveryResult:ZeroconfDiscoveryResult,
        uuid:UUID, 
        serviceName:str,
        serviceType:str,
        ) -> None:
        """
        Called when a Chromecast MDNS service record has been discovered
        or updated for a Chromecast device.

        Args:
            zeroconfDiscoveryResult (ZeroconfDiscoveryResult):
                A `ZeroconfDiscoveryResult` object that contains discovery details.
            uuid (UUID):
                The cast's uuid, which is the dictionary key to find the chromecast 
                metadata in CastBrowser.devices and CastBrowser.services collection.
            serviceName (str):
                First known MDNS service name or host:port.
            serviceType (str):
                Service call type (e.g. "add_cast", "update_cast").

        This method will be called in a thread-safe manner, as the caller is using
        the `_Zeroconf_RLock` object to control access.
        """
        # syncronize access via lock, as we are accessing the collection.
        with self._SpotifyConnectDevices_RLock:

            try:

                # trace.
                _logsi.EnterMethod(SILevel.Debug)

                # add / update discovered results by serviceinfo key value.
                # examples: 
                # - Name="SHIELD-Android-TV-72735c92dead1a2d62df0229b1590a65._googlecast._tcp.local.",   Key="72735c92-dead-1a2d-62df-0229b1590a65"
                # - Name="LS50-Wireless-II-5b1bb9c433d5bc1f7c8bf208c0cdda3f._googlecast._tcp.local.",    Key="5b1bb9c4-33d5-bc1f-7c8b-f208c0cdda3f"

                # note that for "Google-Cast-Group-x" entries, the name will vary slightly with each member of
                # the group, but the key value will be the same.  this is important because for groups you want
                # to update the same group KEY as group updates are made (e.g. group / ungroup devices).
                # examples: 
                # - Name="Google-Cast-Group-631B535F21D3408A8EE2C52BEBDB99E7._googlecast._tcp.local.",   Key="631b535f-21d3-408a-8ee2-c52bebdb99e7"
                # - Name="Google-Cast-Group-631B535F21D3408A8EE2C52BEBDB99E7-1._googlecast._tcp.local.", Key="631b535f-21d3-408a-8ee2-c52bebdb99e7"
                # - Name="Google-Cast-Group-631B535F21D3408A8EE2C52BEBDB99E7-2._googlecast._tcp.local.", Key="631b535f-21d3-408a-8ee2-c52bebdb99e7"

                # get cast device instance by discovery key.
                # note that we cannot use discovery name here, as Google Groups use different
                # names that refer to the same key value!
                scDevice:SpotifyConnectDevice = None
                idx:int = self._SpotifyConnectDevices.GetDeviceIndexByDiscoveryKey(zeroconfDiscoveryResult.Key)
                if (idx == -1):

                    # trace.
                    _logsi.LogVerbose("Creating new SpotifyConnectDevice instance from CastInfo data: \"%s\" (%s) [key=%s]" % (zeroconfDiscoveryResult.DeviceName, zeroconfDiscoveryResult.Name, zeroconfDiscoveryResult.Key))

                    # connect to the device using CastInfo to get more details.
                    castInfo:CastInfo = self._CastBrowser.services[uuid]
                    _logsi.LogVerbose("Retrieving Chromecast device instance from CastInfo object \"%s\" (%s)" % (zeroconfDiscoveryResult.DeviceName, zeroconfDiscoveryResult.Name))
                    castDevice:Chromecast = get_chromecast_from_cast_info(
                        cast_info=castInfo,
                        zconf=self._ZeroconfInstance,
                        tries=2,
                        retry_wait=0.5,
                        timeout=5)

                    # wait for the device to become ready (10 seconds max).
                    castDevice.wait(10)
                    _logsi.LogObject(SILevel.Verbose, "Chromecast device instance \"%s\" (%s)" % (castInfo.friendly_name, zeroconfDiscoveryResult.Name), castDevice)

                    # create a new Spotify Connect Device instance.
                    scDevice = SpotifyConnectDevice()
                    scDevice.Name = zeroconfDiscoveryResult.DeviceName
                    scDevice.Id = self.GetSpotifyDeviceIDFromName(castInfo.friendly_name)

                    # set zeroconf discovery result properties.
                    scDevice.DiscoveryResult = zeroconfDiscoveryResult

                    # Spotify Connect GetInformation is called as part of the cast app launch process,
                    # and cannot be performed yet.

                    # set device info properties that we know about; the rest will be filled in
                    # when we connect to the device and the cast `getInfoResponse` is returned.
                    scDevice.DeviceInfo = ZeroconfGetInfo()
                    scDevice.DeviceInfo.DeviceId = scDevice.Id
                    scDevice.DeviceInfo.DeviceType = "CastAudio"
                    scDevice.DeviceInfo.BrandDisplayName = castInfo.manufacturer or "ChromeCast"
                    scDevice.DeviceInfo.ModelDisplayName = castInfo.model_name
                    scDevice.DeviceInfo.RemoteName = castInfo.friendly_name

                    # did this device change from a dynamic device (e.g. non-zeroconf) to a zeroconf device?
                    # this can happen if the device is initially added as a dynamic device, then the zeroconf
                    # device is discovered.  if so, we will remove the dynamic device entry.
                    spDynamicDevice:SpotifyConnectDevice = self._SpotifyConnectDevices.GetDeviceById(scDevice.DeviceInfo.DeviceId)
                    if (spDynamicDevice is not None):

                        # trace.
                        _logsi.LogVerbose("Chromecast Zeroconf is converting SpotifyConnectDevice entry %s from dynamic to zeroconf" % (spDynamicDevice.Title))

                        # copy real-time status dynamic properties to zerconf object.
                        scDevice.IsActiveDevice = spDynamicDevice.IsActiveDevice
                        scDevice.IsInDeviceList = spDynamicDevice.IsInDeviceList

                        # remove the dynamic device from the collection.
                        self.RemoveDevice(spDynamicDevice.Id, dynamicDeviceOnly=True)

                    # # is this an add_cast event?
                    # if (serviceType == "add_cast"):

                    #     # add cast device to multizone manager instance.  this will add a listener
                    #     # for multizone status events to be processed, which allows us to keep track
                    #     # of which device is a group leader.
                    #     self._CastMultiZoneManager.add_multizone(castDevice)
                    #     self._CastMultiZoneManager.register_listener(castDevice.uuid, SpotifyConnectZeroconfCastMultiZoneListener(self, self.ZeroconfInstance))


                    # is this a Google Cast Group?
                    if (castInfo.cast_type == CAST_TYPE_GROUP):

                        # if so, then "add_cast" entries will occur for every member of the group.
                        # we only want to keep the LAST group entry zeroconfDiscoveryResult on file,
                        # and ignore all of the others; otherwise, it creates duplicate entries in the 
                        # devices collection for each member device of the group!

                        # note that we will query the current multi-zone status if it's a group entry, as
                        # we have to start the SpotifyAppTask on the group leader / coordinator device.

                        # example: RemoteName = "Kitchen Parlor", DeviceID = 3fb9b12379e4fa1957d065b4c4568939
                        # - (add_cast) "Google-Cast-Group-B85B00FE5F514A40BF6AFBBCCEB7C8DF-1._googlecast._tcp.local."
                        #   HostIPAddr = 192.168.1.14:32139
                        #   GroupMembr = "Kitchen Speakers", 192.168.1.14:8009
                        #   RemoteName = "Kitchen Parlor"
                        #   DeviceID   = 3fb9b12379e4fa1957d065b4c4568939
                        # - (add_cast) "Google-Cast-Group-B85B00FE5F514A40BF6AFBBCCEB7C8DF._googlecast._tcp.local."
                        #   HostIPAddr = 192.168.1.186:32139
                        #   GroupMembr = "Parlor Speakers", 192.168.1.186:8009
                        #   RemoteName = "Kitchen Parlor"
                        #   DeviceID   = 3fb9b12379e4fa1957d065b4c4568939

                        # ignore "update_cast" entries, as we don't want to create duplicates.
                        if (serviceType == "update_cast"):
                            _logsi.LogVerbose("SpotifyConnectDevice instance will be ignored for Google Cast Group data: \"%s\" (%s)" % (zeroconfDiscoveryResult.DeviceName, zeroconfDiscoveryResult.Name))
                            return

                        # does the device name and id already exist?
                        groupDevice:SpotifyConnectDevice = self._SpotifyConnectDevices.GetDeviceByNameAndId(scDevice.Name, scDevice.Id)
                        if (groupDevice is not None):
                            _logsi.LogVerbose("SpotifyConnectDevice instance already exists for Google Cast Group data: \"%s\" (%s), Group RemoteName=%s, Host IP=%s" % (zeroconfDiscoveryResult.DeviceName, zeroconfDiscoveryResult.Name, groupDevice.Title, groupDevice.DiscoveryResult.HostIpTitle))

                            # set zeroconf discovery result properties.
                            scDevice.DiscoveryResult = zeroconfDiscoveryResult

                            # update existing Spotify Connect Device in devices collection.
                            self._SpotifyConnectDevices.Items[idx] = scDevice
                            self._SpotifyConnectDevices.DateLastRefreshed = datetime.utcnow().timestamp()
                            return



                    # TEST TODO REMOVEME
                    # # register a multizone listener to listen for group change events; these
                    # # events will tell us what cast device is currently the leader of a group.

                    # try:

                    #     # is this an add_cast event?
                    #     if (serviceType == "add_cast"):

                    #         # do we have a multizone controller registered for this device yet?
                    #         castMultizoneController:MultizoneController = self._CastMultiZoneControllers.get(scDevice.DiscoveryResult.Key, None)
                    #         if (castMultizoneController is None):

                    #             # trace.
                    #             _logsi.LogVerbose("Chromecast Multizone Controller Listener will be added for Cast device: %s [%s]" % (scDevice.Title, scDevice.DiscoveryResult.HostIpTitle))

                    #             # add cast device to multizone controller instance.  this will add a listener
                    #             # for multizone status events to be processed, which allows us to keep track
                    #             # of which device is a group leader.
                    #             castMultizoneController = MultizoneController(castDevice.uuid)
                    #             castMultizoneController.register_listener(SpotifyConnectZeroconfCastMultiZoneListener(self, self._ZeroconfInstance, self._Zeroconf_RLock, castMultizoneController, castDevice))
                    #             castDevice.register_handler(castMultizoneController)
                    #             #castDevice.register_connection_listener(MyConnectionStatusListener(castMultizoneController))
                    #             castMultizoneController.update_members()  # Request an initial status

                    #             # add cast multizone controller to active multizone controllers collection.
                    #             self._CastMultiZoneControllers[str(castDevice.uuid)] = castMultizoneController

                    #             # trace.
                    #             _logsi.LogArray(SILevel.Verbose, "Chromecast Multizone Controller Listener was added for Cast device: %s [%s] (initial members)" % (scDevice.Title, scDevice.DiscoveryResult.HostIpTitle), castMultizoneController.members)

                    # except Exception as ex:

                    #     # trace.
                    #     _logsi.LogException("%s - MultiZoneController register_listener Exception: %s" % (self.name, str(ex)), ex, logToSystemLogger=False)



                    # add new Spotify Connect Device to devices collection.
                    self._SpotifyConnectDevices.Items.append(scDevice)
                    self._SpotifyConnectDevices.DateLastRefreshed = datetime.utcnow().timestamp()

                    # trace.
                    _logsi.LogObject(SILevel.Verbose, "Chromecast Zeroconf added SpotifyConnectDevices collection entry: \"%s\" (%s)" % (scDevice.Name, scDevice.DiscoveryResult.Name), scDevice, excludeNonPublic=True, colorValue=SIColors.ForestGreen)
                    _logsi.LogObject(SILevel.Debug, "SpotifyConnectDevice info: %s (DeviceInfo / getInfo)" % (scDevice.Title), scDevice.DeviceInfo, excludeNonPublic=True)
                    _logsi.LogObject(SILevel.Debug, "SpotifyConnectDevice info: %s (DiscoveryResult) [%s]" % (scDevice.Title, scDevice.DiscoveryResult.HostIpTitle), scDevice.DiscoveryResult, excludeNonPublic=True)

                    # sort devices collection by device name.
                    if (len(self._SpotifyConnectDevices.Items) > 0):
                        self._SpotifyConnectDevices.Items.sort(key=lambda x: (x.Name or "").lower(), reverse=False)

                    # raise event.
                    self._RaiseDeviceAdded(scDevice)

                else:

                    # trace.
                    _logsi.LogDebug("Updating existing SpotifyConnectDevice instance from CastInfo data: \"%s\" (%s) [key=%s]" % (zeroconfDiscoveryResult.DeviceName, zeroconfDiscoveryResult.Name, zeroconfDiscoveryResult.Key))

                    # get existing Spotify Connect Device instance.
                    scDevice = self._SpotifyConnectDevices.Items[idx]

                    # were any changes made to the zeroconf discovery results?
                    if (not scDevice.DiscoveryResult.Equals(zeroconfDiscoveryResult)):

                        # trace.
                        _logsi.LogObject(SILevel.Debug, "SpotifyConnectDevice info: \"%s\" (OLD DeviceInfo / getInfo)" % (scDevice.Title), scDevice.DeviceInfo, excludeNonPublic=True)
                        _logsi.LogObject(SILevel.Debug, "SpotifyConnectDevice info: \"%s\" (OLD DiscoveryResult) [%s]" % (scDevice.Title, scDevice.DiscoveryResult.HostIpTitle), scDevice.DiscoveryResult, excludeNonPublic=True)

                        # set zeroconf discovery result properties.
                        scDevice.DiscoveryResult = zeroconfDiscoveryResult

                        # did the device name change?  if so, then update name and id properties,
                        # as well as the corresponding getInfo properties.
                        if (scDevice.Name != zeroconfDiscoveryResult.DeviceName):

                            # if Spotify Cast App is active on the cast device then request that it stop
                            # as it will need to re-register the new device name and device id.
                            castAppTask:SpotifyConnectZeroconfCastAppTask = self._CastAppTasks.get(scDevice.DiscoveryResult.Key, None)
                            if (castAppTask is not None):
                                if (castAppTask.is_alive()):
                                    _logsi.LogVerbose("%s - Stopping Spotify Cast App task (due to device rename)" % (self.name))
                                    castAppTask.IsStopRequested = True
                                    castAppTask.join()
                                    _logsi.LogVerbose("%s - Spotify Cast App task was stopped successfully (due to device rename)" % (self.name))
                                self._CastAppTasks.pop(scDevice.DiscoveryResult.Key, None)

                            # update name and id properties, as well as the corresponding getInfo properties.
                            newDeviceName:str = zeroconfDiscoveryResult.DeviceName
                            newDeviceId:str = self.GetSpotifyDeviceIDFromName(zeroconfDiscoveryResult.DeviceName)
                            _logsi.LogVerbose("Chromecast Zeroconf SpotifyConnectDevice entry name and id changed from %s to \"%s\" (%s)" % (scDevice.Title, newDeviceName, newDeviceId))
                            scDevice.Name = newDeviceName
                            scDevice.Id = newDeviceId
                            scDevice.DeviceInfo.DeviceId = newDeviceId
                            scDevice.DeviceInfo.RemoteName = newDeviceName

                        # update existing Spotify Connect Device in devices collection.
                        self._SpotifyConnectDevices.Items[idx] = scDevice
                        self._SpotifyConnectDevices.DateLastRefreshed = datetime.utcnow().timestamp()

                        # trace.
                        _logsi.LogObject(SILevel.Verbose, "Chromecast Zeroconf updated SpotifyConnectDevices collection entry: \"%s\" (%s)" % (scDevice.Name, scDevice.DiscoveryResult.Name), scDevice, excludeNonPublic=True, colorValue=SIColors.ForestGreen)
                        _logsi.LogObject(SILevel.Debug, "SpotifyConnectDevice info: %s (DeviceInfo / getInfo)" % (scDevice.Title), scDevice.DeviceInfo, excludeNonPublic=True)
                        _logsi.LogObject(SILevel.Debug, "SpotifyConnectDevice info: %s (DiscoveryResult) [%s]" % (scDevice.Title, scDevice.DiscoveryResult.HostIpTitle), scDevice.DiscoveryResult, excludeNonPublic=True)

                        # sort devices collection by device name.
                        if (len(self._SpotifyConnectDevices.Items) > 0):
                            self._SpotifyConnectDevices.Items.sort(key=lambda x: (x.Name or "").lower(), reverse=False)

                        # raise event.
                        self._RaiseDeviceUpdated(scDevice)

                    else:

                        # trace.
                        _logsi.LogObject(SILevel.Verbose, "SpotifyConnectDevice info: \"%s\" (ignored; DiscoveryResult did not change)" % (scDevice.Name), scDevice.DiscoveryResult, excludeNonPublic=True)

            except Exception as ex:

                # trace.
                _logsi.LogException("%s - Exception: %s" % (self.name, str(ex)), ex, logToSystemLogger=False)
            
                # ignore exceptions, as there is nothing we can do at this point.

            finally:

                # trace.
                _logsi.LeaveMethod(SILevel.Debug)


    def OnServiceInfoRemovedChromecast(
        self, 
        zeroconfDiscoveryResult: ZeroconfDiscoveryResult,
        uuid:UUID, 
        serviceName:str, 
        castInfo:CastInfo
        ) -> None:
        """
        Called when a cast has been lost (MDNS info expired or host down).

        Args:
            zeroconfDiscoveryResult (ZeroconfDiscoveryResult):
                A `ZeroconfDiscoveryResult` object that contains discovery details.
            uuid (UUID):
                The cast's uuid, which is the dictionary key to find the chromecast 
                metadata in CastBrowser.devices collection.
            serviceName (str):
                Last valid MDNS service name or host:port.
            castInfo (CastInfo):
                CastInfo for the service to aid cleanup.

        This could be called under the following conditions:
        - when a Chromecast device has logged out of zeroconf and left the network.
        - transfer playback failed (e.g. device restriction, etc).

        This method will be called in a thread-safe manner, as the caller is using
        the `_Zeroconf_RLock` object to control access.
        """
        # syncronize access via lock, as we are accessing the collection.
        with self._SpotifyConnectDevices_RLock:

            try:

                # trace.
                _logsi.EnterMethod(SILevel.Debug)

                # get cast device instance by discovery key.
                # note that we cannot use discovery name here, as Google Groups use different
                # names that refer to the same key value!
                idx:int = self._SpotifyConnectDevices.GetDeviceIndexByDiscoveryKey(zeroconfDiscoveryResult.Key)
                if (idx == -1):

                    # trace.
                    _logsi.LogVerbose("SpotifyConnectDevice instance could not be found to remove: \"%s\" (%s) [%s]" % (zeroconfDiscoveryResult.DeviceName, zeroconfDiscoveryResult.Name, zeroconfDiscoveryResult.Key))

                else:

                    # trace.
                    _logsi.LogVerbose("Removing existing SpotifyConnectDevice instance from CastInfo data: \"%s\" (%s) [%s]" % (zeroconfDiscoveryResult.DeviceName, zeroconfDiscoveryResult.Name, zeroconfDiscoveryResult.Key))


                    # TEST TODO REMOVEME
                    # # is this a Google Cast Group?
                    # if (castInfo.cast_type == CAST_TYPE_GROUP):

                    #     try:

                    #             # deregister our MultiZoneManagerListener instance for this device.
                    #             self._CastMultiZoneManager.deregister_listener(castInfo.uuid, None)

                    #             #multizoneListener:SpotifyConnectZeroconfCastMultiZoneListener = SpotifyConnectZeroconfCastMultiZoneListener(self, self.ZeroconfInstance)
                    #             #castDevice.multizone_manager.register_listener(multizoneListener)

                    #     except Exception as ex:

                    #         # trace.
                    #         _logsi.LogException("%s - get_multizone_status Exception: %s" % (self.name, str(ex)), ex, logToSystemLogger=False)


                    # remove existing Spotify Connect Device instance from devices collection.
                    scDevice:SpotifyConnectDevice = self._SpotifyConnectDevices.Items.pop(idx)
                    self._SpotifyConnectDevices.DateLastRefreshed = datetime.utcnow().timestamp()

                    # trace.
                    _logsi.LogObject(SILevel.Verbose, "Chromecast Zeroconf removed SpotifyConnectDevices collection entry: \"%s\" (%s)" % (scDevice.Name, scDevice.DiscoveryResult.Name), scDevice, excludeNonPublic=True, colorValue=SIColors.DarkOrange)
                    _logsi.LogObject(SILevel.Debug, "SpotifyConnectDevice info: %s (DeviceInfo / getInfo)" % (scDevice.Title), scDevice.DeviceInfo, excludeNonPublic=True)
                    _logsi.LogObject(SILevel.Debug, "SpotifyConnectDevice info: %s (DiscoveryResult) [%s]" % (scDevice.Title, scDevice.DiscoveryResult.HostIpTitle), scDevice.DiscoveryResult, excludeNonPublic=True)

                    # raise event.
                    self._RaiseDeviceRemoved(scDevice)

            except Exception as ex:

                # trace.
                _logsi.LogException("%s - Exception: %s" % (self.name, str(ex)), ex, logToSystemLogger=False)
            
                # ignore exceptions, as there is nothing we can do at this point.

            finally:

                # trace.
                _logsi.LeaveMethod(SILevel.Debug)


    def OnCastGetInfoResponseReceived(
        self, 
        uuid:UUID, 
        info:ZeroconfGetInfo
        ) -> None:
        """
        Called when the cast app task has received a Spotify Connect Zeroconf GetInfoResponse
        data structure.  

        Args:
            uuid (UUID):
                Spotify Connect device that was added.
            info (ZeroconfGetInfo):
                A `ZeroconfGetInfo` instance that contains the GetInfoResponse data.

        This method allows us to update the SpotifyConnectDevice entry with the Spotify Connect 
        Zeroconf device information.                
        """
        # syncronize access via lock, as we are accessing the collection.
        with self._SpotifyConnectDevices_RLock:

            # get device instance.
            scDevice:SpotifyConnectDevice = self._SpotifyConnectDevices.GetDeviceByDiscoveryKey(str(uuid))
            if (scDevice is not None):

                # ZeroconfGetInfo class properties.
                # we use underscore property reference for those that don't have a property setter method.
                scDevice.DeviceInfo._AccountReq = info.AccountReq
                scDevice.DeviceInfo.ActiveUser = info.ActiveUser
                scDevice.DeviceInfo._Aliases = info.Aliases
                scDevice.DeviceInfo._Availability = info.Availability
                scDevice.DeviceInfo._ClientId = info.ClientId
                scDevice.DeviceInfo.DeviceId = info.DeviceId            # same as zeroconf deviceId
                scDevice.DeviceInfo._GroupStatus = info.GroupStatus
                scDevice.DeviceInfo._LibraryVersion = info.LibraryVersion
                scDevice.DeviceInfo.ProductId = info.ProductId
                scDevice.DeviceInfo.PublicKey = info.PublicKey
                scDevice.DeviceInfo.RemoteName = info.RemoteName        # same as zeroconf friendly_name
                scDevice.DeviceInfo._ResolverVersion = info.ResolverVersion
                scDevice.DeviceInfo._Scope = info.Scope
                scDevice.DeviceInfo._SupportedCapabilities = info.SupportedCapabilities
                scDevice.DeviceInfo._SupportedDrmMediaFormats = info.SupportedDrmMediaFormats
                scDevice.DeviceInfo._TokenType = info.TokenType
                scDevice.DeviceInfo._Version = info.Version
                scDevice.DeviceInfo._VoiceSupport = info.VoiceSupport

                # we will leave the following properties with their current values as
                # set from the CastInfo instance, as they contain more consistent values
                # that properly describe the device.
                #scDevice.DeviceInfo.BrandDisplayName = info.BrandDisplayName
                #scDevice.DeviceInfo.DeviceType = info.DeviceType
                #scDevice.DeviceInfo.ModelDisplayName = info.ModelDisplayName

                # ZeroconfResponse base class properties.
                scDevice.DeviceInfo._ResponseSource = info.ResponseSource
                scDevice.DeviceInfo.SpotifyError = info.SpotifyError
                scDevice.DeviceInfo.Status = info.Status
                scDevice.DeviceInfo.StatusString = info.StatusString

                # trace.
                _logsi.LogObject(SILevel.Debug, "SpotifyConnectDevice info: %s (DeviceInfo / getInfo, OnCastGetInfoResponseReceived)" % (scDevice.Title), scDevice.DeviceInfo, excludeNonPublic=True)

                # log a warning if the received deviceId did not match the expected deviceId.
                if (scDevice.Id != info.DeviceId):
                    _logsi.LogVerbose("OnCastGetInfoResponseReceived deviceId mismatch for device: %s - expected \"%s\", but received \"%s\"" % (scDevice.Title, scDevice.Id, info.DeviceId), colorValue=SIColors.Red)


    def OnCastZeroconfResponseReceived(
        self, 
        uuid:UUID, 
        response:ZeroconfResponse,
        ) -> None:
        """
        Called when the cast app task has received a Spotify Connect ZeroconfResponse
        data structure.  

        Args:
            uuid (UUID):
                Spotify Connect device that was added.
            response (ZeroconfResponse):
                A `ZeroconfResponse` instance that contains the zeroconf response data.

        This method allows us to update the SpotifyConnectDevice entry with the Spotify Connect 
        Zeroconf response information.
        """
        # syncronize access via lock, as we are accessing the collection.
        with self._SpotifyConnectDevices_RLock:

            # get device instance.
            scDevice:SpotifyConnectDevice = self._SpotifyConnectDevices.GetDeviceByDiscoveryKey(str(uuid))
            if (scDevice is not None):

                # ZeroconfResponse class properties.
                scDevice.ZeroconfResponseInfo.ResponseSource = response.ResponseSource
                scDevice.ZeroconfResponseInfo.SpotifyError = response.SpotifyError
                scDevice.ZeroconfResponseInfo.Status = response.Status
                scDevice.ZeroconfResponseInfo.StatusString = response.StatusString

                # trace.
                _logsi.LogObject(SILevel.Debug, "SpotifyConnectDevice info: \"%s\" (ZeroconfResponseInfo)" % (scDevice.Name), scDevice.ZeroconfResponseInfo, excludeNonPublic=True)

                # indicate zeroconf response data was received.
                if (response.ResponseSource == TYPE_ADD_USER_RESPONSE) or (response.ResponseSource == TYPE_ADD_USER_ERROR) \
                or (response.ResponseSource == TYPE_GET_INFO_ERROR):
                    self.WaitForActivationComplete.set()
                elif (response.ResponseSource == TYPE_TRANSFER_SUCCESS) or (response.ResponseSource == TYPE_TRANSFER_ERROR):
                    self.WaitForTransferComplete.set()
                elif (response.ResponseSource == TYPE_LAUNCH_ERROR):
                    self.WaitForActivationComplete.set()


    def OnServiceInfoAddedUpdatedSpotifyConnect(
        self, 
        zeroconfDiscoveryResult:ZeroconfDiscoveryResult
        ) -> None:
        """
        Called when a new Spotify Connect ServiceInfo record has been discovered
        or updated for a Spotify Connect device.

        Args:
            zeroconfDiscoveryResult (ZeroconfDiscoveryResult):
                A `ZeroconfDiscoveryResult` object that contains discovery details.

        This method will be called in a thread-safe manner, as the caller is using
        the `_Zeroconf_RLock` object to control access.
        """
        # syncronize access via lock, as we are accessing the collection.
        with self._SpotifyConnectDevices_RLock:

            try:

                # trace.
                _logsi.EnterMethod(SILevel.Debug)

                # add / update discovered results by serviceinfo key value. 
                # we use the serviceinfo NAME value (not KEY) since some manufacturers use random ip port 
                # numbers, and the port number could have been updated.  in this case, the name SHOULD remain the same.
                # note that a different serviceinfo name SHOULD be created for speaker groups; at least they are for BOSE devices.
                scDevice:SpotifyConnectDevice = None
                idx:int = self._SpotifyConnectDevices.GetDeviceIndexByDiscoveryName(zeroconfDiscoveryResult.Name)
                if (idx == -1):

                    # trace.
                    _logsi.LogVerbose("Creating new SpotifyConnectDevice instance from ServiceInfo data: \"%s\" (%s)" % (zeroconfDiscoveryResult.DeviceName, zeroconfDiscoveryResult.Name))

                    # By default, the ZeroConf DeviceName is used for the device name value; this
                    # will change later when the Spotify Connect `getInfo` call is made to retrieve the
                    # RemoteName value, which is what Spotify Connect capable players display as a device name.
                    # For most manufacturers, the ZeroConf DeviceName is an internal-use type of value (e.g. "sonosRINCON_38420B909DC801400").
                    # For other manufacturers, this is a user-friendly type of value (e.g. "Bose-ST10-1").
                    # Here are some examples (by manufacturer):

                    # Manufacturer  ZeroConf DeviceName               getInfo Remotename                     getInfo Alias
                    # ------------  ------------------------------    -----------------------------------    -----------------------
                    # Sonos         sonosRINCON_38420B909DC801400"    Office                                 n/a
                    # Bose          Bose-ST10-1                       Bose-ST10-1                            n/a
                    # Bose          Bose-ST10-1 + Bose-ST10-2 (L+R)   Bose-ST10-1 (if stereo paired)         n/a
                    # Bose          Bose-ST10-1 Group                 Bose-ST10-1 (if zoned)                 n/a
                    # Denon         0005cdb737b2LivingRoom            Living Room                            n/a
                    # Wiim          FF98F35902BB6CA851FE34D5          n/a (uses Alias)                       "Kitchen Speakers"

                    # create a new Spotify Connect Device instance.
                    scDevice = SpotifyConnectDevice()
                    scDevice.Name = zeroconfDiscoveryResult.DeviceName

                    # set zeroconf discovery result properties.
                    scDevice.DiscoveryResult = zeroconfDiscoveryResult

                    # verify CPath property was present; if not, log a warning as the endpoint url will be invalid!
                    if (zeroconfDiscoveryResult.SpotifyConnectCPath is None):
                        _logsi.LogWarning("Spotify Connect device Zeroconf ServiceInfo data did not contain a CPath value: \"%s\" (%s)" % (zeroconfDiscoveryResult.DeviceName, zeroconfDiscoveryResult.Name))

                    try:

                        # trace.
                        _logsi.LogVerbose("Retrieving Spotify Connect device information: %s" % (zeroconfDiscoveryResult.Id))

                        # create connection object to retrieve spotify connect device information (via direct ip address).
                        zconn:ZeroconfConnect = ZeroconfConnect(
                            zeroconfDiscoveryResult.HostIpAddress,
                            zeroconfDiscoveryResult.HostIpPort,
                            zeroconfDiscoveryResult.SpotifyConnectCPath,
                            zeroconfDiscoveryResult.SpotifyConnectVersion,
                            useSSL=False,
                            tokenStorageDir=self.SpotifyClientInstance.TokenStorageDir,
                            tokenStorageFile=self.SpotifyClientInstance.TokenStorageFile
                        )

                        # retrieve initial spotify connect device information (by ip address).
                        scDevice.DeviceInfo = zconn.GetInformation()
                        scDevice.Id = scDevice.DeviceInfo.DeviceId
                        scDevice.Name = scDevice.DeviceInfo.RemoteName

                        # if remote name was not specified, then set device name to first alias name.
                        # note that we will not reset the RemoteName, as the "" value indicates an alias is in use.
                        if ((scDevice.DeviceInfo.RemoteName + "").strip() == ""):
                            if (scDevice.DeviceInfo.HasAliases):
                                _logsi.LogVerbose("Spotify Connect Zeroconf GetInformation alias name will be utilized for Zeroconf Discovery Result: \"%s\" (%s)" % (zeroconfDiscoveryResult.DeviceName, zeroconfDiscoveryResult.Name))
                                scDevice.Name = scDevice.DeviceInfo.Aliases[0].Name

                    except Exception as ex:

                        # trace.
                        _logsi.LogVerbose("Could not retrieve Spotify Connect device information by ip address; retrying with DNS server alias \"%s\"" % (zeroconfDiscoveryResult.Server))

                        try:

                            # *IMPORTANT* This call can take up to 20 seconds to timeout because it is using DNS
                            # resolution to find the device.  the timeout is a system-level value, so it cannot be
                            # controlled by this api!
                        
                            # create connection object to retrieve spotify connect device information (via dns alias).
                            zconn:ZeroconfConnect = ZeroconfConnect(
                                zeroconfDiscoveryResult.Server,
                                zeroconfDiscoveryResult.HostIpPort,
                                zeroconfDiscoveryResult.SpotifyConnectCPath,
                                zeroconfDiscoveryResult.SpotifyConnectVersion,
                                useSSL=False,
                                tokenStorageDir=self.SpotifyClientInstance.TokenStorageDir,
                                tokenStorageFile=self.SpotifyClientInstance.TokenStorageFile
                            )

                            # retrieve initial spotify connect device information (by dns alias).
                            scDevice.DeviceInfo = zconn.GetInformation()
                            scDevice.Id = scDevice.DeviceInfo.DeviceId
                            scDevice.Name = scDevice.DeviceInfo.RemoteName
                    
                            # if remote name was not specified, then set device name to first alias name.
                            # note that we will not reset the RemoteName, as the "" value indicates an alias is in use.
                            if ((scDevice.DeviceInfo.RemoteName + "").strip() == ""):
                                if (scDevice.DeviceInfo.HasAliases):
                                    _logsi.LogVerbose("Spotify Connect Zeroconf GetInformation alias name will be utilized for Zeroconf Discovery Result: \"%s\" (%s)" % (zeroconfDiscoveryResult.DeviceName, zeroconfDiscoveryResult.Name))
                                    scDevice.Name = scDevice.DeviceInfo.Aliases[0].Name

                            # update HostIpAddress in discovery result so it knows to use the dns alias
                            # instead of the ip address.
                            _logsi.LogVerbose("Spotify Connect Zeroconf GetInformation call for Instance Name \"%s\" (%s) was resolved using DNS Server alias; HostIpAddress will be updated with the resolved ip address" % (zeroconfDiscoveryResult.DeviceName, zeroconfDiscoveryResult.Server))
                            resolvedIpAddress = socket.gethostbyname(zeroconfDiscoveryResult.Server)
                            zeroconfDiscoveryResult.HostIpAddress = resolvedIpAddress
                            
                        except Exception as ex:
                            
                            # trace.
                            _logsi.LogException("Spotify Connect Zeroconf GetInformation call failed for device instance \"%s\" (ip=%s:%s): %s" % (scDevice.Name, zeroconfDiscoveryResult.HostIpAddress, zeroconfDiscoveryResult.HostIpPort, str(ex)), ex, logToSystemLogger=False)
                    
                            # if Getinformation call failed, then default device information.
                            scDevice.DeviceInfo = ZeroconfGetInfo()
                            scDevice.DeviceInfo.DeviceId = "getInfoError"
                            scDevice.DeviceInfo.RemoteName = zeroconfDiscoveryResult.DeviceName
                            scDevice.DeviceInfo.ResponseSource = "spotifywebapiPython"
                            scDevice.DeviceInfo.Status = 9999
                            scDevice.DeviceInfo.StatusString = str(ex)
                            scDevice.Id = scDevice.DeviceInfo.DeviceId

                    # did this device change from a dynamic device (e.g. non-zeroconf) to a zeroconf device?
                    # this can happen if the device is initially added as a dynamic device, then the zeroconf
                    # device is discovered.  if so, we will remove the dynamic device entry.
                    spDynamicDevice:SpotifyConnectDevice = self._SpotifyConnectDevices.GetDeviceById(scDevice.DeviceInfo.DeviceId)
                    if (spDynamicDevice is not None):

                        # trace.
                        _logsi.LogVerbose("Spotify Connect Zeroconf is converting SpotifyConnectDevice entry %s from dynamic to zeroconf" % (spDynamicDevice.Title))

                        # copy real-time status dynamic properties to zerconf object.
                        scDevice.IsActiveDevice = spDynamicDevice.IsActiveDevice
                        scDevice.IsInDeviceList = spDynamicDevice.IsInDeviceList

                        # at this point we will remove the device from the collection so that it can be
                        # replaced with the static device entry; this will also remove any duplicate
                        # device id entries, which can appear for some manufacturers when devices are 
                        # grouped, zoned, or stereo paired (e.g. Bose).
                        dynamicOnly:bool = True
                        if (scDevice.DiscoveryResult.IsDynamicDevice == False) and (spDynamicDevice.DiscoveryResult.IsDynamicDevice == False):
                            dynamicOnly = False
                        self.RemoveDevice(spDynamicDevice.Id, dynamicDeviceOnly=dynamicOnly)

                    # add new Spotify Connect Device to devices collection.
                    self._SpotifyConnectDevices.Items.append(scDevice)
                    self._SpotifyConnectDevices.DateLastRefreshed = datetime.utcnow().timestamp()

                    # trace.
                    _logsi.LogObject(SILevel.Verbose, "Spotify Connect Zeroconf added SpotifyConnectDevices collection entry: \"%s\" (%s)" % (scDevice.Name, scDevice.DiscoveryResult.Name), scDevice, excludeNonPublic=True, colorValue=SIColors.ForestGreen)
                    _logsi.LogObject(SILevel.Debug, "SpotifyConnectDevice info: %s (DeviceInfo / getInfo)" % (scDevice.Title), scDevice.DeviceInfo, excludeNonPublic=True)
                    _logsi.LogObject(SILevel.Debug, "SpotifyConnectDevice info: %s (DiscoveryResult) [%s]" % (scDevice.Title, scDevice.DiscoveryResult.HostIpTitle), scDevice.DiscoveryResult, excludeNonPublic=True)

                    # sort devices collection by device name.
                    if (len(self._SpotifyConnectDevices.Items) > 0):
                        self._SpotifyConnectDevices.Items.sort(key=lambda x: (x.Name or "").lower(), reverse=False)

                    try:

                        # is this a Sonos device?
                        if (scDevice.IsSonos):

                            # create a Sonos Controller instance for the device, retrieve the Sonos speaker information, 
                            # and add it to the Sonos players collection.  use device ip address as the key, as the
                            # Spotify Web API reports "id=null" for restricted devices in playerstate!
                            _logsi.LogVerbose("Sonos device detected; creating Sonos Controller instance for device: %s (ip=%s)" % (scDevice.Title, zeroconfDiscoveryResult.HostIpAddress))
                            sonosPlayer:SoCo = SoCo(zeroconfDiscoveryResult.HostIpAddress)
                            self._SonosPlayers[zeroconfDiscoveryResult.HostIpAddress] = sonosPlayer

                            try:
                                sonosPlayer.get_speaker_info()
                            except Exception as ex:
                                _logsi.LogException("Could not get speaker info for Sonos Controller instance: %s" % (str(ex)), ex, logToSystemLogger=False)

                            # trace.
                            if (_logsi.IsOn(SILevel.Verbose)):
                                _logsi.LogObject(SILevel.Verbose, "Sonos Controller instance for device: %s" % (scDevice.Title), sonosPlayer)
                                _logsi.LogDictionary(SILevel.Verbose, "Sonos Controller instance for device: %s (speaker_info)" % (scDevice.Title), sonosPlayer.speaker_info)
                                _logsi.LogObject(SILevel.Verbose, "Sonos Controller instance for device: %s (group)" % (scDevice.Title), sonosPlayer.group)
                                _logsi.LogObject(SILevel.Verbose, "Sonos Controller instance for device: %s (zone_group_state)" % (scDevice.Title), sonosPlayer.zone_group_state)
                                _logsi.LogEnumerable(SILevel.Verbose, "Sonos Controller instance for device: %s (all_zones)" % (scDevice.Title), sonosPlayer.all_zones)

                    except:

                        # trace.
                        _logsi.LogException("%s - Could not create Sonos Control API reference: %s" % (self.name, str(ex)), ex, logToSystemLogger=False)
            
                        # ignore exceptions, as there is nothing we can do at this point.

                    # raise event.
                    self._RaiseDeviceAdded(scDevice)

                else:

                    # trace.
                    _logsi.LogDebug("Updating existing SpotifyConnectDevice instance from ServiceInfo data: \"%s\" (%s)" % (zeroconfDiscoveryResult.DeviceName, zeroconfDiscoveryResult.Name))

                    # get existing Spotify Connect Device instance.
                    scDevice = self._SpotifyConnectDevices.Items[idx]

                    # were any changes made to the zeroconf discovery results?
                    if (not scDevice.DiscoveryResult.Equals(zeroconfDiscoveryResult)):

                        # trace.
                        _logsi.LogObject(SILevel.Debug, "SpotifyConnectDevice info: \"%s\" (OLD DeviceInfo / getInfo)" % (scDevice.Title), scDevice.DeviceInfo, excludeNonPublic=True)
                        _logsi.LogObject(SILevel.Debug, "SpotifyConnectDevice info: \"%s\" (OLD DiscoveryResult) [%s]" % (scDevice.Title, scDevice.DiscoveryResult.HostIpTitle), scDevice.DiscoveryResult, excludeNonPublic=True)

                        # set zeroconf discovery result properties.
                        scDevice.DiscoveryResult = zeroconfDiscoveryResult

                        # did the device name change?  if so, then update name and id properties,
                        # as well as the corresponding getInfo properties.
                        if (scDevice.Name != zeroconfDiscoveryResult.DeviceName):
                            newDeviceName:str = zeroconfDiscoveryResult.DeviceName
                            newDeviceId:str = self.GetSpotifyDeviceIDFromName(zeroconfDiscoveryResult.DeviceName)
                            _logsi.LogVerbose("Spotify Connect Zeroconf SpotifyConnectDevice entry name and id changed from %s to \"%s\" (%s)" % (scDevice.Title, newDeviceName, newDeviceId))
                            scDevice.Name = newDeviceName
                            scDevice.Id = newDeviceId
                            scDevice.DeviceInfo.DeviceId = newDeviceId
                            scDevice.DeviceInfo.RemoteName = newDeviceName

                        # update existing Spotify Connect Device in devices collection.
                        self._SpotifyConnectDevices.Items[idx] = scDevice
                        self._SpotifyConnectDevices.DateLastRefreshed = datetime.utcnow().timestamp()

                        # trace.
                        _logsi.LogObject(SILevel.Verbose, "Spotify Connect Zeroconf updated SpotifyConnectDevices collection entry: \"%s\" (%s)" % (scDevice.Name, scDevice.DiscoveryResult.Name), scDevice, excludeNonPublic=True, colorValue=SIColors.ForestGreen)
                        _logsi.LogObject(SILevel.Debug, "SpotifyConnectDevice info: %s (DeviceInfo / getInfo)" % (scDevice.Title), scDevice.DeviceInfo, excludeNonPublic=True)
                        _logsi.LogObject(SILevel.Debug, "SpotifyConnectDevice info: %s (DiscoveryResult) [%s]" % (scDevice.Title, scDevice.DiscoveryResult.HostIpTitle), scDevice.DiscoveryResult, excludeNonPublic=True)

                        # sort devices collection by device name.
                        if (len(self._SpotifyConnectDevices.Items) > 0):
                            self._SpotifyConnectDevices.Items.sort(key=lambda x: (x.Name or "").lower(), reverse=False)

                        # raise event.
                        self._RaiseDeviceUpdated(scDevice)

                    else:

                        # trace.
                        _logsi.LogObject(SILevel.Verbose, "SpotifyConnectDevice info: \"%s\" (ignored; DiscoveryResult did not change)" % (scDevice.Name), scDevice.DiscoveryResult, excludeNonPublic=True)

            except Exception as ex:

                # trace.
                _logsi.LogException("%s - Exception: %s" % (self.name, str(ex)), ex, logToSystemLogger=False)
            
                # ignore exceptions, as there is nothing we can do at this point.

            finally:

                # trace.
                _logsi.LeaveMethod(SILevel.Debug)


    def OnServiceInfoRemovedSpotifyConnect(
        self, 
        zeroconfDiscoveryResult:ZeroconfDiscoveryResult
        ) -> None:
        """
        Called when an mDNS service is lost.

        Args:
            zeroconfDiscoveryResult (ZeroconfDiscoveryResult):
                A `ZeroconfDiscoveryResult` object that contains discovery details.

        This method will be called in a thread-safe manner, as the caller is using
        the `_Zeroconf_RLock` object to control access.
        """
        # syncronize access via lock, as we are accessing the collection.
        with self._SpotifyConnectDevices_RLock:

            try:

                # trace.
                _logsi.EnterMethod(SILevel.Debug)

                # remove discovered results by serviceinfo key value. 
                # we use the serviceinfo NAME value (not KEY) since that is the only information available on
                # a remove serviceinfo request.
                idx:int = self._SpotifyConnectDevices.GetDeviceIndexByDiscoveryName(zeroconfDiscoveryResult.Name)
                if (idx == -1):

                    # trace.
                    _logsi.LogVerbose("SpotifyConnectDevice instance could not be found to remove: \"%s\" (%s)" % (zeroconfDiscoveryResult.DeviceName, zeroconfDiscoveryResult.Name))

                else:

                    # trace.
                    _logsi.LogVerbose("Removing existing SpotifyConnectDevice instance from ServiceInfo data: \"%s\" (%s)" % (zeroconfDiscoveryResult.DeviceName, zeroconfDiscoveryResult.Name))

                    # remove existing Spotify Connect Device instance from devices collection.
                    scDevice:SpotifyConnectDevice = self._SpotifyConnectDevices.Items.pop(idx)
                    self._SpotifyConnectDevices.DateLastRefreshed = datetime.utcnow().timestamp()

                    # trace.
                    _logsi.LogObject(SILevel.Verbose, "Spotify Connect Zeroconf removed SpotifyConnectDevices collection entry: \"%s\" (%s)" % (scDevice.Name, scDevice.DiscoveryResult.Name), scDevice, excludeNonPublic=True, colorValue=SIColors.DarkOrange)
                    _logsi.LogObject(SILevel.Debug, "SpotifyConnectDevice info: %s (DeviceInfo / getInfo)" % (scDevice.Title), scDevice.DeviceInfo, excludeNonPublic=True)
                    _logsi.LogObject(SILevel.Debug, "SpotifyConnectDevice info: %s (DiscoveryResult) [%s]" % (scDevice.Title, scDevice.DiscoveryResult.HostIpTitle), scDevice.DiscoveryResult, excludeNonPublic=True)

                    # raise event.
                    self._RaiseDeviceRemoved(scDevice)

            except Exception as ex:

                # trace.
                _logsi.LogException("%s - Exception: %s" % (self.name, str(ex)), ex, logToSystemLogger=False)
            
                # ignore exceptions, as there is nothing we can do at this point.

            finally:

                # trace.
                _logsi.LeaveMethod(SILevel.Debug)


    def _RaiseDeviceAdded(
        self, 
        device:SpotifyConnectDevice
        ) -> None:
        """
        Raises the `DeviceAdded` event.

        Args:
            device (SpotifyConnectDevice):
                Spotify Connect device that was added.
        """
        try:
        
            # raise event.
            args:SpotifyConnectDeviceEventArgs = SpotifyConnectDeviceEventArgs(device)
            self.DeviceAdded(self, args)

        except Exception as ex:

            # ignore exceptions.
            pass

        
    @abstractmethod
    def OnDeviceAdded(
        self, 
        sender:object, 
        e:SpotifyConnectDeviceEventArgs
        ) -> None:
        """
        Method that will handle the `DeviceAdded` event.
        Inheriting classes can override this method to handle the event.
        
        Args:
            sender (object):
                The object which fired the event.
            e (SpotifyConnectDeviceEventArgs):
                Arguments that contain detailed information related to the event.

        This event is fired when a Spotify Connect device has been added to the 
        SpotifyConnectDevices collection.

        This method will be called in a thread-safe manner, as the caller is using
        the `SpotifyConnectDevices_RLock` object to control access.
        """
        pass


    def _RaiseDeviceRemoved(
        self, 
        device:SpotifyConnectDevice
        ) -> None:
        """
        Raises the `DeviceRemoved` event.

        Args:
            device (SpotifyConnectDevice):
                Spotify Connect device that was removed.
        """
        try:
        
            # raise event.
            args:SpotifyConnectDeviceEventArgs = SpotifyConnectDeviceEventArgs(device)
            self.DeviceRemoved(self, args)

        except Exception as ex:

            # ignore exceptions.
            pass

        
    @abstractmethod
    def OnDeviceRemoved(
        self, 
        sender:object, 
        e:SpotifyConnectDeviceEventArgs
        ) -> None:
        """
        Method that will handle the `DeviceRemoved` event.
        Inheriting classes can override this method to handle the event.
        
        Args:
            sender (object):
                The object which fired the event.
            e (SpotifyConnectDeviceEventArgs):
                Arguments that contain detailed information related to the event.

        This event is fired when a Spotify Connect device has been removed from the 
        SpotifyConnectDevices collection.

        This method will be called in a thread-safe manner, as the caller is using
        the `SpotifyConnectDevices_RLock` object to control access.
        """
        pass


    def _RaiseDeviceUpdated(
        self, 
        device:SpotifyConnectDevice
        ) -> None:
        """
        Raises the `DeviceUpdated` event.

        Args:
            device (SpotifyConnectDevice):
                Spotify Connect device that was updated.
        """
        try:
        
            # raise event.
            args:SpotifyConnectDeviceEventArgs = SpotifyConnectDeviceEventArgs(device)
            self.DeviceUpdated(self, args)

        except Exception as ex:

            # ignore exceptions.
            pass

        
    @abstractmethod
    def OnDeviceUpdated(
        self, 
        sender:object, 
        e:SpotifyConnectDeviceEventArgs
        ) -> None:
        """
        Method that will handle the `DeviceUpdated` event.
        Inheriting classes can override this method to handle the event.
        
        Args:
            sender (object):
                The object which fired the event.
            e (SpotifyConnectDeviceEventArgs):
                Arguments that contain detailed information related to the event.

        This event is fired when a Spotify Connect device has been updated in the 
        SpotifyConnectDevices collection.

        This method will be called in a thread-safe manner, as the caller is using
        the `SpotifyConnectDevices_RLock` object to control access.
        """
        pass
