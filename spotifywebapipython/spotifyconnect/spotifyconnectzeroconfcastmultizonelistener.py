# external package imports.
from pychromecast.controllers.multizone import MultizoneController, MultiZoneControllerListener
from pychromecast.dial import MultizoneStatus, get_multizone_status
from pychromecast import Chromecast
import pychromecast
import threading
from uuid import UUID
from zeroconf import Zeroconf

# our package imports.
from spotifywebapipython.models import SpotifyConnectDevice, ZeroconfDiscoveryResult
# note - cannot reference `SpotifyConnectDirectoryTask` due to circular import!
# from .spotifyconnectdirectorytask import SpotifyConnectDirectoryTask

# get smartinspect logger reference; create a new session for this module name.
from smartinspectpython.siauto import SIAuto, SILevel, SISession, SIMethodParmListContext, SIColors
import logging

_logsi:SISession = SIAuto.Si.GetSession(__name__)
if (_logsi == None):
    _logsi = SIAuto.Si.AddSession(__name__, True)
_logsi.SystemLogger = logging.getLogger(__name__)


class SpotifyConnectZeroconfCastMultiZoneListener(MultiZoneControllerListener):
    """
    Google Chromecast Zeroconf MultiZone Listener class.
    
    Listens for Chromecast device multi-zone status updates for devices that
    support multi-zone / group functionality.
    """

    def __init__(
        self, 
        parentDirectory,
        zeroconfInstance:Zeroconf,
        zeroconf_RLock:threading.RLock,
        castMultizoneController:MultizoneController,
        castDevice:Chromecast,
        ) -> None:
        """
        Initializes a new instance of the class.

        Args:
            parentDirectory (SpotifyConnectDirectoryTask):
                Parent SpotifyConnectDirectoryTask instance.
            zeroconfInstance (Zeroconf):
                Zeroconf instance used to query zeroconf.
            zeroconf_RLock (threading.RLock):
                Lock object used to enforce thread-safe updates.
            castMultizoneController (MultizoneController)
                MultizoneController parent instance.
            castDevice (Chromecast):
                Chromecast device object.
        """
        # invoke base class method.
        super().__init__()

        # initialize storage.
        self._CastMultizoneController:MultizoneController = castMultizoneController
        self._CastDevice = castDevice
        self._ParentDirectory = parentDirectory
        self._ZeroconfInstance:Zeroconf = zeroconfInstance
        self._Zeroconf_RLock:threading.RLock = zeroconf_RLock


    def multizone_member_added(
        self, 
        group_uuid:str, 
        ) -> None:
        """
        Called when cast has been added to group identified by group_uuid.
        """
        # use lock, as multiple threads could be calling this method simultaneously.
        with self._Zeroconf_RLock:

            # copy passed parameters to thread-safe storage.
            argsGroupUuid:UUID = group_uuid
                
            apiMethodName:str = "multizone_member_added"
            apiMethodParms:SIMethodParmListContext = None

            try:

                # trace.
                apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
                apiMethodParms.AppendKeyValue("group_uuid", argsGroupUuid)
                _logsi.LogMethodParmList(SILevel.Debug, "Chromecast multizone group notification was received for group \"%s\"" % (argsGroupUuid), apiMethodParms, colorValue=SIColors.Lavender)

                # get device instance.
                scDevice:SpotifyConnectDevice = self._ParentDirectory._SpotifyConnectDevices.GetDeviceByDiscoveryKey(str(argsGroupUuid))
                if (scDevice is None):

                    # trace.
                    _logsi.LogVerbose("Could not find SpotifyConnectDevices instance for Cast Group discovery key: \"%s\"" % (str(argsGroupUuid)), colorValue=SIColors.Lavender)

                else:

                    # trace.
                    _logsi.LogVerbose("Chromecast member device %s was added to multizone group \"%s\"" % (scDevice.Title, self._CastDevice.cast_info.friendly_name), colorValue=SIColors.Lavender)

                    # dump the multizone status for the newly added member.
                    castMultiZoneStatus:MultizoneStatus = get_multizone_status(scDevice.DiscoveryResult.HostIpAddress, self._CastDevice.cast_info.services, self._ZeroconfInstance, 5)
                    _logsi.LogObject(SILevel.Verbose, "Chromecast member device multizone status: %s [%s] (get_multizone_status)" % (scDevice.Title, scDevice.DiscoveryResult.HostIpTitle), castMultiZoneStatus, colorValue=SIColors.Lavender)

            except Exception as ex:
            
                # trace.
                _logsi.LogException("Unhandled exception occured while processing Chromecast MultiZoneController notification (%s)" % (apiMethodName), ex, logToSystemLogger=False)
            
                # ignore exception, as nothing can be done about it.

            finally:

                # trace.
                _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def multizone_member_removed(
        self, 
        group_uuid, 
        ) -> None:
        """
        Called when cast has been removed from group identified by group_uuid.
        """
        # use lock, as multiple threads could be calling this method simultaneously.
        with self._Zeroconf_RLock:

            # copy passed parameters to thread-safe storage.
            argsGroupUuid:UUID = group_uuid
                
            apiMethodName:str = "multizone_member_removed"
            apiMethodParms:SIMethodParmListContext = None

            try:

                # trace.
                apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
                apiMethodParms.AppendKeyValue("group_uuid", argsGroupUuid)
                _logsi.LogMethodParmList(SILevel.Debug, "Chromecast multizone group notification was received for group \"%s\"" % (argsGroupUuid), apiMethodParms, colorValue=SIColors.Lavender)

                # get device instance.
                scDevice:SpotifyConnectDevice = self._ParentDirectory._SpotifyConnectDevices.GetDeviceByDiscoveryKey(str(argsGroupUuid))
                if (scDevice is None):

                    # trace.
                    _logsi.LogVerbose("Could not find SpotifyConnectDevices instance for Cast Group discovery key: \"%s\"" % (str(argsGroupUuid)), colorValue=SIColors.Lavender)

                else:

                    # trace.
                    _logsi.LogVerbose("Chromecast member device %s was removed from multizone group \"%s\"" % (scDevice.Title, self._CastDevice.cast_info.friendly_name), colorValue=SIColors.Lavender)

            except Exception as ex:
            
                # trace.
                _logsi.LogException("Unhandled exception occured while processing Chromecast MultiZoneController notification (%s)" % (apiMethodName), ex, logToSystemLogger=False)
            
                # ignore exception, as nothing can be done about it.

            finally:

                # trace.
                _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def multizone_status_received(
        self, 
        ) -> None:
        """
        Called when Multizone status has been updated.
        """
        # use lock, as multiple threads could be calling this method simultaneously.
        with self._Zeroconf_RLock:

            # copy passed parameters to thread-safe storage.
            # n/a
                
            apiMethodName:str = "multizone_status_received"
            apiMethodParms:SIMethodParmListContext = None

            try:

                # trace.
                apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
                _logsi.LogMethodParmList(SILevel.Debug, "Chromecast multizone group status has been updated", apiMethodParms, colorValue=SIColors.Lavender)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):

                    # build member list with friendly names.
                    result:list[str] = []
                    member:str = None
                    for member in self._CastMultizoneController.members:
                        scDevice:SpotifyConnectDevice = self._ParentDirectory._SpotifyConnectDevices.GetDeviceByDiscoveryKey(member)
                        if (scDevice is None):
                            result.append(member)
                        else:
                            result.append(scDevice.Title)
                    _logsi.LogArray(SILevel.Verbose, "Chromecast multizone group \"%s\" members (count=%d)" % (self._CastDevice.cast_info.friendly_name, len(result)), result, colorValue=SIColors.Lavender)

            except Exception as ex:
            
                # trace.
                _logsi.LogException("Unhandled exception occured while processing Chromecast MultiZoneController notification (%s)" % (apiMethodName), ex, logToSystemLogger=False)
            
                # ignore exception, as nothing can be done about it.

            finally:

                # trace.
                _logsi.LeaveMethod(SILevel.Debug, apiMethodName)
