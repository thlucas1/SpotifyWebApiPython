# external package imports.
try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty
import time
from zeroconf import Zeroconf, ServiceBrowser, ServiceInfo, ServiceStateChange, IPVersion

# our package imports.
from .saappmessages import SAAppMessages
from .spotifyapierror import SpotifyApiError
from .sautils import export
from .models.device import Device
from .models import ZeroconfDiscoveryResult, ZeroconfProperty

# get smartinspect logger reference; create a new session for this module name.
from smartinspectpython.siauto import SIAuto, SILevel, SISession
import logging
_logsi:SISession = SIAuto.Si.GetSession(__name__)
if (_logsi == None):
    _logsi = SIAuto.Si.AddSession(__name__, True)
_logsi.SystemLogger = logging.getLogger(__name__)


@export
class SpotifyDiscovery:
    """
    This class contains methods used to dicover Spotify Connect devices on a local
    network.  The ZeroConf (aka MDNS, etc) service is used to detect devices,
    and adds them to a device list as they are discovered.

    Click the **Sample Code** links in the individual methods for sample code examples.
    """

    def __init__(
            self, 
            zeroconfClient:Zeroconf=None,
            printToConsole:bool=False
            ) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            zeroconfClient (Zeroconf)
                A Zeroconf client instance that will be used to discover Spotify Connect devices,
                or null to create a new instance of Zeroconf.
                Default is null.
            printToConsole (bool):
                True to print discovered device information to the console as the devices
                are discovered; otherwise, False to not print anything to the console.
                Default is False.
        """
        # validations.
        if zeroconfClient is not None and (not isinstance(zeroconfClient, Zeroconf)):
            raise SpotifyApiError(SAAppMessages.ARGUMENT_TYPE_ERROR % ("__init__", 'zeroconfClient', 'Zeroconf', type(zeroconfClient).__name__), logsi=_logsi)

        # create the zeroconf client if one was not specified.
        if zeroconfClient is None:
            _logsi.LogVerbose("Creating new Zeroconf instance for discovery")
            zeroconfClient = Zeroconf()
        else:
            _logsi.LogObject(SILevel.Verbose, "Using existing Zeroconf instance for discovery", zeroconfClient)

        # initialize instance properties.
        self._DiscoveredDeviceNames:dict = {}
        self._DiscoveryResults:list[ZeroconfDiscoveryResult] = []
        self._PrintToConsole:bool = printToConsole
        self._ZeroconfClient = zeroconfClient


    def __getitem__(self, key):
        if repr(key) in self._DiscoveredDeviceNames:
            return self._DiscoveredDeviceNames[repr(key)]


    def __iter__(self):
        return iter(self._DiscoveredDeviceNames)


    def __len__(self) -> int:
        return len(self._DiscoveredDeviceNames)


    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def DiscoveredDeviceNames(self) -> dict:
        """
        A dictionary of discovered device names that were detected by the discovery process.
        
        Dictionary keys will be in the form of "'name' (address:port)", where "name" is the
        device name, "address" is the device server address and the "port" is the ipv4 port 
        number the Spotify Connect device is listening on.
        
        Dictionary values will be the device names (e.g. "Web Player (Chrome)", etc.).  This SHOULD
        match the name of the device as displayed in the Spotify App, but is not guaranteed.
        """
        return self._DiscoveredDeviceNames


    @property
    def DiscoveryResults(self) -> list[ZeroconfDiscoveryResult]:
        """
        An array of `ZeroconfDiscoveryResult` items that contain discovery details for
        each service that was discovered.
        """
        return self._DiscoveryResults


    @property
    def ZeroconfClient(self) -> Zeroconf:
        """ 
        Zeroconf client instance that will be used to discover Spotify Connect devices.
        """
        return self._ZeroconfClient
    

    def _OnServiceStateChange(self,
                              zeroconf:Zeroconf, 
                              service_type:str, 
                              name:str, 
                              state_change:ServiceStateChange
                              ) -> None:
        """
        Called by the zeroconf ServiceBrowser when a service state has changed (e.g. added,
        removed, or updated).  In our case, we only care about devices that were added.
        
        IMPORTANT - This method is executed on a different thread, so be careful about 
        multi-threaded operations!
        """
        serviceType:str = service_type
        serviceName:str = name
        serviceStateChange:ServiceStateChange = state_change
        
        # process by the state change value.
        if (serviceStateChange is ServiceStateChange.Added):
            _logsi.LogVerbose("Discovered Spotify Connect device service: '%s' (%s:%s)" % (serviceName, serviceType, serviceStateChange))
            
            deviceName:str = (serviceName.split(".")[0])
            serviceInfo:ServiceInfo = zeroconf.get_service_info(service_type, serviceName)
            if serviceInfo is None:
                return
            
            # get list of displayable (parsed) ipv4 addresses that were detected; if none, then we are done.
            ipAddressList = serviceInfo.parsed_addresses(IPVersion.V4Only)
            if (ipAddressList is None):
                return
            
            # create new result instance.
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
            result.ServiceInfo = serviceInfo
            result.ServiceType = serviceType
            result.Weight = serviceInfo.weight
                
            # formulate a unique key for this device.
            deviceKey:str = "'%s' (%s:%i)" % (deviceName, result.HostIpAddress, result.HostIpPort)
            _logsi.LogVerbose("Discovered Spotify Connect device: %s %s" % (deviceKey, result.HostIpAddresses))
            if (self._PrintToConsole == True):
                print("Discovered Spotify Connect device: %s [%s]" % (deviceKey, result.HostIpAddresses))
            _logsi.LogObject(SILevel.Verbose, "Discovered Spotify Connect device ServiceInfo: %s" % (deviceKey), serviceInfo) 
                
            # process service info propertys.
            # note that the property keys and values must first be decoded to utf-8 encoding.
            if serviceInfo.properties is not None:
                dspProperties:dict = {}
                for key, value in serviceInfo.properties.items():
                    keyStr = key.decode('utf-8')
                    valueStr = value.decode('utf-8')
                    result.Properties.append(ZeroconfProperty(keyStr, valueStr)) 
                    dspProperties[keyStr] = valueStr
                    # check for Spotify Connect common properties.
                    if keyStr.lower() == 'cpath':
                        result.SpotifyConnectCPath = valueStr
                    elif keyStr.lower() == 'version':
                        result.SpotifyConnectVersion = valueStr
                _logsi.LogDictionary(SILevel.Verbose, "Discovered Spotify Connect device ServiceInfo.Properties: %s" % (deviceKey), dspProperties)                        

            # add the device name to the list (if not already added).
            if deviceKey not in self._DiscoveredDeviceNames.keys():
                self._DiscoveredDeviceNames[deviceKey] = deviceName

            # add the device result to the list.
            self._DiscoveryResults.append(result)

            # trace.
            _logsi.LogObject(SILevel.Verbose, "Discovered Spotify Connect device result: %s" % (deviceKey), result, excludeNonPublic=True)                        

        elif (serviceStateChange is ServiceStateChange.Removed):
            _logsi.LogVerbose("Discovered Spotify Connect device removal (ignored): '%s' (%s:%s)", serviceName, serviceType, serviceStateChange)
            pass

        elif (serviceStateChange is ServiceStateChange.Updated):
            _logsi.LogVerbose("Discovered Spotify Connect device update (ignored): '%s' (%s:%s)", serviceName, serviceType, serviceStateChange)
            pass


    def DiscoverDevices(self, timeout:float=2) -> dict:
        """
        Discover Spotify Connect devices on the local network via the 
        ZeroConf (aka MDNS) service.

        Args:
            timeout (float): 
                Maximum amount of time to wait (in seconds) for the 
                discovery to complete.  
                Default is 2 seconds.
                
        Returns:
            A dictionary of `ZeroconfDiscoveryResult` objects.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyDiscovery/DiscoverDevices.py
        ```
        </details>
        """
        browser:ServiceBrowser = None

        # using Queue as a timer (timeout functionality).
        discoveryQueueTimer = Queue()
       
        try:

            # create the zeroconf service browser that will start device discovery.
            _logsi.LogVerbose("Discovery of Spotify Connect devices via Zeroconf is starting")
            browser = ServiceBrowser(self._ZeroconfClient, "_spotify-connect._tcp.local.", handlers=[self._OnServiceStateChange])
            
            # trace.
            _logsi.LogObject(SILevel.Verbose, "ZeroconfClient object after ServiceBrowser creation", self._ZeroconfClient)
            
            # give the ServiceBrowser time to discover.
            discoveryQueueTimer.get(timeout=timeout)
            
        except Empty:
            
            # this is not really an exception, but more of an indicator that
            # the timeout has been reached.
            _logsi.LogVerbose("Discovery of Spotify Connect devices via Zeroconf has reached its timeout of %f seconds" % timeout)
            
        finally:
            
            if (browser is not None):
                
                # remove the zeroconf service browser with associated listener and free resources.
                _logsi.LogVerbose("Releasing Zeroconf ServiceBrowser instance")
                browser.cancel()
                del browser
                _logsi.LogObject(SILevel.Verbose, "ZeroconfClient object after ServiceBrowser resources released", self._ZeroconfClient)

            # trace.
            _logsi.LogVerbose("Discovery of Spotify Connect devices via Zeroconf has ended")
        
        # return result to caller.
        return self._DiscoveredDeviceNames


    def ToString(self, includeItems:bool=False) -> str:
        """
        Returns a displayable string representation of the class.
        
        Args:
            includeItems (bool):
                True to include all items in the list; otherwise False to only
                include the base list.
        """
        msg:str = 'SpotifyDiscovery:'
        msg = "%s (%d items)" % (msg, len(self._DiscoveredDeviceNames))
        
        if includeItems == True:
            
            for key, deviceName in self._DiscoveredDeviceNames.items():
                msg = "%s\n- %s" % (msg, key)
            
        return msg
