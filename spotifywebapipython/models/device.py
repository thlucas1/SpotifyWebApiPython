# external package imports.

# our package imports.
from ..sautils import export

@export
class Device:
    """
    Spotify Web API Device object.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        # initialize storage.
        self._Id:str = None
        self._IsActive:bool = None
        self._IsPrivateSession:bool = None
        self._IsRestricted:bool = None
        self._Name:str = None
        self._Type:str = None
        self._VolumePercent:int = None
        self._SupportsVolume:bool = None
        
        if (root is None):

            pass
        
        else:

            self._Id = root.get('id', None)
            self._IsActive = root.get('is_active', None)
            self._IsPrivateSession = root.get('is_private_session', None)
            self._IsRestricted = root.get('is_restricted', None)
            self._Name = root.get('name', None)
            self._Type = root.get('type', None)
            self._VolumePercent = root.get('volume_percent', None)
            self._SupportsVolume = root.get('supports_volume', None)


    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Id(self) -> str:
        """ 
        The device ID.  
        
        This ID is unique and persistent to some extent. However, this is not guaranteed 
        and any cached device_id should periodically be cleared out and refetched as necessary.
        """
        return self._Id


    @property
    def IsActive(self) -> bool:
        """ 
        If this device is the currently active device.
        """
        return self._IsActive


    @property
    def IsPrivateSession(self) -> bool:
        """ 
        If this device is currently in a private session.
        """
        return self._IsPrivateSession


    @property
    def IsRestricted(self) -> bool:
        """ 
        Whether controlling this device is restricted.  
        
        At present if this is "true" then no Web API commands will be accepted by this device.
        """
        return self._IsRestricted


    @property
    def Name(self) -> str:
        """ 
        A human-readable name for the device. 
        
        Some devices have a name that the user can configure (e.g. "Loudest speaker") and some 
        devices have a generic name associated with the manufacturer or device model.
        
        Example: `Kitchen speaker`
        """
        return self._Name


    @property
    def Type(self) -> str:
        """ 
        Device type, such as `computer`, `smartphone` or `speaker`.
        
        Example: `computer`
        """
        return self._Type


    @property
    def VolumePercent(self) -> int:
        """ 
        The current volume in percent.
        
        Range: `0 - 100`
        Example: `59`
        """
        return self._VolumePercent


    @property
    def SupportsVolume(self) -> bool:
        """ 
        If this device can be used to set the volume.
        """
        return self._SupportsVolume


    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'Device:'
        if self._Id is not None: msg = '%s\n Id="%s"' % (msg, str(self._Id))
        if self._IsActive is not None: msg = '%s\n IsActive="%s"' % (msg, str(self._IsActive))
        if self._IsPrivateSession is not None: msg = '%s\n IsPrivateSession="%s"' % (msg, str(self._IsPrivateSession))
        if self._IsRestricted is not None: msg = '%s\n IsRestricted="%s"' % (msg, str(self._IsRestricted))
        if self._Name is not None: msg = '%s\n Name="%s"' % (msg, str(self._Name))
        if self._Type is not None: msg = '%s\n Type="%s"' % (msg, str(self._Type))
        if self._VolumePercent is not None: msg = '%s\n VolumePercent="%s"' % (msg, str(self._VolumePercent))
        if self._SupportsVolume is not None: msg = '%s\n SupportsVolume="%s"' % (msg, str(self._SupportsVolume))
        return msg 
