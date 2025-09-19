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


class SpotifyConnectZeroconfCastMultiZoneControllerListener(MultiZoneControllerListener):
    """
    Google Chromecast Zeroconf MultiZone Listener class.
    
    Listens for Chromecast device multi-zone status updates for devices that
    support multi-zone / group functionality.

    This class should only be added as a listener to Chromecast group devices.
    """

    UNHANDLED_EXCEPTION_MSG:str = "Unhandled exception occured while processing Chromecast MultiZoneController notification (%s)"
    """
    Unhandled exception occured while processing Chromecast MultiZoneController notification (%s)
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
        """ Cast group device that received the multizone notification. """
        self._ParentDirectory = parentDirectory
        self._ZeroconfInstance:Zeroconf = zeroconfInstance
        self._Zeroconf_RLock:threading.RLock = zeroconf_RLock


    def multizone_member_added(
        self, 
        member_uuid:str, 
        ) -> None:
        """
        Called when cast device identified by `member_uuid` has been added to a group.
        """
        # use lock, as multiple threads could be calling this method simultaneously.
        with self._Zeroconf_RLock:

            # copy passed parameters to thread-safe storage.
            argsMemberUuid:UUID = member_uuid
                
            apiMethodName:str = "multizone_member_added (MultiZoneControllerListener)"
            apiMethodParms:SIMethodParmListContext = None

            try:

                # trace.
                apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
                apiMethodParms.AppendKeyValue("member_uuid", argsMemberUuid)
                _logsi.LogMethodParmList(SILevel.Debug, "Chromecast multizone controller notification was received for Cast device key \"%s\"" % (argsMemberUuid), apiMethodParms, colorValue=SIColors.Lavender)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):

                    # get device instance.
                    scDevice:SpotifyConnectDevice = self._ParentDirectory._SpotifyConnectDevices.GetDeviceByDiscoveryKey(str(argsMemberUuid))
                    if (scDevice is None):

                        # trace.
                        _logsi.LogVerbose("Could not find SpotifyConnectDevices instance for Cast device key: \"%s\"" % (str(argsMemberUuid)), colorValue=SIColors.Lavender)

                    else:

                        _logsi.LogVerbose("Chromecast multizone controller for group \"%s\" added member device: %s" % (self._CastDevice.cast_info.friendly_name, scDevice.Title), colorValue=SIColors.Lavender)

                        # get multizone controller reference for the group device, so we can get it's members.
                        castMultizoneController:MultizoneController = self._ParentDirectory._CastMultiZoneControllers.get(str(self._CastDevice.uuid), None)
                        if (castMultizoneController is not None):
                            membersSummary:list[str] = []
                            for member in castMultizoneController.members:
                                scMemberDevice:SpotifyConnectDevice = self._ParentDirectory._SpotifyConnectDevices.GetDeviceByDiscoveryKey(member)
                                if (scMemberDevice is None):
                                    membersSummary.append(str(member))
                                else:
                                    membersSummary.append("%s [ip=%s]" % (scMemberDevice.Title, scMemberDevice.DiscoveryResult.HostIpTitle))
                            _logsi.LogArray(SILevel.Verbose, "Chromecast multizone controller members for group: \"%s\" (count=%d)" % (self._CastDevice.cast_info.friendly_name, len(membersSummary)), membersSummary, colorValue=SIColors.Lavender)

            except Exception as ex:
            
                # trace.
                _logsi.LogException(SpotifyConnectZeroconfCastMultiZoneControllerListener.UNHANDLED_EXCEPTION_MSG % (apiMethodName), ex, logToSystemLogger=False)
            
                # ignore exception, as nothing can be done about it.

            finally:

                # trace.
                _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def multizone_member_removed(
        self, 
        member_uuid, 
        ) -> None:
        """
        Called when cast device identified by `member_uuid` has been removed from a group.
        """
        # use lock, as multiple threads could be calling this method simultaneously.
        with self._Zeroconf_RLock:

            # copy passed parameters to thread-safe storage.
            argsMemberUuid:UUID = member_uuid
                
            apiMethodName:str = "multizone_member_removed (MultiZoneControllerListener)"
            apiMethodParms:SIMethodParmListContext = None

            try:

                # trace.
                apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
                apiMethodParms.AppendKeyValue("member_uuid", argsMemberUuid)
                _logsi.LogMethodParmList(SILevel.Debug, "Chromecast multizone controller notification was received for Cast device key \"%s\"" % (argsMemberUuid), apiMethodParms, colorValue=SIColors.Lavender)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):

                    # get device instance.
                    scDevice:SpotifyConnectDevice = self._ParentDirectory._SpotifyConnectDevices.GetDeviceByDiscoveryKey(str(argsMemberUuid))
                    if (scDevice is None):

                        # trace.
                        _logsi.LogVerbose("Could not find SpotifyConnectDevices instance for Cast device key: \"%s\"" % (str(argsMemberUuid)), colorValue=SIColors.Lavender)

                    else:

                        _logsi.LogVerbose("Chromecast multizone controller for group \"%s\" removed member device: %s" % (self._CastDevice.cast_info.friendly_name, scDevice.Title), colorValue=SIColors.Lavender)

                        # get multizone controller reference for the group device, so we can get it's members.
                        castMultizoneController:MultizoneController = self._ParentDirectory._CastMultiZoneControllers.get(str(self._CastDevice.uuid), None)
                        if (castMultizoneController is not None):
                            membersSummary:list[str] = []
                            for member in castMultizoneController.members:
                                scMemberDevice:SpotifyConnectDevice = self._ParentDirectory._SpotifyConnectDevices.GetDeviceByDiscoveryKey(member)
                                if (scMemberDevice is None):
                                    membersSummary.append(str(member))
                                else:
                                    membersSummary.append("%s [ip=%s]" % (scMemberDevice.Title, scMemberDevice.DiscoveryResult.HostIpTitle))
                            _logsi.LogArray(SILevel.Verbose, "Chromecast multizone controller members for group: \"%s\" (count=%d)" % (self._CastDevice.cast_info.friendly_name, len(membersSummary)), membersSummary, colorValue=SIColors.Lavender)

            except Exception as ex:
            
                # trace.
                _logsi.LogException(SpotifyConnectZeroconfCastMultiZoneControllerListener.UNHANDLED_EXCEPTION_MSG % (apiMethodName), ex, logToSystemLogger=False)
            
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
                
            apiMethodName:str = "multizone_status_received (MultiZoneControllerListener)"
            apiMethodParms:SIMethodParmListContext = None

            try:

                # trace.
                apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
                _logsi.LogMethodParmList(SILevel.Debug, "Chromecast multizone controller status has been updated for group: \"%s\"" % (self._CastDevice.cast_info.friendly_name), apiMethodParms, colorValue=SIColors.Lavender)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):

                    # trace.
                    _logsi.LogObject(SILevel.Verbose, "Chromecast multizone controller group status: \"%s\"" % (self._CastDevice.cast_info.friendly_name), self._CastDevice.status, colorValue=SIColors.Lavender)

                    # build member list with friendly names.
                    membersSummary:list[str] = []
                    member:str = None
                    for member in self._CastMultizoneController.members:
                        scMemberDevice:SpotifyConnectDevice = self._ParentDirectory._SpotifyConnectDevices.GetDeviceByDiscoveryKey(member)
                        if (scMemberDevice is None):
                            membersSummary.append(str(member))
                        else:
                            membersSummary.append("%s [ip=%s]" % (scMemberDevice.Title, scMemberDevice.DiscoveryResult.HostIpTitle))
                    _logsi.LogArray(SILevel.Verbose, "Chromecast multizone controller group members: \"%s\" (count=%d)" % (self._CastDevice.cast_info.friendly_name, len(membersSummary)), membersSummary, colorValue=SIColors.Lavender)

            except Exception as ex:
            
                # trace.
                _logsi.LogException(SpotifyConnectZeroconfCastMultiZoneControllerListener.UNHANDLED_EXCEPTION_MSG % (apiMethodName), ex, logToSystemLogger=False)
            
                # ignore exception, as nothing can be done about it.

            finally:

                # trace.
                _logsi.LeaveMethod(SILevel.Debug, apiMethodName)
