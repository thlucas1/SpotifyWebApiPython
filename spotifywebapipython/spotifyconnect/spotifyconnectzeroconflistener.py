# external package imports.
import threading
from zeroconf import Zeroconf, ServiceInfo, ServiceStateChange, IPVersion

# our package imports.
from spotifywebapipython.models import ZeroconfProperty, ZeroconfDiscoveryResult
# note - cannot reference `SpotifyConnectDirectoryTask` due to circular import!
# from .SpotifyConnectDirectoryTask import SpotifyConnectDirectoryTask

# get smartinspect logger reference; create a new session for this module name.
from smartinspectpython.siauto import SIAuto, SILevel, SISession, SIMethodParmListContext
import logging

_logsi:SISession = SIAuto.Si.GetSession(__name__)
if (_logsi == None):
    _logsi = SIAuto.Si.AddSession(__name__, True)
_logsi.SystemLogger = logging.getLogger(__name__)

ZEROCONF_SERVICETYPE_SPOTIFYCONNECT:str = "_spotify-connect._tcp.local."
"""
Spotify Connect Zeroconf service type identifier.
"""


class SpotifyConnectZeroconfListener:
    """
    Spotify Connect Zeroconf Listener class.
    
    Listens for Chromecast device connection updates for devices that
    support Spotify Connect.
    """

    # this class can be tested by issuing the following commands from an MS-DOS
    # command prompt to simulate Zeroconf registration updates.

    # - add a new Spotify Connect instance registration:
    # > dns-sd -R "MyTestSC1" _spotify-connect._tcp. local 8080 cpath=/zcXXX version=1.0
    
    # - update a new Spotify Connect instance registration; 
    # - if you change the name, service type, or port number, a NEW registration is created!
    # - for updates, the only thing you can really update is the TXT record properties.
    # > dns-sd -R "MyTestSC1" _spotify-connect._tcp. local 8080 cpath=/zcYYY version=1.0
    
    # - remove an existing Spotify Connect instance registration; 
    # > the only way to remove an entry is to kill the process the entry was created under!


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
        zeroconf:Zeroconf, 
        serviceType:str, 
        serviceName:str, 
        serviceStateChange:ServiceStateChange
        ) -> ZeroconfDiscoveryResult:
        """
        Builds a `ZeroconfDiscoveryResult` instance from Zeroconf Service Information data
        when an add or update service state change takes place.

        Args:
            zeroconf (Zeroconf):
                Zeroconf instance that raised the notification.
            serviceType (str):
                Service type that was affected.
            serviceName (str):
                Service name that was affected.
            serviceStateChange (ServiceStateChange):
                A description of the type of service state change (add, remove, update).
        """
        result:ZeroconfDiscoveryResult = None

        try:

            # get service information instance; if none, then we are done.
            deviceName:str = (serviceName.split(".")[0])
            serviceInfo:ServiceInfo = zeroconf.get_service_info(serviceType, serviceName)
            if serviceInfo is None:
                # serviceinfo will be missing if it's a removal, so don't log the "ignored" message in this case.
                if (serviceStateChange != ServiceStateChange.Removed):
                    _logsi.LogDebug("Spotify Connect Zeroconf discovery service notification ignored: \"%s\" (%s:%s) - no serviceinfo data" % (serviceName, serviceType, serviceStateChange))
                return result

            # get list of displayable (parsed) ipv4 addresses; if none, then we are done.
            ipAddressList = serviceInfo.parsed_addresses(IPVersion.V4Only)
            if (ipAddressList is None):
                _logsi.LogDebug("Spotify Connect Zeroconf discovery service notification ignored: \"%s\" (%s:%s) - no IP address list" % (serviceName, serviceInfo.name, serviceStateChange))
                return result
            
            # trace.
            _logsi.LogObject(SILevel.Debug, "Spotify Connect Zeroconf service details: \"%s\" (%s) (serviceinfo object)" % (deviceName, serviceInfo.name), serviceInfo) 
            
            # create new discovery result instance.
            result:ZeroconfDiscoveryResult = ZeroconfDiscoveryResult()
            result.DeviceName = deviceName
            result.Domain = '.local'
            for item in ipAddressList:
                result.HostIpAddresses.append(item)
            result.HostIpPort = serviceInfo.port
            result.HostTTL = serviceInfo.host_ttl
            result.Key = serviceInfo.key
            result.Name = serviceInfo.name
            result.OtherTTL = serviceInfo.other_ttl
            result.Priority = serviceInfo.priority
            result.Server = serviceInfo.server
            result.ServerKey = serviceInfo.server_key
            #result.ServiceInfo = serviceInfo
            result.ServiceType = serviceType
            result.Weight = serviceInfo.weight
            result.Id = "\"%s\" (%s:%s)" % (result.DeviceName, result.HostIpAddress, result.HostIpPort)

            # process service info propertys.
            # note that the property keys and values must first be decoded to utf-8 encoding.
            if serviceInfo.properties is not None:
                dspProperties:dict = {}
                for key, value in serviceInfo.properties.items():
                    keyStr = key.decode('utf-8') or ""
                    valueStr = value.decode('utf-8') or ""
                    result.Properties.append(ZeroconfProperty(keyStr, valueStr)) 
                    dspProperties[keyStr] = valueStr
                    # check for Spotify Connect common properties.
                    if keyStr.lower() == 'cpath':
                        result.SpotifyConnectCPath = valueStr
                    elif keyStr.lower() == 'version':
                        result.SpotifyConnectVersion = valueStr
                _logsi.LogDictionary(SILevel.Debug, "Spotify Connect Zeroconf service details: \"%s\" (%s) (serviceinfo properties)" % (deviceName, serviceInfo.name), dspProperties) 

            # trace.
            _logsi.LogObject(SILevel.Debug, "Spotify Connect Zeroconf Discovery Result: %s (object)" % (result.Id), result, excludeNonPublic=True)                        

            # return discovery result.
            return result

        except Exception as ex:
            
            # trace.
            _logsi.LogException("Could not load ZeroconfDiscoveryResult instance from Zeroconf serviceinfo object.", ex, logToSystemLogger=False)
            
            # ignore exception
            return None
            

    def OnServiceStateChange(
        self,
        zeroconf:Zeroconf, 
        service_type:str, 
        name:str, 
        state_change:ServiceStateChange
        ) -> None:
        """
        Called by the spotify connect zeroconf ServiceBrowser when an mDNS service
        state has changed (e.g. added, removed, or updated).

        Args:
            zeroconf (Zeroconf):
                Zeroconf instance that raised the notification.
            service_type (str):
                Service type that was affected.
            name (str):
                Service name that was affected.
            state_change (ServiceStateChange):
                The type of service state change (add, remove, update).
        """
        # use lock, as multiple threads could be calling this method simultaneously.
        with self._Zeroconf_RLock:

            # copy passed parameters to thread-safe storage.
            serviceType:str = service_type
            serviceName:str = name
            serviceStateChange:ServiceStateChange = state_change

            apiMethodName:str = "OnServiceStateChange"
            apiMethodParms:SIMethodParmListContext = None
            
            try: 

                # trace.
                apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
                apiMethodParms.AppendKeyValue("serviceType", serviceType)
                apiMethodParms.AppendKeyValue("serviceName", serviceName)
                apiMethodParms.AppendKeyValue("serviceStateChange", serviceStateChange)
                _logsi.LogMethodParmList(SILevel.Verbose, "Spotify Connect Zeroconf discovery service notification: \"%s\" (%s)" % (serviceName, str(serviceStateChange)), apiMethodParms)

                # call method based on serviceStateChange argument value.
                if (serviceStateChange == ServiceStateChange.Added):
                    self.add_service(zeroconf, serviceType, serviceName, serviceStateChange)
                    return

                if (serviceStateChange == ServiceStateChange.Removed):
                    self.remove_service(zeroconf, serviceType, serviceName, serviceStateChange)
                    return

                if (serviceStateChange == ServiceStateChange.Updated):
                    self.update_service(zeroconf, serviceType, serviceName, serviceStateChange)
                    return
            
            except Exception as ex:
            
                # trace.
                _logsi.LogException("Unhandled exception occured while processing Spotify Connect Zeroconf discovery browser ServiceStateChange notification (%s)" % (serviceStateChange), ex, logToSystemLogger=False)
            
                # ignore exception, as nothing can be done about it.

            finally:

                # trace.
                _logsi.LeaveMethod(SILevel.Debug, apiMethodName)

        
    def add_service(
        self,
        zeroconf:Zeroconf, 
        serviceType:str, 
        serviceName:str, 
        serviceStateChange:ServiceStateChange
        ) -> None:
        """
        Called when an mDNS service is discovered.

        Args:
            zeroconf (Zeroconf):
                Zeroconf instance that raised the notification.
            serviceType (str):
                Service type that was affected.
            serviceName (str):
                Service name that was affected.
            serviceStateChange (ServiceStateChange):
                A description of the type of service state change (add, remove, update).

        This method will be called in a thread-safe manner, as the caller is using
        the `Zeroconf_RLock` object to control access.
        """
        # build discovery result instance from service state information.
        # if nothing returned, then don't bother!
        result:ZeroconfDiscoveryResult = self._GetZeroconfDiscoveryResult(zeroconf, serviceType, serviceName, serviceStateChange)
        if (result is None):
            return

        # let the parent handle the event.
        self._ParentDirectory.OnServiceInfoAddedUpdatedSpotifyConnect(result)
        return
    

    def remove_service(
        self,
        zeroconf:Zeroconf, 
        serviceType:str, 
        serviceName:str, 
        serviceStateChange:ServiceStateChange
        ) -> None:
        """
        Called when an mDNS service is lost.

        Args:
            zeroconf (Zeroconf):
                Zeroconf instance that raised the notification.
            serviceType (str):
                Service type that was affected.
            serviceName (str):
                Service name that was affected.
            serviceStateChange (ServiceStateChange):
                A description of the type of service state change (add, remove, update).

        This method will be called in a thread-safe manner, as the caller is using
        the `Zeroconf_RLock` object to control access.
        """
        # for service removal notifications, there will be no zeroconf service info.
        # build discovery result instance from service state information.
        # if nothing returned, then it's ok - build a minimal discovery instance that
        # will contain the necessary details to remove the device entry.
        result:ZeroconfDiscoveryResult = self._GetZeroconfDiscoveryResult(zeroconf, serviceType, serviceName, serviceStateChange)
        if (result is None):
            result = ZeroconfDiscoveryResult()
            result.DeviceName = (serviceName.split(".")[0])
            result.Key = serviceName.lower()
            result.Name = serviceName
            result.ServiceType = serviceType

        # let the parent handle the event.
        self._ParentDirectory.OnServiceInfoRemovedSpotifyConnect(result)
        return


    def update_service(
        self,
        zeroconf:Zeroconf, 
        serviceType:str, 
        serviceName:str, 
        serviceStateChange:ServiceStateChange
        ) -> None:
        """
        Called when an mDNS service is updated.

        Args:
            zeroconf (Zeroconf):
                Zeroconf instance that raised the notification.
            serviceType (str):
                Service type that was affected.
            serviceName (str):
                Service name that was affected.
            serviceStateChange (ServiceStateChange):
                A description of the type of service state change (add, remove, update).

        This method will be called in a thread-safe manner, as the caller is using
        the `Zeroconf_RLock` object to control access.
        """
        # build discovery result instance from service state information.
        # if nothing returned, then don't bother!
        result:ZeroconfDiscoveryResult = self._GetZeroconfDiscoveryResult(zeroconf, serviceType, serviceName, serviceStateChange)
        if (result is None):
            return

        # let the parent handle the event.
        self._ParentDirectory.OnServiceInfoAddedUpdatedSpotifyConnect(result)
        return
