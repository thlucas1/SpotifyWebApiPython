# external package imports.
try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty
import threading
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
        self._Zeroconf_RLock = threading.RLock()


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


    def ContainsId(self, value:str) -> bool:
        """ 
        Returns True if the `DiscoveryResults` collection contains the specified id value;
        otherwise, False.
        """
        item:ZeroconfDiscoveryResult = self.GetResultById(value)
        if item is not None:
            return True
        return False


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


    def GetIndexByKey(self, value:str) -> int:
        """ 
        Returns the index of the `DiscoveryResults` collection that contains 
        the specified device key value; otherwise, -1.
        """
        result:int = -1
        if value is None:
            return result
        
        # convert case for comparison.
        value = value.lower()

        # process all discovered devices.
        for i in range(len(self._DiscoveryResults)):
            if (self._DiscoveryResults[i].Key.lower() == value):
                result = i
                break       
        return result


    def GetResultById(self, value:str) -> bool:
        """ 
        Returns a `ZeroconfDiscoveryResult` instance if the `DiscoveryResults` collection contains 
        the specified device id value; otherwise, None.
        """
        result:ZeroconfDiscoveryResult = None
        if value is None:
            return result
        
        # convert case for comparison.
        value = value.lower()
        
        # process all discovered devices.
        item:ZeroconfDiscoveryResult
        for item in self._DiscoveryResults:
            if (item.Id.lower() == value):
                result = item
                break
        return result


    @property
    def ZeroconfClient(self) -> Zeroconf:
        """ 
        Zeroconf client instance that will be used to discover Spotify Connect devices.
        """
        return self._ZeroconfClient
    

    def _GetZeroconfDiscoveryResult(
        self,
        zeroconf:Zeroconf, 
        serviceType:str, 
        serviceName:str, 
        serviceStateChange:ServiceStateChange,
        serviceStateChangeDesc:str
        ) -> ZeroconfDiscoveryResult:
        """
        Builds a `ZeroconfDiscoveryResult` instance from Zeroconf Service Information data.
        """
        result:ZeroconfDiscoveryResult = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)
            
            # get device service information instance; if none, then we are done.
            deviceName:str = (serviceName.split(".")[0])
            serviceInfo:ServiceInfo = zeroconf.get_service_info(serviceType, serviceName)
            if serviceInfo is None:
                _logsi.LogVerbose("Spotify Connect Zeroconf discovery service notification ignored: \"%s\" (%s:%s) - no serviceinfo data" % (serviceName, serviceType, serviceStateChange))
                return result

            # get list of displayable (parsed) ipv4 addresses; if none, then we are done.
            ipAddressList = serviceInfo.parsed_addresses(IPVersion.V4Only)
            if (ipAddressList is None):
                _logsi.LogVerbose("Spotify Connect Zeroconf discovery service notification ignored: \"%s\" (%s:%s) - no IP address list" % (serviceName, serviceType, serviceStateChange))
                return result
            
            # trace.
            _logsi.LogObject(SILevel.Verbose, "Spotify Connect Zeroconf service details: \"%s\" %s (serviceinfo object)" % (deviceName, ipAddressList), serviceInfo) 
            
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
            result.ServiceType = serviceType
            result.Weight = serviceInfo.weight
            result.Id = "\"%s\" (%s:%s)" % (result.DeviceName, result.HostIpAddress, result.HostIpPort)

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
                _logsi.LogDictionary(SILevel.Verbose, "Spotify Connect Zeroconf service details: \"%s\" %s (serviceinfo properties)" % (deviceName, ipAddressList), dspProperties) 

            # trace.
            _logsi.LogObject(SILevel.Verbose, "Spotify Connect Zeroconf Discovery Result: %s (object)" % (result.Id), result, excludeNonPublic=True)                        

            # return discovery result.
            return result

        except Exception as ex:
            
            # trace.
            _logsi.LogException("Could not load ZeroconfDiscoveryResult instance from Zeroconf serviceinfo object.", ex, logToSystemLogger=False)
            
            # ignore exception
            return None
            
        finally:
            
            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _OnServiceStateChange(
        self,
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

        # this method can be tested by issuing the following commands from an MS-DOS
        # command prompt to simulate Zeroconf registration updates.

        # - add a new Spotify Connect instance registration:
        # > dns-sd -R "MyTestSC1" _spotify-connect._tcp. local 8080 cpath=/zcXXX version=1.0
        
        # - update a new Spotify Connect instance registration; 
        # - if you change the name, service type, or port number, a NEW registration is created!
        # - for updates, the only thing you can really update is the TXT record properties.
        # > dns-sd -R "MyTestSC1" _spotify-connect._tcp. local 8080 cpath=/zcYYY version=1.0
        
        # - remove an existing Spotify Connect instance registration; 
        # > the only way to remove an entry is to kill the process the entry was created under!
        
        # enter the following section one thread at a time (threadsafe).
        with self._Zeroconf_RLock:

            # copy passed parameters to thread-safe storage.
            serviceType:str = service_type
            serviceName:str = name
            serviceStateChange:ServiceStateChange = state_change
            serviceStateChangeDesc:str = None

            try:

                # trace.
                _logsi.EnterMethod(SILevel.Debug)

                # process by the state change value.
                if (serviceStateChange is ServiceStateChange.Added) \
                or (serviceStateChange is ServiceStateChange.Updated):

                    # set service state change description.
                    serviceStateChangeDesc = "Added"
                    if (serviceStateChange is ServiceStateChange.Updated):
                        serviceStateChangeDesc = "Updated"

                    # trace.
                    _logsi.LogVerbose("Spotify Connect Zeroconf discovery service notification: \"%s\" (%s)" % (serviceName, serviceStateChangeDesc))

                    # build discovery result instance from service state information.
                    # if nothing returned, then don't bother!
                    result:ZeroconfDiscoveryResult = self._GetZeroconfDiscoveryResult(zeroconf, serviceType, serviceName, serviceStateChange, serviceStateChangeDesc)
                    if (result is None):
                        return

                    # add device name to list of registered names.
                    self._DiscoveredDeviceNames[result.Id] = result.DeviceName

                    # add / update discovered results by serviceinfo key value. 
                    # we use the serviceinfo KEY value (not SERVERKEY) since some manufacturers use random ip port 
                    # numbers, and the port number could have been updated.  in this case, the key SHOULD remain the same.
                    # note that a different serviceinfo key SHOULD be created for speaker groups; at least they are for BOSE devices.
                    idx:int = self.GetIndexByKey(result.Key)
                    if (idx == -1):
                        self._DiscoveryResults.append(result)  # add new result
                        _logsi.LogVerbose("Spotify Connect Zeroconf service discovery result was added: %s (%s)" % (result.Id, serviceStateChangeDesc))
                    else:
                        self._DiscoveryResults[idx] = result   # update existing result
                        _logsi.LogVerbose("Spotify Connect Zeroconf service discovery result was updated: %s (%s)" % (result.Id, serviceStateChangeDesc))

                    # trace.
                    if (self._PrintToConsole == True):
                        print("Spotify Connect Zeroconf service %s: %s" % (serviceStateChangeDesc, result.Id))

                elif (serviceStateChange is ServiceStateChange.Removed):

                    # set service state change description.
                    serviceStateChangeDesc = "Removed"

                    # trace.
                    _logsi.LogVerbose("Spotify Connect Zeroconf discovery service notification: \"%s\" (%s)" % (serviceName, serviceStateChangeDesc))

                    # build discovery result instance from service state information.
                    # if nothing returned, then don't bother!
                    result:ZeroconfDiscoveryResult = self._GetZeroconfDiscoveryResult(zeroconf, serviceType, serviceName, serviceStateChange, serviceStateChangeDesc)
                    if (result is None):
                        return

                    # remove device name from list of registered names.
                    self._DiscoveredDeviceNames.pop(result.Id, None)

                    # remove device from results collection;
                    # the reversed() function creates an iterator that traverses the list in reverse order. 
                    # This ensures that removing an element doesn't affect the indices of the subsequent 
                    # elements we're going to iterate over.
                    resultCompare:str = result.Id.lower()
                    for i in reversed(range(len(self._DiscoveryResults))):
                        if (self._DiscoveryResults[i].Id.lower() == resultCompare):

                            # remove discovery result.
                            result = self._DiscoveryResults.pop(i)

                            # trace.
                            _logsi.LogVerbose("Spotify Connect Zeroconf service %s: %s" % (serviceStateChangeDesc, result.Id))
                            if (self._PrintToConsole == True):
                                print("Spotify Connect Zeroconf service %s: %s" % (serviceStateChangeDesc, result.Id))

                            break

            except Exception as ex:
            
                # trace.
                _logsi.LogException("Unhandled exception occured while processing Spotify Connect Zeroconf discovery service notification (%s)" % (serviceStateChange), ex, logToSystemLogger=False)
            
                # ignore exception
                return None
            
            finally:
            
                # trace.
                _logsi.LeaveMethod(SILevel.Debug)


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
