# external package imports.
from zeroconf import ServiceInfo

# our package imports.
from ..sautils import export
from .zeroconfdiscoveryresult import ZeroconfDiscoveryResult
from spotifywebapipython.zeroconfapi.zeroconfgetinfo import ZeroconfGetInfo

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
        self._Name:str = None
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
    def IsChromeCast(self) -> bool:
        """ 
        True if the device is a Google ChromeCast device; otherwise, False.
        """
        if (self._DiscoveryResult is not None):
            return self._DiscoveryResult.IsChromeCast
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
        Spotify Connect device name and id value (e.g. '"Bose-ST10-1" (30fbc80e35598f3c242f2120413c943dfd9715fe)').
        """
        return '%s (%s)' % (self._Name, self._Id)
    

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
    

    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        result:dict = \
        {
            'Id': self._Id,
            'Name': self._Name,
            'Title': self.Title,
            'WasReConnected': self._WasReConnected,
            'IsChromeCast': self.IsChromeCast,
            'DeviceInfo': self._DeviceInfo.ToDictionary(),
            'DiscoveryResult': self._DiscoveryResult.ToDictionary(),
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
            msg = '%s\n WasReConnected="%s"' % (msg, str(self._WasReConnected))
           
        # build result.
        msg = '%s\n %s\n' % (msg, str(self._DeviceInfo.ToString(True)))
        msg = '%s\n %s\n' % (msg, str(self._DiscoveryResult.ToString(True)))
        return msg 
