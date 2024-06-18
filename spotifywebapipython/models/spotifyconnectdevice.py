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


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        result:dict = \
        {
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
            msg = 'Device: "%s" (%s)' % (self._DiscoveryResult.DeviceName, self._DeviceInfo.DeviceId)
           
        # build result.
        msg = '%s\n %s\n' % (msg, str(self._DeviceInfo.ToString(True)))
        msg = '%s\n %s\n' % (msg, str(self._DiscoveryResult.ToString(True)))
        return msg 
