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
        self._SupportsVolume:bool = None
        self._Type:str = None
        self._VolumePercent:int = None
        
        if (root is None):

            pass
        
        else:

            self._Id = root.get('id', None)
            self._IsActive = root.get('is_active', None)
            self._IsPrivateSession = root.get('is_private_session', None)
            self._IsRestricted = root.get('is_restricted', None)
            self._Name = root.get('name', None)
            self._SupportsVolume = root.get('supports_volume', None)
            self._Type = root.get('type', None)
            self._VolumePercent = root.get('volume_percent', None)

        # post load validations.
        if self._IsActive is None:
            self._IsActive = False
        if self._IsPrivateSession is None:
            self._IsPrivateSession = False
        if self._IsRestricted is None:
            self._IsRestricted = False
        if self._SupportsVolume is None:
            self._SupportsVolume = False
        if self._VolumePercent is None:
            self._VolumePercent = 0


    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    # implement sorting support.
    def __eq__(self, other):
        try:
            return self.Name == other.Name
        except Exception as ex:
            if (isinstance(self, Device )) and (isinstance(other, Device )):
                return self.Name == other.Name
            return False

    def __lt__(self, other):
        try:
            return self.Name < other.Name
        except Exception as ex:
            if (isinstance(self, Device )) and (isinstance(other, Device )):
                return self.Name < other.Name
            return False


    @property
    def Id(self) -> str:
        """ 
        The device ID.  
        
        This ID is unique and persistent to some extent. However, this is not guaranteed 
        and any cached device_id should periodically be cleared out and refetched as necessary.
        """
        return self._Id

    @Id.setter
    def Id(self, value:str):
        """ 
        Sets the Id property value.
        """
        if isinstance(value, str):
            self._Id = value


    @property
    def IsActive(self) -> bool:
        """ 
        If this device is the currently active device.
        """
        return self._IsActive

    @IsActive.setter
    def IsActive(self, value:bool):
        """ 
        Sets the IsActive property value.
        """
        if isinstance(value, bool):
            self._IsActive = value


    @property
    def IsMuted(self) -> bool:
        """ 
        True if the player device volume is zero (muted); 
        otherwise, false.
        """
        return (self._VolumePercent == 0)


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

    @Name.setter
    def Name(self, value:str):
        """ 
        Sets the Name property value.
        """
        if isinstance(value, str):
            self._Name = value


    @property
    def SelectItemNameAndId(self) -> str:
        """
        Returns a string that can be used in a selection list in the
        form of "Name (Id)".
        
        This is a helper property, and not part of the Spotify Web API interface.
        """
        return "%s (%s)" % (self.Name, self.Id)
        

    @property
    def SupportsVolume(self) -> bool:
        """ 
        If this device can be used to set the volume.
        """
        return self._SupportsVolume


    @property
    def Type(self) -> str:
        """ 
        Device type, such as `computer`, `smartphone` or `speaker`.
        
        Example: `computer`
        """
        return self._Type

    @Type.setter
    def Type(self, value:str):
        """ 
        Sets the Type property value.
        """
        if isinstance(value, str):
            self._Type = value


    @property
    def VolumePercent(self) -> int:
        """ 
        The current volume in percent.
        
        Range: `0 - 100`
        Example: `59`
        """
        return self._VolumePercent

    @VolumePercent.setter
    def VolumePercent(self, value:int):
        """ 
        Sets the VolumePercent property value.
        """
        if isinstance(value, int):
            self._VolumePercent = value


    @staticmethod
    def GetIdFromSelectItem(value:str) -> str:
        """
        Returns the Id portion of a `SelectItemNameAndId` property value.
        
        Args:
            value (str):
                A `SelectItemNameAndId` property value.
                
        Returns:
            The Id portion of a `SelectItemNameAndId` property value, or None
            if the Id portion could not be determined.
        """
        result:str = None
        if isinstance(value, str):
            idx:int = value.rfind("(")
            if idx > -1:
                result = value[idx+1:len(value)-1]  # drop the "(" and ")"
        return result
        

    @staticmethod
    def GetNameFromSelectItem(value:str) -> str:
        """
        Returns the Name portion of a `SelectItemNameAndId` property value.
        
        Args:
            value (str):
                A `SelectItemNameAndId` property value.
                
        Returns:
            The Name portion of a `SelectItemNameAndId` property value, or None
            if the Name portion could not be determined.
        """
        result:str = None
        if isinstance(value, str):
            idx:int = value.rfind("(")
            if idx > -1:
                result = value[:idx-1]
        return result
        

    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        result:dict = \
        {
            'id': self._Id,
            'is_active': self._IsActive,
            'is_private_session': self._IsPrivateSession,
            'is_restricted': self._IsRestricted,
            'name': self._Name,
            'supports_volume': self._SupportsVolume,
            'type': self._Type,
            'volume_percent': self._VolumePercent,
            # helper property(s), not part of the Spotify Web API interface:
            'is_muted': self.IsMuted,
            'select_item_name_and_id': self.SelectItemNameAndId,
        }
        return result
        

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'Device:'
        if self._Id is not None: msg = '%s\n Id="%s"' % (msg, str(self._Id))
        if self._IsActive is not None: msg = '%s\n IsActive="%s"' % (msg, str(self._IsActive))
        if self.IsMuted is not None: msg = '%s\n IsMuted="%s"' % (msg, str(self.IsMuted))
        if self._IsPrivateSession is not None: msg = '%s\n IsPrivateSession="%s"' % (msg, str(self._IsPrivateSession))
        if self._IsRestricted is not None: msg = '%s\n IsRestricted="%s"' % (msg, str(self._IsRestricted))
        if self._Name is not None: msg = '%s\n Name="%s"' % (msg, str(self._Name))
        if self._SupportsVolume is not None: msg = '%s\n SupportsVolume="%s"' % (msg, str(self._SupportsVolume))
        if self._Type is not None: msg = '%s\n Type="%s"' % (msg, str(self._Type))
        if self._VolumePercent is not None: msg = '%s\n VolumePercent="%s"' % (msg, str(self._VolumePercent))
        return msg 
