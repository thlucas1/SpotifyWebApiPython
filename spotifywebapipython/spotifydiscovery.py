# external package imports.
try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty
from time import sleep
from zeroconf import Zeroconf, ServiceBrowser, ServiceInfo, ServiceStateChange, IPVersion

# our package imports.
from .saappmessages import SAAppMessages
from .sautils import export
from .models.device import Device
from .spotifyclient import SpotifyClient, SpotifyApiError
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

    def __init__(self, spotifyClient:SpotifyClient=None, areDevicesVerified:bool=False, printToConsole:bool=False) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            spotifyClient (SpotifyClient):
                A SpotifyClient instance that will be used to verify discovered devices.   
                This can be null if the areDevicesVerified argument is False.  
                This argument is required if the areDevicesVerified argument is True.  
            areDevicesVerified (bool):
                True to create a `SpotifyClient` instance for discovered devices, which
                verifies that the device can be accessed and basic information obtained 
                about its capabilities; otherwise, False to just identify the IPV4 Address, 
                Port, and Device Name.  
                Default is False.
            printToConsole (bool):
                True to print discovered device information to the console as the devices
                are discovered; otherwise, False to not print anything to the console.
                Default is False.
                
        Specify False for the `areDevicesVerified` argument if you want to speed up
        device discovery, as it takes extra time to verify device connections as they 
        are discovered.
        """
        # validations.
        if spotifyClient is not None and (not isinstance(spotifyClient, SpotifyClient)):
            raise SpotifyApiError(SAAppMessages.ARGUMENT_TYPE_ERROR % ("__init__", 'spotifyClient', 'SpotifyClient', type(spotifyClient).__name__), logsi=_logsi)
        if spotifyClient is None and areDevicesVerified == True:
            raise SpotifyApiError("The spotifyClient argument is required if devices are to be verified (areDevicesVerified argument = True)", logsi=_logsi)

        # initialize instance properties.
        self._AreDevicesVerified:bool = areDevicesVerified
        self._DiscoveredDeviceNames:dict = {}
        self._DiscoveryResults:list[ZeroconfDiscoveryResult] = []
        self._PrintToConsole:bool = printToConsole
        self._SpotifyClient:SpotifyClient = spotifyClient
        self._VerifiedDevices:dict = {}


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
    def AreDevicesVerified(self) -> bool:
        """
        Determines if a `Device` object is created for devices that are
        discovered.  This property is set by what is passed to the class constructor.
        
        If False, then the `VerifiedDevices` property will be empty;
        
        If True, then the `VerifiedDevices` property will contain a `Device`
        instance for each device that was detected as part of the discovery process
        and was found in the Spotify User's player devices list.
        """
        return self._AreDevicesVerified
        

    @property
    def DiscoveredDeviceNames(self) -> dict:
        """
        A dictionary of discovered device names that were detected by the discovery process.
        
        Dictionary keys will be in the form of "address:port", where "address" is the device
        ipv4 address and the "port" is the ipv4 port number the Spotify Connect device
        is listening on.
        
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
    def VerifiedDevices(self) -> dict:
        """
        A dictionary of discovered `Device` instances that were detected on the network.
        
        This property is only populated if the `AreDevicesVerified` property is True.
        
        Dictionary keys will be in the form of "address:port", where "address" is the device
        ipv4 address and the "port" is the ipv4 port number the Spotify Connect device
        is listening on.
        
        Dictionary values will be `Device` instances that represent the discovered
        device.
        """
        return self._VerifiedDevices


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
            
            # create device instances for each ipv4 address found.
            for deviceIpAddress in ipAddressList:
                
                # create new result instance.
                result:ZeroconfDiscoveryResult = ZeroconfDiscoveryResult()
                result.DeviceName = deviceName
                result.Domain = '.local'
                result.HostIpv4Address = deviceIpAddress
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
                
                devicePort:int = serviceInfo.port
                deviceKey:str = '%s:%i' % (deviceIpAddress, devicePort)
                _logsi.LogVerbose("Discovered Spotify Connect device: %s - %s" % (deviceKey, deviceName))
                if (self._PrintToConsole == True):
                    print("Discovered Spotify Connect device: %s - %s" % (deviceKey, deviceName))
                _logsi.LogObject(SILevel.Verbose, "Discovered Spotify Connect device ServiceInfo: %s - %s" % (deviceKey, deviceName), serviceInfo) 
                
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
                    _logsi.LogDictionary(SILevel.Verbose, "Discovered Spotify Connect device ServiceInfo.Properties: '%s' (%s:%i)" % (deviceName, deviceIpAddress, devicePort), dspProperties)                        

                # add the device name to the list (if not already added) using its 
                # ipv4 address and port number as the key.
                if deviceKey not in self._DiscoveredDeviceNames.keys():
                    self._DiscoveredDeviceNames[deviceKey] = deviceName

                # add the device result to the list.
                self._DiscoveryResults.append(result)

                # are we verifying devices connections?  if so, then create a SpotifyClient
                # object, which will verify the connection and gather basic capabilities of the device.
                # we will also add the SpotifyClient instance using the same key as the device name list.
                if self._AreDevicesVerified == True:
                    
                    if deviceKey not in self._VerifiedDevices.keys():
                        
                        # get Spotify Connect player device by it's Name value.
                        device:Device = self._SpotifyClient.GetPlayerDevice(deviceName)
                        if device is not None:
                            self._VerifiedDevices[deviceKey] = device
                            result.SpotifyConnectIsInDeviceList = True

                # trace.
                _logsi.LogObject(SILevel.Verbose, "Discovered Spotify Connect device result: '%s' (%s:%i)" % (deviceName, deviceIpAddress, devicePort), result, excludeNonPublic=True)                        
                #_logsi.LogArray(SILevel.Verbose, "Discovered Spotify Connect device result.Properties: '%s' (%s:%i)" % (deviceName, deviceIpAddress, devicePort), result.Properties)                        

        elif (serviceStateChange is ServiceStateChange.Removed):
            _logsi.LogVerbose("Discovered Spotify Connect device removal (ignored): '%s' (%s:%s)", serviceName, serviceType, serviceStateChange)
            pass

        elif (serviceStateChange is ServiceStateChange.Updated):
            _logsi.LogVerbose("Discovered Spotify Connect device update (ignored): '%s' (%s:%s)", serviceName, serviceType, serviceStateChange)
            pass


    def DiscoverDevices(self, timeout:int=5) -> dict:
        """
        Discover Spotify Connect devices on the local network via the 
        ZeroConf (aka MDNS) service.

        Args:
            timeout (int): 
                Maximum amount of time to wait (in seconds) for the 
                discovery to complete.  
                Default is 5 seconds.
                
        Returns:
            A dictionary of discovered `SpotifyClient` objects.

        <details>
          <summary>Sample Code</summary>
        ```python
        .. include:: ../docs/include/samplecode/SpotifyDiscovery/DiscoverDevices.py
        ```
        </details>
        """
        # using Queue as a timer (timeout functionality).
        discoveryQueueTimer = Queue()

        # create the zeroconf service and our listener callback.
        zeroconf:Zeroconf = Zeroconf()
        
        # create the zeroconf service browser that will start device discovery.
        _logsi.LogVerbose("Discovery of Spotify Connect devices via Zeroconf is starting ...")
        ServiceBrowser(zeroconf, "_spotify-connect._tcp.local.", handlers=[self._OnServiceStateChange])
        
        try:
            # give the ServiceBrowser time to discover
            discoveryQueueTimer.get(timeout=timeout)
            
        except Empty:
            
            # this is not really an exception, but more of an indicator that
            # the timeout has been reached.
            _logsi.LogVerbose("Discovery of Spotify Connect devices via Zeroconf has ended.")
        
        return self._DiscoveredDeviceNames


    def BroadcastService(self, serviceInfo:ServiceInfo, port:int=5353) -> None:
        """
        Generate a Zeroconf / mDNS broadcast to announce a service, and sends the broadcast out.

        Args:
            serviceInfo (ServiceInfo): 
                Service information to broadcast.
            port (int): 
                mDNS port number to send the broadcast on.  
                Default is 5353.  
        """
        try:

            # create the zeroconf service.
            zeroconf:Zeroconf = Zeroconf(ip_version=IPVersion.V4Only)
                   
            # # TEST TODO - hardcoded serviceinfo properties for testing.
            # serviceType:str = '_spotify-connect._tcp.local.'
            # serviceName:str = 'Bose-ST10-95._spotify-connect._tcp.local.'
            # parsedAddresses:list[str] = ['192.168.1.82']
            # port:int = 8200
            # hostTTL:int = 120
            # priority:int = 0
            # otherTTL:int = 4500
            # server:str = 'Bose-SM2-987bf3244-95.local.'
            # weight:int = 0
            # properties:dict = {b'CPath': b'/zc', b'VERSION': b'1.0'}

            # # create the zeroconf serviceinfo object.
            # zcfServiceInfo:ServiceInfo = ServiceInfo(serviceType, serviceName, port, weight, priority, properties, server, hostTTL, otherTTL, parsed_addresses=parsedAddresses)
        
            # generate a broadcast packet to announce the service.
            _logsi.LogVerbose("Generating Zeroconf Service Broadcast for service: '%s'" % serviceInfo.name)
            dnsOutgoing = zeroconf.generate_service_broadcast(serviceInfo, serviceInfo.host_ttl, True)

            # send the broadcast packet.
            _logsi.LogVerbose("Sending Zeroconf Service Broadcast for service: '%s'" % serviceInfo.name)
            zeroconf.send(dnsOutgoing, addr=None, port=port)
           
        except Exception as ex:
            
            # this is not really an exception, but more of an indicator that
            # the timeout has been reached.
            _logsi.LogException("Zeroconf Broadcast Service exception: %s" % str(ex), ex, logToSystemLogger=False)
        

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
                device:Device
                verifiedStatus:str = ''
                device = self._VerifiedDevices.get(key, None)
                if device is not None:
                    verifiedStatus = ' (verified - ID=%s)' % device.Id
                msg = "%s\n- %s - %s %s" % (msg, key, deviceName, verifiedStatus)
            
        return msg
