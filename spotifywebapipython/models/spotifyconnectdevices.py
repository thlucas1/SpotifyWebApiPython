# external package imports.
from datetime import datetime
from typing import Iterator

# our package imports.
from ..sautils import export
from .device import Device
from .spotifyconnectdevice import SpotifyConnectDevice
from .playerplaystate import PlayerPlayState
from .zeroconfdiscoveryresult import ZeroconfDiscoveryResult
from spotifywebapipython.zeroconfapi import ZeroconfGetInfo, ZeroconfGetInfoAlias

# get smartinspect logger reference; create a new session for this module name.
from smartinspectpython.siauto import SIAuto, SILevel, SISession, SIMethodParmListContext
import logging

_logsi:SISession = SIAuto.Si.GetSession(__name__)
if (_logsi == None):
    _logsi = SIAuto.Si.AddSession(__name__, True)
_logsi.SystemLogger = logging.getLogger(__name__)


@export
class SpotifyConnectDevices():
    """
    Spotify Connect Devices collection.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        self._DateLastRefreshed:int = 0
        self._Items:list[SpotifyConnectDevice] = []


    def __getitem__(self, key) -> SpotifyConnectDevice:
        return self._Items[key]


    def __iter__(self) -> Iterator:
        return iter(self._Items)


    def __len__(self) -> int:
        return len(self._Items)


    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def AgeLastRefreshed(self) -> float:
        """ 
        Number of seconds between the current date time and the `DateLastRefreshed` property value.
        """
        return (datetime.utcnow().timestamp() - self._DateLastRefreshed)
    

    @property
    def DateLastRefreshed(self) -> float:
        """ 
        Date and time the device list was last refreshed, in unix epoch format (e.g. 1669123919.331225).
        """
        return self._DateLastRefreshed
    
    @DateLastRefreshed.setter
    def DateLastRefreshed(self, value:float):
        """ 
        Sets the DateLastRefreshed property value.
        """
        if isinstance(value, float):
            self._DateLastRefreshed = value
    

    @property
    def Items(self) -> list[SpotifyConnectDevice]:
        """ 
        Array of `SpotifyConnectDevice` objects.
        """
        return self._Items
    

    @property
    def ItemsCount(self) -> int:
        """ 
        Number of objects in the `Items` property array.
        """
        if self._Items is not None:
            return len(self._Items)
        return 0
    

    def AddDynamicDevice(
        self, 
        device:Device, 
        activeUser:str
        ) -> None:
        """ 
        Adds a new dynamic device entry to the `Items` collection.  
        
        Args:
            device (Device):
                Device information to add.
            activeUser (str):
                Currently active user id.

        Dynamic devices are Spotify Connect devices that are not found in Zeroconf discovery
        process, but still exist in the player device list.  These are usually Spotify Player
        client devices (e.g. mobile / web / desktop players) that utilize temporary device id's.
        """
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
        info.ActiveUser = activeUser
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
        self._Items.append(scDevice)

        # trace.
        _logsi.LogVerbose("Added dynamic device \"%s\" (%s) to Spotify Connect Devices collection" % (scDevice.Name, scDevice.Id))


    def UpdatePlayerDevices(
        self, 
        playerDevices:list[Device],
        activeUser:str,
        playerState:PlayerPlayState=None
        ) -> None:
        """ 
        Adds a list of dynamic player device entries to the `Items` collection, removes any
        existing dynamic devices from the collection that are not in the `playerDevices` list,
        and updates the currently active device based on playerState.
        
        Args:
            playerDevices (list[Device]):
                List of current player devices obtained via a call to `GetPlayerDevices` method.
            activeUser (str):
                Currently active user id.
            playerState (PlayerPlayState):
                Current player state obtained via a call to `GetPlayerPlaybackState` method
                which will be used to set the active device in the `Items` collection;
                otherwise, null to bypass active device set.

        Dynamic devices are Spotify Connect devices that are not found in Zeroconf discovery
        process, but still exist in the player device list.  These are usually Spotify Player
        client devices (e.g. mobile / web / desktop players) that utilize temporary device id's.
        """
        # validations
        if (not isinstance(playerDevices, list)):
            return

        # add dynamic devices.
        scDevice:SpotifyConnectDevice
        device:Device
        for device in playerDevices:

            # is the player device present in the collection? if not, then add it.
            if (not self.ContainsDeviceId(device.Id)):
                self.AddDynamicDevice(device, activeUser)
                        
            # is the device in the available device list for this user context?
            # if not, then set an indicator so we can re-activate it later if need be.
            for scDevice in self._Items:
                if (scDevice.DeviceInfo.DeviceId == device.Id):
                    scDevice.DeviceInfo.IsInDeviceList = True
                    break

        # remove stale dynamic devices from results collection;
        # the reversed() function creates an iterator that traverses the list in reverse order. 
        # this ensures that removing an element doesn't affect the indices of the subsequent 
        # elements we're going to iterate over.
        for idx in reversed(range(len(self._Items))):

            # only process dynamic devices.
            scDevice = self._Items[idx]
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
                    _logsi.LogVerbose("Removed dynamic device \"%s\" (%s) from Spotify Connect Devices collection" % (scDevice.Name, scDevice.Id))
                    self._Items.pop(idx)

        # are we updating active device entry?
        if (playerState is not None) and (isinstance(playerState, PlayerPlayState)):

            # we do this in case the active device is a "restricted" device; if it is, then it may 
            # not show up as the active device (common issue with Sonos devices).  
            # in this case, it WILL show up in the player state device property as the active device.
            # if it IS active, then we will set the active flag.        
            # note that the PlayerPlayState device is a name and not a device id.
            if playerState.Device is not None:
                device = playerState.Device
                for scDevice in self._Items:
                    scDevice.DeviceInfo.IsActiveDevice = False
                    if (device.Name == scDevice.Name):
                        _logsi.LogVerbose("Spotify Connect active device detected: \"%s\" (%s)" % (device.Name, device.Id))
                        scDevice.DeviceInfo.IsActiveDevice = True


    def ContainsDeviceId(self, value:str) -> bool:
        """ 
        Returns True if the `Items` collection contains the specified device id value;
        otherwise, False.
        
        Alias entries (if any) are also compared.
        """
        scDevice:SpotifyConnectDevice = self.GetDeviceById(value)
        if scDevice is not None:
            return True
        return False


    def ContainsDeviceName(self, value:str) -> bool:
        """ 
        Returns True if the `Items` collection contains the specified device name value;
        otherwise, False.
        
        Alias entries (if any) are also compared.
        """
        scDevice:SpotifyConnectDevice = self.GetDeviceByName(value)
        if scDevice is not None:
            return True
        return False
        

    def ContainsZeroconfEndpointGetInformation(self, value:str) -> bool:
        """ 
        Returns True if the `Items` collection contains the specified Zeroconf getInfo Endpoint url value;
        otherwise, False.
        """
        result:bool = False
        if value is None:
            return result
        
        # convert case for comparison.
        value = value.lower()
        
        # process all discovered devices.
        scDevice:SpotifyConnectDevice
        for scDevice in self._Items:
            if (scDevice.DiscoveryResult.ZeroconfApiEndpointGetInformation.lower() == value):
                result = True
                break
        return result
    

    def GetDeviceByDiscoveryKey(self, value:str) -> SpotifyConnectDevice:
        """ 
        Returns a `SpotifyConnectDevice` instance if the `Items` collection contains the specified 
        device zeroconf discovery results key value; otherwise, None.
        """
        result:SpotifyConnectDevice = None
        if value is None:
            return result
        
        # convert case for comparison.
        value = value.lower()

        # process all devices, comparing discovery keys.
        for i in range(len(self._Items)):
            if (self._Items[i].DiscoveryResult is not None):
                if (self._Items[i].DiscoveryResult.Key is not None):
                    if (self._Items[i].DiscoveryResult.Key.lower() == value):
                        result = self._Items[i]
                        break       
        return result


    def GetDeviceById(self, value:str) -> SpotifyConnectDevice:
        """ 
        Returns a `SpotifyConnectDevice` instance if the `Items` collection contains the specified 
        device id value; otherwise, None.
        
        Alias entries (if any) are also compared.
        """
        result:SpotifyConnectDevice = None
        if value is None:
            return result
        
        # convert case for comparison.
        value = value.lower()
        
        # process all discovered devices.
        scDevice:SpotifyConnectDevice
        for scDevice in self._Items:
            if (scDevice.DeviceInfo.HasAliases):
                scAlias:ZeroconfGetInfoAlias
                for scAlias in scDevice.DeviceInfo.Aliases:
                    if (scAlias.Id.lower() == value):
                        result = scDevice
                        break
                if result:
                    break
            else:
                if (scDevice.DeviceInfo.DeviceId.lower() == value):
                    result = scDevice
                    break
        return result
    

    def GetDeviceByName(self, value:str) -> SpotifyConnectDevice:
        """ 
        Returns a `SpotifyConnectDevice` instance if the `Items` collection contains the specified 
        device name value; otherwise, None.
        
        Alias entries (if any) are also compared.
        """
        result:SpotifyConnectDevice = None
        if value is None:
            return result
        
        # convert case for comparison.
        value = value.lower()
        
        # process all discovered devices.
        scDevice:SpotifyConnectDevice
        for scDevice in self._Items:
            if (scDevice.DeviceInfo.HasAliases):
                scAlias:ZeroconfGetInfoAlias
                for scAlias in scDevice.DeviceInfo.Aliases:
                    if (scAlias.Name.lower() == value):
                        result = scDevice
                        break
                if result is not None:
                    break
            else:
                if (scDevice.DeviceInfo.RemoteName.lower() == value):
                    result = scDevice
                    break
        return result
    

    def GetDeviceList(self) -> list[Device]:
        """
        Returns a list of `Device` objects that can be used to build a selection list
        of available devices.  
        
        Note that the `Device` object has the following properties populated:
        Id, Name, IsActive, Type.
        """
        result:list[Device] = []
        
        # process all discovered devices.
        scDevice:SpotifyConnectDevice
        for scDevice in self._Items:

            # map device information details.
            info:ZeroconfGetInfo = scDevice.DeviceInfo

            # create new mock device.
            device = Device()
            device.Type = info.DeviceType
                
            # are aliases being used (RemoteName is null if so)?
            if info.RemoteName is None:
                    
                # if aliases are defined, then use the alias details.
                infoAlias:ZeroconfGetInfoAlias
                for infoAlias in info.Aliases:
                    device.Id = infoAlias.Id
                    device.Name = infoAlias.Name

            else:

                # if no aliases then use the remote name and id.
                device.Id = info.DeviceId
                device.Name = info.RemoteName
                
            # append device to results.
            result.append(device)

        # sort items on Name property, ascending order.
        if len(result) > 0:
            result.sort(key=lambda x: (x.Name or "").lower(), reverse=False)

        return result
    

    def GetDeviceIndexByDiscoveryKey(self, value:str) -> int:
        """ 
        Returns the index of the `Items` collection entry that contains 
        the specified device zeroconf discovery results key value if found; 
        otherwise, -1.
        """
        result:int = -1
        if value is None:
            return result
        
        # convert case for comparison.
        value = value.lower()

        # process all devices, comparing discovery keys.
        for i in range(len(self._Items)):
            if (self._Items[i].DiscoveryResult is not None):
                if (self._Items[i].DiscoveryResult.Key is not None):
                    if (self._Items[i].DiscoveryResult.Key.lower() == value):
                        result = i
                        break       
        return result


    def GetDeviceIndexByDiscoveryName(self, value:str) -> int:
        """ 
        Returns the index of the `Items` collection entry that contains 
        the specified device zeroconf discovery results name value if found; 
        otherwise, -1.
        """
        result:int = -1
        if value is None:
            return result
        
        # convert case for comparison.
        value = value.lower()

        # process all devices, comparing discovery keys.
        for i in range(len(self._Items)):
            if (self._Items[i].DiscoveryResult is not None):
                if (self._Items[i].DiscoveryResult.Name is not None):
                    if (self._Items[i].DiscoveryResult.Name.lower() == value):
                        result = i
                        break       
        return result


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        result:dict = \
        {
            'AgeLastRefreshed': self.AgeLastRefreshed,
            'DateLastRefreshed': self._DateLastRefreshed,
            'ItemsCount': self.ItemsCount,
            'Items': [ item.ToDictionary() for item in self._Items ],
        }

        return result
        
           
    def ToString(self, includeItems:bool=False) -> str:
        """
        Returns a displayable string representation of the class.
        
        Args:
            includeItems (bool):
                True to include the Items collection of objects; otherwise, False
                to only return base properties.
        """
        msg:str = 'Items Count=%s' % (str(self.ItemsCount))
        msg:str = '%s, DateLastRefreshed=%s' % (msg, str(self._DateLastRefreshed))
        
        if (includeItems):
            item:SpotifyConnectDevice
            for item in self._Items:
                msg = "%s\n- %s" % (msg, item.ToString(True))
            
        return msg 
