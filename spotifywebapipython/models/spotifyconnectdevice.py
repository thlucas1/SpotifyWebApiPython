# external package imports.

# our package imports.
from ..sautils import export
from .zeroconfdiscoveryresult import ZeroconfDiscoveryResult
from spotifywebapipython.zeroconfapi import ZeroconfGetInfo, ZeroconfResponse

@export
class SpotifyConnectDevice():
    """
    Spotify Connect Device object.
    
    Information about the Spotify Connect device, which is a combination of the 
    `ZeroconfDiscoveryResult` and `ZeroconfGetInfo` classes.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        self._DiscoveryResult:ZeroconfDiscoveryResult = None
        self._DeviceInfo:ZeroconfGetInfo = None
        self._Id:str = None
        self._IsActiveDevice:bool = False
        self._IsInDeviceList:bool = False
        self._IsRestricted:bool = False
        self._Name:str = None
        self._ZeroconfResponseInfo:ZeroconfResponse = ZeroconfResponse()
        self._WasReConnected:bool = False


    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def DiscoveryResult(self) -> ZeroconfDiscoveryResult:
        """ 
        Information about the Zeroconf entry for a SpotifyConnect device as found by Zeroconf (mDNS).
        """
        return self._DiscoveryResult
    
    @DiscoveryResult.setter
    def DiscoveryResult(self, value:ZeroconfDiscoveryResult):
        """ 
        Sets the DiscoveryResult property value.
        """
        if isinstance(value, ZeroconfDiscoveryResult):
            self._DiscoveryResult = value


    @property
    def DeviceInfo(self) -> ZeroconfGetInfo:
        """ 
        Spotify Zeroconf API GetInfo response object.
        """
        return self._DeviceInfo
    
    @DeviceInfo.setter
    def DeviceInfo(self, value:ZeroconfGetInfo):
        """ 
        Sets the DeviceInfo property value.
        """
        if isinstance(value, ZeroconfGetInfo):
            self._DeviceInfo = value


    @property
    def Id(self) -> str:
        """ 
        Spotify Connect device id value (e.g. "30fbc80e35598f3c242f2120413c943dfd9715fe").
        """
        return self._Id
    
    @Id.setter
    def Id(self, value:str):
        """ 
        Sets the Id property value.
        """
        self._Id = value
    

    @property
    def IsActiveDevice(self) -> bool:
        """ 
        Returns True if this device is the currently active Spotify Web API player device;
        otherwise, False.
        """
        return self._IsActiveDevice
    
    @IsActiveDevice.setter
    def IsActiveDevice(self, value:bool):
        """ 
        Sets the IsActiveDevice property value.
        """
        if isinstance(value, bool):
            self._IsActiveDevice = value


    @property
    def IsChromeCast(self) -> bool:
        """ 
        True if the device is a Google ChromeCast device; otherwise, False.
        """
        if (self._DiscoveryResult is not None):
            return self._DiscoveryResult.IsChromeCast
        return False
    

    @property
    def IsInDeviceList(self) -> bool:
        """ 
        Returns True if this device is a member of the Spotify Web API player device list;
        otherwise, False.
        """
        return self._IsInDeviceList
    
    @IsInDeviceList.setter
    def IsInDeviceList(self, value:bool):
        """ 
        Sets the IsInDeviceList property value.
        """
        if isinstance(value, bool):
            self._IsInDeviceList = value


    @property
    def IsRestricted(self) -> bool:
        """ 
        Returns True if this device is a member of the Spotify Web API player device list;
        otherwise, False.
        """
        return self._IsRestricted
    
    @IsRestricted.setter
    def IsRestricted(self, value:bool):
        """ 
        Sets the IsRestricted property value.
        """
        if isinstance(value, bool):
            self._IsRestricted = value


    @property
    def IsSonos(self) -> bool:
        """ 
        True if the device is a Sonos device; otherwise, False.
        """
        if (self._DeviceInfo is not None):
            return self._DeviceInfo.IsBrandSonos
        return False
    

    @property
    def Name(self) -> str:
        """ 
        Spotify Connect device name value (e.g. "Bose-ST10-1").
        """
        return self._Name
    
    @Name.setter
    def Name(self, value:str):
        """ 
        Sets the Name property value.
        """
        self._Name = value
    

    @property
    def Title(self) -> str:
        """ 
        Spotify Connect device name and id value (e.g. "Bose-ST10-1" (30fbc80e35598f3c242f2120413c943dfd9715fe)).
        """
        return "\"%s\" (%s)" % (self._Name, self._Id)
    

    @property
    def WasReConnected(self) -> bool:
        """ 
        True if the device was re-connected, after being inactive or disconnected.
        """
        return self._WasReConnected
    
    @WasReConnected.setter
    def WasReConnected(self, value:bool):
        """ 
        Sets the WasReConnected property value.
        """
        self._WasReConnected = value
    

    @property
    def ZeroconfResponseInfo(self) -> ZeroconfResponse:
        """ 
        Spotify Zeroconf API Zeroconf response object.
        """
        return self._ZeroconfResponseInfo
    
    @ZeroconfResponseInfo.setter
    def ZeroconfResponseInfo(self, value:ZeroconfResponse):
        """ 
        Sets the ZeroconfResponseInfo property value.
        """
        if isinstance(value, ZeroconfResponse):
            self._ZeroconfResponseInfo = value


    def Equals(self, obj) -> bool:
        """
        Returns true if the specified object instance contains the same argument
        values as our object instance values; otherwise, False.

        Args:
            obj (SpotifyConnectDevice):
                Object instance to compare.
        """
        result:bool = False
        if (not isinstance(obj, type(self))):
            return result

        # compare attributes for equality.
        if (self._Id != obj._Id): return result
        if (self._Name != obj._Name): return result
        if (not self._DeviceInfo.Equals(obj._DeviceInfo)): return result
        if (not self._DiscoveryResult.Equals(obj._DiscoveryResult)): return result

        # objects attributes are equal.
        return True


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        result:dict = \
        {
            'Id': self._Id,
            'Name': self._Name,
            'Title': self.Title,
            'IsActiveDevice': self._IsActiveDevice,
            'IsChromeCast': self.IsChromeCast,
            'IsInDeviceList': self._IsInDeviceList,
            'IsRestricted': self._IsRestricted,
            'IsSonos': self.IsSonos,
            'WasReConnected': self._WasReConnected,
            'DeviceInfo': self._DeviceInfo.ToDictionary(),
            'DiscoveryResult': self._DiscoveryResult.ToDictionary(),
            'ZeroconfResponseInfo': self._ZeroconfResponseInfo.ToDictionary(),
        }
        return result
        

    def ToString(self, includeTitle:bool=True) -> str:
        """
        Returns a displayable string representation of the class.
        
        Args:
            includeTitle (str):
                True to include the class name title prefix.
        """
        msg:str = ''
        if includeTitle: 
            msg = 'Device: "%s" (%s)' % (self._Name, self._Id)
            msg = '%s\n IsActiveDevice="%s"' % (msg, str(self._IsActiveDevice))
            msg = '%s\n IsChromecast="%s"' % (msg, str(self.IsChromeCast))
            msg = '%s\n IsInDeviceList="%s"' % (msg, str(self._IsInDeviceList))
            msg = '%s\n IsRestricted="%s"' % (msg, str(self._IsRestricted))
            msg = '%s\n IsSonos="%s"' % (msg, str(self.IsSonos))
            msg = '%s\n WasReConnected="%s"' % (msg, str(self._WasReConnected))
            msg = '%s\n' % (msg)
           
        # build result.
        msg = '%s\n %s\n' % (msg, str(self._DeviceInfo.ToString(True)))
        msg = '%s\n %s\n' % (msg, str(self._DiscoveryResult.ToString(True)))
        msg = '%s\n %s\n' % (msg, str(self._ZeroconfResponseInfo.ToString(True)))
        return msg 
