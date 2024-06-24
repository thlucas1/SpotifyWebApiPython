# external package imports.
from datetime import datetime
from typing import Iterator

# our package imports.
from ..sautils import export
from .device import Device
from .spotifyconnectdevice import SpotifyConnectDevice
from .zeroconfdiscoveryresult import ZeroconfDiscoveryResult
from spotifywebapipython.zeroconfapi import ZeroconfGetInfo, ZeroconfGetInfoAlias

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
        return self._Presets[key]


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
    

    def AddDynamicDevice(self, device:Device, activeUser:str) -> None:
        """ 
        Adds a new dynamic device entry to the `Items` collection.  
        
        Dynamic devices are Spotify Connect devices that are not found in Zeroconf discovery
        process, but still exist in the player device list.  These are usually devices in
        a Spotify Connect web or mobile player.
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
        
        # add the device.
        scDevice:SpotifyConnectDevice = SpotifyConnectDevice()
        scDevice.DeviceInfo = info
        scDevice.DiscoveryResult = discoverResult
        self._Items.append(scDevice)


    def ContainsDeviceId(self, value:str) -> bool:
        """ 
        Returns True if the `Items` collection contains the specified device id value;
        otherwise, False.
        
        Alias entries (if any) are also compared.
        """
        result:bool = False
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
                        result = True
                        break
                if result:
                    break
            else:
                if (scDevice.DeviceInfo.DeviceId.lower() == value):
                    result = True
                    break
        return result
    

    def ContainsDeviceName(self, value:str) -> bool:
        """ 
        Returns True if the `Items` collection contains the specified device name value;
        otherwise, False.
        
        Alias entries (if any) are also compared.
        """
        result:bool = False
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
                        result = True
                        break
                if result:
                    break
            else:
                if (scDevice.DeviceInfo.RemoteName.lower() == value):
                    result = True
                    break
        return result
    

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
            #device.IsActive = info.HasActiveUser
            device.IsActive = info.IsAvailable
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
    

    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        result:dict = \
        {
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
