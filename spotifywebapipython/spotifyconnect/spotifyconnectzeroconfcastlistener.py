# external package imports.
from pychromecast import CastInfo, HostServiceInfo
from pychromecast.discovery import AbstractCastListener
import ipaddress
import threading
from uuid import UUID

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

ZEROCONF_SERVICETYPE_GOOGLECAST:str = "_googlecast._tcp.local."
"""
Googlecast Zeroconf service type identifier (e.g. "_googlecast._tcp.local.").
"""

# chromecast types supported.
CAST_TYPE_CHROMECAST = "cast"
""" Regular chromecast, supports video/audio """
CAST_TYPE_AUDIO = "audio"
""" Cast Audio device, supports only audio """
CAST_TYPE_GROUP = "group" 
""" Cast Audio group device, supports only audio """
CAST_TYPE_NONE = None
""" cast_type not set; assume it supports audio """


class SpotifyConnectZeroconfCastListener(AbstractCastListener):
    """
    Google Chromecast Zeroconf Listener class.
    
    Listens for Chromecast device connection updates for devices that
    support Spotify Connect.
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


    def _GetZeroconfDiscoveryResult(
        self,
        uuid:UUID, 
        serviceName:str,
        castInfo_removed:CastInfo = None
        ) -> ZeroconfDiscoveryResult:
        """
        Builds a `ZeroconfDiscoveryResult` instance from Zeroconf CastInfo data
        when an add or update service state change takes place.

        Args:
            uuid (UUID):
                The cast's uuid, which is the dictionary key to find the chromecast 
                metadata in CastBrowser.devices collection.
            serviceName (str):
                First known MDNS service name or host:port.
            castInfo_removed (CastInfo):
                CastInfo for the service to aid cleanup; only supplied for removal
                requests since the CastBrowser.services collection no longer contains
                a CastInfo object for the specified uuid.
        """
        result:ZeroconfDiscoveryResult = None
        castInfoHost:str = None
        castInfoPort:int = 0

        try:

            # is this an MDNSServiceInfo service record?  we only want discovery results
            # that contain MDNSServiceInfo service information.
            if (serviceName.find(ZEROCONF_SERVICETYPE_GOOGLECAST) == -1):
                _logsi.LogDebug("Chromecast Zeroconf discovery service notification: \"%s\" (%s)" % (serviceName, "ignored; not MDNSInfo"))
                return None

            # get chromecast info.
            castInfo:CastInfo = castInfo_removed
            if (castInfo is None):

                # map the CastInfo object.
                castInfo:CastInfo = self._ParentDirectory._CastBrowser.services[uuid]
                castInfoHost = castInfo.host
                castInfoPort = castInfo.port

                # 20250628 commented out the ipv6 address resolution code.
                # the `get_multizone_status` (in directorytask) could possibly return ipv6 info, with no ipv4 data!

                # # find ipv4 host and port number.
                # # if the base CastInfo object is ipv6, then find the ipv4 HostServiceInfo
                # # service record and get it from there.
                # if ((castInfoHost + "").find(":") != -1):

                #     # cast info host information is ipv6!
                #     # find the ipv4 host service info object.
                #     _logsi.LogDebug("Chromecast Zeroconf discovery service notification contained IPV6 HostServiceInfo data: \"%s\" (%s)" % (serviceName, "searching for IPV4 info"), colorValue=SIColors.Coral)
                #     castHostIpv4:HostServiceInfo = None
                #     for castSvc in castInfo.services:
                #         if (isinstance(castSvc, HostServiceInfo)):
                #             if ((castSvc.host + "").find(":") == -1):
                #                 castInfoHost = castSvc.host
                #                 castInfoPort = castSvc.port
                #                 castHostIpv4 = castSvc
                #                 break

                #     # if ipv4 host service info not found then we are done, as Spotify Connect 
                #     # zeroconf requires an IPV4 address structure.
                #     if (castHostIpv4 is None):
                #         _logsi.LogDebug("Chromecast Zeroconf discovery service notification did not contain IPV4 HostServiceInfo service entry: \"%s\" (%s)" % (serviceName, "IPV6 HostServiceInfo may fail"), colorValue=SIColors.Coral)

            else:

                # set host and port number for remove request.
                castInfoHost = castInfo.host
                castInfoPort = castInfo.port

            # trace.
            _logsi.LogObject(SILevel.Debug, "Chromecast Zeroconf service details: \"%s\" (%s) (CastInfo object)" % (castInfo.friendly_name, serviceName), castInfo) 

            # only certain cast_type values support Spotify Connect.
            castType:str = castInfo.cast_type
            if (not (castType in [CAST_TYPE_AUDIO, CAST_TYPE_GROUP, CAST_TYPE_CHROMECAST, CAST_TYPE_NONE])):
                _logsi.LogDebug("Chromecast device cast_type of \"%s\" is not supported; ignoring: \"%s\" (%s)" % (castType, castInfo.friendly_name, serviceName), colorValue=SIColors.Coral)
                return None

            # ensure IPV4 connection - ignore if IPV6.
            # Windows OS does not support dual-stack socket handling IPv4 (224.0.0.251) and IPv6 (ff02::fb).
            ip = ipaddress.ip_address(castInfo.host)
            if (ip.version == 6):
                _logsi.LogDebug("Chromecast IPV6 device addresses are not supported; device could cause problems: \"%s\" (%s)" % (castInfo.friendly_name, serviceName), colorValue=SIColors.Red)

                # will still allow this for now, but we might want to ignore IPV6 devices
                # in the future!  To do so, just uncomment the following, which will 
                # ignore the device.
                #return None
            
            # create new discovery result instance.
            result:ZeroconfDiscoveryResult = ZeroconfDiscoveryResult()
            result.DeviceName = castInfo.friendly_name
            result.Domain = ".local"
            result.HostIpAddresses = [castInfoHost]
            result.HostIpPort = castInfoPort
            result.HostTTL = 120
            result.IsChromeCast = True
            result.Key = str(uuid)
            result.Name = serviceName
            result.Priority = 0
            result.OtherTTL = 4500
            result.Server = serviceName
            result.ServerKey = serviceName
            result.ServiceType = ZEROCONF_SERVICETYPE_GOOGLECAST
            result.Weight = 0
            result.Properties.append(ZeroconfProperty("CPath", "/na"))
            result.Properties.append(ZeroconfProperty("VERSION", "1.0"))
            result.Properties.append(ZeroconfProperty("cast_type", castType))
            result.SpotifyConnectCPath = "/na"
            result.SpotifyConnectVersion = "1.0"
            result.Id = "\"%s\" (%s:%s)" % (result.DeviceName, result.HostIpAddress, result.HostIpPort)

            # trace.
            _logsi.LogObject(SILevel.Debug, "Chromecast Zeroconf Discovery Result: %s (object)" % (result.Id), result, excludeNonPublic=True)                        

            # return discovery result.
            return result

        except Exception as ex:
            
            # trace.
            _logsi.LogException("Could not load ZeroconfDiscoveryResult instance from Chromecast Zeroconf service details", ex, logToSystemLogger=False)
            
            # ignore exception
            return None
            

    def add_cast(
        self, 
        uuid:UUID, 
        serviceName:str
        ) -> None:
        """
        Called when a new cast has been discovered.

        Args:
            uuid (UUID):
                The cast's uuid, which is the dictionary key to find the chromecast 
                metadata in CastBrowser.devices collection.
            serviceName (str):
                First known MDNS service name or host:port.
        """
        # use lock, as multiple threads could be calling this method simultaneously.
        with self._Zeroconf_RLock:

            # copy passed parameters to thread-safe storage.
            argsUuid:UUID = uuid
            argsServiceName:str = serviceName
                
            apiMethodName:str = "add_cast"
            apiMethodParms:SIMethodParmListContext = None

            try:

                # trace.
                apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
                apiMethodParms.AppendKeyValue("uuid", argsUuid)
                apiMethodParms.AppendKeyValue("serviceName", argsServiceName)
                _logsi.LogMethodParmList(SILevel.Debug, "Chromecast Zeroconf discovery service notification: \"%s\" (%s)" % (argsServiceName, apiMethodName), apiMethodParms)

                # build discovery result instance from service state information.
                # if nothing returned, then don't bother!
                result:ZeroconfDiscoveryResult = self._GetZeroconfDiscoveryResult(argsUuid, argsServiceName, None)
                if (result is None):
                    return

                # let the parent handle the event.
                self._ParentDirectory.OnServiceInfoAddedUpdatedChromecast(result, argsUuid, argsServiceName, apiMethodName)

            except Exception as ex:
            
                # trace.
                _logsi.LogException("Unhandled exception occured while processing Chromecast Zeroconf service browser ServiceStateChange notification (%s)" % (apiMethodName), ex, logToSystemLogger=False)
            
                # ignore exception, as nothing can be done about it.

            finally:

                # trace.
                _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def remove_cast(
        self, 
        uuid:UUID, 
        serviceName:str, 
        castInfo:CastInfo
        ) -> None:
        """
        Called when a cast has been lost (MDNS info expired or host down).

        Args:
            uuid (UUID):
                The cast's uuid, which is the dictionary key to find the chromecast 
                metadata in CastBrowser.devices collection.
            serviceName (str):
                Last valid MDNS service name or host:port.
            castInfo (CastInfo):
                CastInfo for the service to aid cleanup.
        """
        # use lock, as multiple threads could be calling this method simultaneously.
        with self._Zeroconf_RLock:
                
            # copy passed parameters to thread-safe storage.
            argsUuid:UUID = uuid
            argsServiceName:str = serviceName
            argsCastInfo:CastInfo = castInfo
                
            apiMethodName:str = "remove_cast"
            apiMethodParms:SIMethodParmListContext = None

            try:

                # trace.
                apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
                apiMethodParms.AppendKeyValue("uuid", argsUuid)
                apiMethodParms.AppendKeyValue("serviceName", argsServiceName)
                _logsi.LogMethodParmList(SILevel.Debug, "Chromecast Zeroconf discovery service notification: \"%s\" (%s)" % (argsServiceName, apiMethodName), apiMethodParms)

                # for service removal notifications, there will be no zeroconf service info.
                # build discovery result instance from service state information.
                # if nothing returned, then it's ok - build a minimal discovery instance that
                # will contain the necessary details to remove the device entry.
                result:ZeroconfDiscoveryResult = self._GetZeroconfDiscoveryResult(argsUuid, argsServiceName, argsCastInfo)
                if (result is None):
                    result = ZeroconfDiscoveryResult()
                    result.DeviceName = castInfo.friendly_name
                    result.Key = str(uuid)
                    result.Name = serviceName
                    result.ServiceType = ZEROCONF_SERVICETYPE_GOOGLECAST

                # let the parent handle the event.
                self._ParentDirectory.OnServiceInfoRemovedChromecast(result, argsUuid, argsServiceName, argsCastInfo)

            except Exception as ex:
            
                # trace.
                _logsi.LogException("Unhandled exception occured while processing Chromecast Zeroconf service browser ServiceStateChange notification (%s)" % (apiMethodName), ex, logToSystemLogger=False)
            
                # ignore exception, as nothing can be done about it.

            finally:

                # trace.
                _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def update_cast(
        self, 
        uuid:UUID, 
        serviceName:str
        ) -> None:
        """
        Called when a cast has been updated (MDNS info renewed or changed).

        Args:
            uuid (UUID):
                The cast's uuid, which is the dictionary key to find the chromecast 
                metadata in CastBrowser.devices collection.
            serviceName (str):
                MDNS service name or host:port.
        """
        # use lock, as multiple threads could be calling this method simultaneously.
        with self._Zeroconf_RLock:
                
            # copy passed parameters to thread-safe storage.
            argsUuid:UUID = uuid
            argsServiceName:str = serviceName
                
            apiMethodName:str = "update_cast"
            apiMethodParms:SIMethodParmListContext = None

            try:

                # trace.
                apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
                apiMethodParms.AppendKeyValue("uuid", argsUuid)
                apiMethodParms.AppendKeyValue("serviceName", argsServiceName)
                _logsi.LogMethodParmList(SILevel.Debug, "Chromecast Zeroconf discovery service notification: \"%s\" (%s)" % (serviceName, apiMethodName), apiMethodParms)

                # build discovery result instance from service state information.
                # if nothing returned, then don't bother!
                result:ZeroconfDiscoveryResult = self._GetZeroconfDiscoveryResult(argsUuid, argsServiceName, None)
                if (result is None):
                    return

                # let the parent handle the event.
                self._ParentDirectory.OnServiceInfoAddedUpdatedChromecast(result, argsUuid, argsServiceName, apiMethodName)

            except Exception as ex:
            
                # trace.
                _logsi.LogException("Unhandled exception occured while processing Chromecast Zeroconf service browser ServiceStateChange notification (%s)" % (apiMethodName), ex, logToSystemLogger=False)
            
                # ignore exception, as nothing can be done about it.

            finally:

                # trace.
                _logsi.LeaveMethod(SILevel.Debug, apiMethodName)
