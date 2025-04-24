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
from smartinspectpython.siauto import SIAuto, SILevel, SISession, SIMethodParmListContext, SIColors
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
                    if (scAlias.Id is not None):
                        if (scAlias.Id.lower() == value):
                            result = scDevice
                            break
                if result:
                    break
            else:
                if (scDevice.DeviceInfo.DeviceId is not None):
                    if (scDevice.DeviceInfo.DeviceId.lower() == value):
                        result = scDevice
                        break
        return result
    

    def GetDeviceByName(self, value:str) -> SpotifyConnectDevice:
        """ 
        Returns a `SpotifyConnectDevice` instance if the `Items` collection contains the specified 
        device name value; otherwise, None.
        
        Alias entries (if any) are also compared.
        Prefers a device with IsActiveDevice == True if available.
        """
        if value is None:
            return None
        
        # convert case for comparison.
        value = value.lower()
        matches: list[SpotifyConnectDevice] = []

        # process all discovered devices.
        for scDevice in self._Items:
            # search aliases (if defined).
            if (scDevice.DeviceInfo.HasAliases):
                for scAlias in scDevice.DeviceInfo.Aliases:
                    if (scAlias.Name is not None) and (scAlias.Name.lower() == value):
                        matches.append(scDevice)
                        break
            else:
                # match on `getInfo` RemoteName value (if defined).
                if (scDevice.DeviceInfo.RemoteName is not None) and (scDevice.DeviceInfo.RemoteName.lower() == value):
                    matches.append(scDevice)
                    continue
                # match on Zeroconf DeviceName value (if defined).
                if (scDevice.DiscoveryResult.DeviceName is not None) and (scDevice.DiscoveryResult.DeviceName.lower() == value):
                    matches.append(scDevice)
                    continue

        # prefer active device if present
        for device in matches:
            if device.IsActiveDevice:
                return device
            
        # return the first device if there are no active devices
        if matches:
            return matches[0]
        
        # return None if no matches are found at all
        return None
    

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
