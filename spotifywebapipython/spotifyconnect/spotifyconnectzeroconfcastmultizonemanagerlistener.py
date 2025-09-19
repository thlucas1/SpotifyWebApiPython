
# external package imports.
from pychromecast.controllers.media import MediaStatus
from pychromecast.controllers.multizone import MultizoneController, MultizoneManager, MultiZoneManagerListener, GroupInfo
from pychromecast.controllers.receiver import CastStatus
from pychromecast.dial import MultizoneStatus, get_multizone_status
from pychromecast import Chromecast
import pychromecast
import threading
from uuid import UUID
from zeroconf import Zeroconf

# our package imports.
from spotifywebapipython.models import SpotifyConnectDevice
# note - cannot reference `SpotifyConnectDirectoryTask` due to circular import!
# from .spotifyconnectdirectorytask import SpotifyConnectDirectoryTask

# get smartinspect logger reference; create a new session for this module name.
from smartinspectpython.siauto import SIAuto, SILevel, SISession, SIMethodParmListContext, SIColors
import logging

_logsi:SISession = SIAuto.Si.GetSession(__name__)
if (_logsi == None):
    _logsi = SIAuto.Si.AddSession(__name__, True)
_logsi.SystemLogger = logging.getLogger(__name__)


class SpotifyConnectZeroconfCastMultiZoneManagerListener(MultiZoneManagerListener):
    """
    Google Chromecast Zeroconf MultiZone Listener class.
    
    Listens for Chromecast device multi-zone status updates for devices that
    support multi-zone / group functionality.

    This class should be added as a listener to all Chromecast devices.
    """

    UNHANDLED_EXCEPTION_MSG:str = "Unhandled exception occured while processing Chromecast MultizoneManager notification (%s)"
    """
    Unhandled exception occured while processing Chromecast MultizoneManager notification (%s)
    """

    def __init__(
        self, 
        parentDirectory,
        zeroconfInstance:Zeroconf,
        zeroconf_RLock:threading.RLock,
        castMultizoneManager:MultizoneManager,
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
            castMultizoneManager (MultizoneManager)
                MultizoneManager parent instance.
            castDevice (Chromecast):
                Chromecast device object.
        """
        # invoke base class method.
        super().__init__()

        # initialize storage.
        self._CastMultizoneManager:MultizoneManager = castMultizoneManager
        self._CastDevice = castDevice
        """ Cast group device that received the multizone notification. """
        self._ParentDirectory = parentDirectory
        self._ZeroconfInstance:Zeroconf = zeroconfInstance
        self._Zeroconf_RLock:threading.RLock = zeroconf_RLock


    def added_to_multizone(
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
                
            apiMethodName:str = "added_to_multizone (MultiZoneManagerListener)"
            apiMethodParms:SIMethodParmListContext = None

            try:

                # trace.
                apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
                apiMethodParms.AppendKeyValue("group_uuid", argsGroupUuid)
                _logsi.LogMethodParmList(SILevel.Debug, "Chromecast multizone manager notification was received for group \"%s\"" % (argsGroupUuid), apiMethodParms, colorValue=SIColors.Lavender)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):

                    # get group device instance.
                    scDevice:SpotifyConnectDevice = self._ParentDirectory._SpotifyConnectDevices.GetDeviceByDiscoveryKey(str(argsGroupUuid))
                    if (scDevice is None):

                        # trace.
                        _logsi.LogVerbose("Could not find SpotifyConnectDevices instance for Cast device key: \"%s\"" % (str(argsGroupUuid)), colorValue=SIColors.Lavender)

                    else:

                        # trace.
                        _logsi.LogVerbose("Chromecast multizone manager added device \"%s\" to multizone group %s" % (self._CastDevice.cast_info.friendly_name, scDevice.Title), colorValue=SIColors.Lavender)

                        # # get the current multizone status.
                        # castMultiZoneStatus:MultizoneStatus = get_multizone_status(scDevice.DiscoveryResult.HostIpAddress, self._CastDevice.cast_info.services, self._ZeroconfInstance, 5)
                        # _logsi.LogObject(SILevel.Verbose, "Chromecast multizone manager status for group: %s [%s] (get_multizone_status)" % (scDevice.Title, scDevice.DiscoveryResult.HostIpTitle), castMultiZoneStatus, colorValue=SIColors.Lavender)

                        # # build member list with friendly names.
                        # result:list[str] = []
                        # member:GroupInfo = None
                        # for key, member in self._CastMultizoneManager._groups.items():
                        #     memberName:str = member["chromecast"].cast_info.friendly_name
                        #     result.append(memberName + ": " + str(member))
                        # _logsi.LogArray(SILevel.Verbose, "Chromecast multizone group \"%s\" groups (count=%d)" % (scDevice.Title, len(result)), result, colorValue=SIColors.Lavender)

                        # # build member list with friendly names.
                        # result:list[str] = []
                        # member:GroupInfo = None
                        # for key, member in self._CastMultizoneManager._casts.items():
                        #     group_members:str = member["group_memberships"]
                        #     if (len(group_members) > 0):
                        #         result.append(str(member))
                        # _logsi.LogArray(SILevel.Verbose, "Chromecast multizone group \"%s\" casts (count=%d)" % (scDevice.Title, len(result)), result, colorValue=SIColors.Lavender)

            except Exception as ex:
            
                # trace.
                _logsi.LogException(SpotifyConnectZeroconfCastMultiZoneManagerListener.UNHANDLED_EXCEPTION_MSG % (apiMethodName), ex, logToSystemLogger=False)
            
                # ignore exception, as nothing can be done about it.

            finally:

                # trace.
                _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def removed_from_multizone(
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
                
            apiMethodName:str = "removed_from_multizone (MultiZoneManagerListener)"
            apiMethodParms:SIMethodParmListContext = None

            try:

                # trace.
                apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
                apiMethodParms.AppendKeyValue("group_uuid", argsGroupUuid)
                _logsi.LogMethodParmList(SILevel.Debug, "Chromecast multizone manager notification was received for group \"%s\"" % (argsGroupUuid), apiMethodParms, colorValue=SIColors.Lavender)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):

                    # get group device instance.
                    scDevice:SpotifyConnectDevice = self._ParentDirectory._SpotifyConnectDevices.GetDeviceByDiscoveryKey(str(argsGroupUuid))
                    if (scDevice is None):

                        # trace.
                        _logsi.LogVerbose("Could not find SpotifyConnectDevices instance for Cast device key: \"%s\"" % (str(argsGroupUuid)), colorValue=SIColors.Lavender)

                    else:

                        # trace.
                        _logsi.LogVerbose("Chromecast multizone manager removed device \"%s\" from multizone group %s" % (self._CastDevice.cast_info.friendly_name, scDevice.Title), colorValue=SIColors.Lavender)

                        # # get the current multizone status.
                        # castMultiZoneStatus:MultizoneStatus = get_multizone_status(scDevice.DiscoveryResult.HostIpAddress, self._CastDevice.cast_info.services, self._ZeroconfInstance, 5)
                        # _logsi.LogObject(SILevel.Verbose, "Chromecast multizone manager status for group: %s [%s] (get_multizone_status)" % (scDevice.Title, scDevice.DiscoveryResult.HostIpTitle), castMultiZoneStatus, colorValue=SIColors.Lavender)

                        # # build member list with friendly names.
                        # result:list[str] = []
                        # member:GroupInfo = None
                        # for key, member in self._CastMultizoneManager._groups.items():
                        #     memberName:str = member["chromecast"].cast_info.friendly_name
                        #     result.append(memberName + ": " + str(member))
                        # _logsi.LogArray(SILevel.Verbose, "Chromecast multizone group \"%s\" groups (count=%d)" % (scDevice.Title, len(result)), result, colorValue=SIColors.Lavender)

                        # # build member list with friendly names.
                        # result:list[str] = []
                        # member:GroupInfo = None
                        # for key, member in self._CastMultizoneManager._casts.items():
                        #     group_members:str = member["group_memberships"]
                        #     if (len(group_members) > 0):
                        #         result.append(str(member))
                        # _logsi.LogArray(SILevel.Verbose, "Chromecast multizone group \"%s\" casts (count=%d)" % (scDevice.Title, len(result)), result, colorValue=SIColors.Lavender)

            except Exception as ex:
            
                # trace.
                _logsi.LogException(SpotifyConnectZeroconfCastMultiZoneManagerListener.UNHANDLED_EXCEPTION_MSG % (apiMethodName), ex, logToSystemLogger=False)

                # ignore exception, as nothing can be done about it.

            finally:

                # trace.
                _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def multizone_new_media_status(
        self, 
        group_uuid: str, 
        media_status: MediaStatus
        ) -> None:
        """
        Called when the group identified by group_uuid, of which the cast is a member, has new media status.
        """

        # Commented out this code, as we do not use it.
        # Left it in place, in case it's required in the future.
        pass

        # # use lock, as multiple threads could be calling this method simultaneously.
        # with self._Zeroconf_RLock:

        #     # copy passed parameters to thread-safe storage.
        #     argsGroupUuid:UUID = group_uuid
        #     argsMediaStatus:MediaStatus = media_status
                               
        #     apiMethodName:str = "multizone_new_media_status (MultiZoneManagerListener)"
        #     apiMethodParms:SIMethodParmListContext = None

        #     try:

        #         # trace.
        #         apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
        #         apiMethodParms.AppendKeyValue("group_uuid", argsGroupUuid)
        #         apiMethodParms.AppendKeyValue("media_status", argsMediaStatus)
        #         _logsi.LogMethodParmList(SILevel.Debug, "Chromecast multizone manager media status has been updated for group: \"%s\"" % (argsGroupUuid), apiMethodParms, colorValue=SIColors.Lavender)

        #         # example - MediaStatus:
        #         # {
        #         #     'metadata_type': 3,
        #         #     'title': 'Fire And Ice',
        #         #     'series_title': None,
        #         #     'season': None,
        #         #     'episode': None,
        #         #     'artist': 'Steve Camp',
        #         #     'album_name': 'Fire And Ice',
        #         #     'album_artist': None,
        #         #     'track': None,
        #         #     'subtitle_tracks': [],
        #         #     'images': [MediaImage(url = 'https://i.scdn.co/image/ab67 ...')],
        #         #     'content_id': 'spotify:track:4M7fCbUaDpYWNKSEZfLpSb',
        #         #     'content_type': 'application/x-spotify.track',
        #         #     ...  <==== truncated for brevity; see developer docs for more details
        #         # }

        #         # trace.
        #         if (_logsi.IsOn(SILevel.Verbose)):

        #             # get group device instance.
        #             scDevice:SpotifyConnectDevice = self._ParentDirectory._SpotifyConnectDevices.GetDeviceByDiscoveryKey(str(argsGroupUuid))
        #             if (scDevice is None):

        #                 # trace.
        #                 _logsi.LogVerbose("Could not find SpotifyConnectDevices instance for Cast device key: \"%s\"" % (str(argsGroupUuid)), colorValue=SIColors.Lavender)

        #             else:

        #                 # formulate current status.
        #                 statusText:str = "unknown"
        #                 if (argsMediaStatus):
        #                     statusText = "%s (%s)" % (argsMediaStatus.title or "null", argsMediaStatus.artist or "null")

        #                 # trace.
        #                 _logsi.LogObject(SILevel.Verbose, "Chromecast multizone manager group MediaStatus: %s [%s] - %s" % (scDevice.Title, scDevice.DiscoveryResult.HostIpTitle, statusText), argsMediaStatus, colorValue=SIColors.Lavender)

        #     except Exception as ex:
            
        #         # trace.
        #         _logsi.LogException(SpotifyConnectZeroconfCastMultiZoneManagerListener.UNHANDLED_EXCEPTION_MSG % (apiMethodName), ex, logToSystemLogger=False)
            
        #         # ignore exception, as nothing can be done about it.

        #     finally:

        #         # trace.
        #         _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def multizone_new_cast_status(
        self, 
        group_uuid: str, 
        cast_status: CastStatus
        ) -> None:
        """
        Called when the group identified by group_uuid, of which the cast is a member, has new status.
        """
        # Commented out this code, as we do not use it.
        # Left it in place, in case it's required in the future.
        #pass

        # use lock, as multiple threads could be calling this method simultaneously.
        with self._Zeroconf_RLock:

            # copy passed parameters to thread-safe storage.
            argsGroupUuid:UUID = group_uuid
            argsCastStatus:CastStatus = cast_status
                
            apiMethodName:str = "multizone_new_cast_status (MultiZoneManagerListener)"
            apiMethodParms:SIMethodParmListContext = None

            try:

                # trace.
                apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
                apiMethodParms.AppendKeyValue("group_uuid", argsGroupUuid)
                apiMethodParms.AppendKeyValue("cast_status", argsCastStatus)
                _logsi.LogMethodParmList(SILevel.Debug, "Chromecast multizone manager cast status has been updated for group: \"%s\"" % (argsGroupUuid), apiMethodParms, colorValue=SIColors.Lavender)

                # example - CastStatus:
                # {
                #     "is_active_input": "None",
                #     "is_stand_by": "None",
                #     "volume_level": "0.10000763088464737",
                #     "volume_muted": "False",
                #     "app_id": "CC32E753",
                #     "display_name": "Spotify",
                #     "namespaces": ['urn:x-cast:com.google.cast.debugoverlay',
                #         'urn:x-cast:com.google.cast.cac',
                #         'urn:x-cast:com.spotify.chromecast.secure.v1',
                #         'urn:x-cast:com.google.cast.media'
                #     ],
                #     "session_id": "690a6e31-647d-4808-97f1-cc65cf2eb473",
                #     "transport_id": "690a6e31-647d-4808-97f1-cc65cf2eb473",
                #     "status_text": "Casting: Strong Enough",
                #     "icon_url": "https://lh3.googleusercontent.com/oodettwQnQA4LTRxkeyqf93S8J6gbWu9r8DPsiVsDoiTffNV2xhiSeNnFCQ8zh5I4xGaAH_xyLzLx3E6",
                #     "volume_control_type": "master"
                # }

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):

                    # get group device instance.
                    scDevice:SpotifyConnectDevice = self._ParentDirectory._SpotifyConnectDevices.GetDeviceByDiscoveryKey(str(argsGroupUuid))
                    if (scDevice is None):

                        # trace.
                        _logsi.LogVerbose("Could not find SpotifyConnectDevices instance for Cast device key: \"%s\"" % (str(argsGroupUuid)), colorValue=SIColors.Lavender)

                    else:

                        # formulate current status.
                        statusText:str = "unknown"
                        if (argsCastStatus):
                            statusText = "%s: %s" % (argsCastStatus.display_name or "null", argsCastStatus.status_text or "null")

                        # trace.
                        _logsi.LogObject(SILevel.Verbose, "Chromecast multizone manager group CastStatus: %s [%s] - %s" % (scDevice.Title, scDevice.DiscoveryResult.HostIpTitle, statusText), argsCastStatus, colorValue=SIColors.Lavender)

            except Exception as ex:

                # trace.
                _logsi.LogException(SpotifyConnectZeroconfCastMultiZoneManagerListener.UNHANDLED_EXCEPTION_MSG % (apiMethodName), ex, logToSystemLogger=False)
            
                # ignore exception, as nothing can be done about it.

            finally:

                # trace.
                _logsi.LeaveMethod(SILevel.Debug, apiMethodName)
