# external package imports.
#from pychromecast.dial import DeviceStatus, MultizoneStatus, get_multizone_status, get_device_info
from pychromecast.controllers.multizone import MultiZoneManagerListener
import pychromecast
import threading
from uuid import UUID
import time
import zeroconf

# our package imports.
from spotifywebapipython.models import ZeroconfProperty, ZeroconfDiscoveryResult
# note - cannot reference `SpotifyConnectDirectoryTask` due to circular import!
# from .spotifyconnectdirectorytask import SpotifyConnectDirectoryTask

# get smartinspect logger reference; create a new session for this module name.
from smartinspectpython.siauto import SIAuto, SILevel, SISession, SIMethodParmListContext, SIColors
import logging

_logsi:SISession = SIAuto.Si.GetSession(__name__)
if (_logsi == None):
    _logsi = SIAuto.Si.AddSession(__name__, True)
_logsi.SystemLogger = logging.getLogger(__name__)


class SpotifyConnectZeroconfCastMultiZoneListener(MultiZoneManagerListener):
    """
    Google Chromecast Zeroconf MultiZone Listener class.
    
    Listens for Chromecast device multi-zone status updates for devices that
    support multi-zone / group functionality.
    """

    def __init__(
        self, 
        parentDirectory,
        zeroconf_RLock:threading.RLock,
        ) -> None:
        """
        Initializes a new instance of the class.

        Args:
            parentDirectory (SpotifyConnectDirectoryTask):
                Parent SpotifyConnectDirectoryTask instance.
            zeroconf_RLock (threading.RLock):
                Lock object used to enforce thread-safe updates.
        """
        # invoke base class method.
        super().__init__()

        # initialize storage.
        self._ParentDirectory = parentDirectory
        self._Zeroconf_RLock:threading.RLock = zeroconf_RLock


    def added_to_multizone(self, group_uuid):
        """Called when the cast device has been added to an audio group."""
        _logsi.LogVerbose("Multi-zone group added: \"%s\"" % (str(group_uuid)), colorValue=SIColors.LightCoral)

    def removed_from_multizone(self, group_uuid):
        """Called when the cast device has been removed from an audio group."""
        _logsi.LogVerbose("Multi-zone group removed: \"%s\"" % (str(group_uuid)), colorValue=SIColors.LightCoral)

    def multizone_new_media_status(self, group_uuid, media_status):
        """Called when the media status of the group changes."""
        _logsi.LogDictionary(SILevel.Verbose, "Multi-zone group \"%s\" new media status" % (str(group_uuid)), media_status, prettyPrint=True, colorValue=SIColors.LightCoral)

    def multizone_new_cast_status(self, group_uuid, cast_status):
        """Called when the cast status of the group changes."""
        _logsi.LogDictionary(SILevel.Verbose, "Multi-zone group \"%s\" new cast status" % (str(group_uuid)), cast_status, prettyPrint=True, colorValue=SIColors.Silver)
