# external package imports.

# our package imports.
from ..sautils import export
from .zeroconfgetinfoalias import ZeroconfGetInfoAlias
from .zeroconfgetinfodrmmediaformat import ZeroconfGetInfoDrmMediaFormat
from .zeroconfresponse import ZeroconfResponse

@export
class ZeroconfGetInfo(ZeroconfResponse):
    """
    Spotify Web API Zeroconf GetInfo response object.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        # initialize base class.
        super().__init__(root=root)
        
        # initialize our attributes.
        self._AccountReq:str = None
        self._ActiveUser:str = None
        self._Aliases:list[ZeroconfGetInfoAlias] = []
        self._Availability:str = None
        self._BrandDisplayName:str = None
        self._ClientId:str = None
        self._DeviceId:str = None
        self._DeviceType:str = None
        self._GroupStatus:str = None
        self._LibraryVersion:str = None
        self._ModelDisplayName:str = None
        self._ProductId:str = None
        self._PublicKey:str = None
        self._RemoteName:str = None
        self._ResolverVersion:str = None
        self._Scope:str = None
        self._SupportedCapabilities:int = None
        self._SupportedDrmMediaFormats:list[ZeroconfGetInfoDrmMediaFormat] = []
        self._TokenType:str = None
        self._Version:str = None
        self._VoiceSupport:str = None
        
        if (root is None):

            pass
        
        else:

            self._AccountReq = root.get('accountReq', None)
            self._ActiveUser = root.get('activeUser', None)
            self._Availability = root.get('availability', None)
            self._BrandDisplayName = root.get('brandDisplayName', None)
            self._ClientId = root.get('clientID', None)
            self._DeviceId = root.get('deviceID', None)
            self._DeviceType = root.get('deviceType', None)
            self._GroupStatus = root.get('groupStatus', None)
            self._LibraryVersion = root.get('libraryVersion', None)
            self._ModelDisplayName = root.get('modelDisplayName', None)
            self._ProductId = root.get('productID', None)
            self._PublicKey = root.get('publicKey', None)
            self._RemoteName = root.get('remoteName', None)
            self._ResolverVersion = root.get('resolverVersion', None)
            self._Scope = root.get('scope', None)
            self._SupportedCapabilities = root.get('supported_capabilities', None)
            self._TokenType = root.get('tokenType', None)
            self._Version = root.get('version', None)
            self._VoiceSupport = root.get('voiceSupport', None)

            # process all collections and objects.
            items:list = root.get('aliases',None)
            if items is not None:
                for item in items:
                    self._Aliases.append(ZeroconfGetInfoAlias(root=item))

            items:list = root.get('supported_drm_media_formats',None)
            if items is not None:
                for item in items:
                    self._SupportedDrmMediaFormats.append(ZeroconfGetInfoDrmMediaFormat(root=item))

    
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def AccountReq(self) -> str:
        """ 
        ? TODO
        """
        return self._AccountReq


    @property
    def ActiveUser(self) -> str:
        """ 
        Canonical username of the logged in user (e.g. "31l77y2123456789012345678901").  
        
        This value will be blank if there is no user logged into the device.
        """
        return self._ActiveUser


    @property
    def Aliases(self) -> list:
        """ 
        
        """
        return self._Aliases


    @property
    def Availability(self) -> str:
        """ 
        ? TODO
        """
        return self._Availability


    @property
    def BrandDisplayName(self) -> str:
        """ 
        A UTF-8-encoded brand name of the hardware device, for hardware integrations (e.g. "Bose", "Onkyo", etc).
        """
        return self._BrandDisplayName


    @property
    def ClientId(self) -> str:
        """ 
        Client id of the application (e.g. "79ebcb219e8e4e123456789000123456").
        """
        return self._ClientId


    @property
    def DeviceId(self) -> str:
        """ 
        Unique device ID used for ZeroConf logins (e.g. "30fbc80e35598f3c242f2120413c943dfd9715fe").
        """
        return self._DeviceId


    @property
    def DeviceType(self) -> str:
        """ 
        Type of the device (e.g. "SPEAKER", "AVR", etc).
        
        Can be any of the following `SpDeviceType` devices:
        - kSpDeviceTypeComputer	    Laptop or desktop computer device.
        - kSpDeviceTypeTablet	    Tablet PC device.
        - kSpDeviceTypeSmartphone	Smartphone device.
        - kSpDeviceTypeSpeaker	    Speaker device.
        - kSpDeviceTypeTV	        Television device.
        - kSpDeviceTypeAVR	        Audio/Video receiver device.
        - kSpDeviceTypeSTB	        Set-Top Box device.
        - kSpDeviceTypeAudioDongle	Audio dongle device.
        - kSpDeviceTypeGameConsole	Game console device.
        - kSpDeviceTypeCastVideo	Chromecast Video.
        - kSpDeviceTypeCastAudio	Chromecast Audio.
        - kSpDeviceTypeAutomobile	Automobile.
        - kSpDeviceTypeSmartwatch	Smartwatch.
        - kSpDeviceTypeChromebook	Chromebook.        
        """
        return self._DeviceType


    @property
    def GroupStatus(self) -> str:
        """ 
        ? TODO ... (e.g. "NONE").
        """
        return self._GroupStatus


    @property
    def LibraryVersion(self) -> str:
        """ 
        Client library version that processed the Zeroconf action (e.g. "3.88.29-gc4d4bb01").
        """
        return self._LibraryVersion


    @property
    def ModelDisplayName(self) -> str:
        """ 
        A UTF-8-encoded model name of the hardware device, for hardware integrations (e.g. "Soundtouch").
        """
        return self._ModelDisplayName


    @property
    def ProductId(self) -> str:
        """ 
        An integer enumerating the product for this partner (e.g. 12345).
        """
        return self._ProductId


    @property
    def PublicKey(self) -> str:
        """ 
        Public key used in ZeroConf logins (e.g. "G+ZM4irhc...").
        """
        return self._PublicKey


    @property
    def RemoteName(self) -> str:
        """ 
        Name to be displayed for the device (e.g. "BOSE-ST10-1").
        """
        return self._RemoteName


    @property
    def ResolverVersion(self) -> str:
        """ 
        ? TODO ... (e.g. "0").
        """
        return self._ResolverVersion


    @property
    def Scope(self) -> str:
        """ 
        OAuth scope requested when authenticating with the Spotify backend (e.g. "streaming").
        """
        return self._Scope


    @property
    def SupportedCapabilities(self) -> int:
        """ 
        ? TODO
        """
        return self._SupportedCapabilities


    @property
    def SupportedDrmMediaFormats(self) -> list:
        """ 
        ? TODO
        """
        return self._SupportedDrmMediaFormats


    @property
    def TokenType(self) -> str:
        """ 
        Token type provided by the client (e.g. "accesstoken").
        """
        return self._TokenType


    @property
    def Version(self) -> str:
        """ 
        ZeroConf API version number (e.g. "2.10.0").
        """
        return self._Version


    @property
    def VoiceSupport(self) -> str:
        """ 
        Indicates if the device supports voice commands (e.g. "YES").
        """
        return self._VoiceSupport


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        # get base class result.
        resultBase:dict = super().ToDictionary()

        # get our attribute results.
        result:dict = \
        {
            'AccountReq': self._AccountReq,
            'ActiveUser': self._ActiveUser,
            'Aliases': [ item.ToDictionary() for item in self._Aliases ],
            'Availability': self._Availability,
            'BrandDisplayName': self._BrandDisplayName,
            'ClientId': self._ClientId,
            'DeviceId': self._DeviceId,
            'DeviceType': self._DeviceType,
            'GroupStatus': self._GroupStatus,
            'LibraryVersion': self._LibraryVersion,
            'ModelDisplayName': self._ModelDisplayName,
            'ProductId': self._ProductId,
            'PublicKey': self._PublicKey,
            'RemoteName': self._RemoteName,
            'ResolverVersion': self._ResolverVersion,
            'Scope': self._Scope,
            'SupportedCapabilities': self._SupportedCapabilities,
            'SupportedDrmMediaFormats': [ item.ToDictionary() for item in self._SupportedDrmMediaFormats ],
            'TokenType': self._TokenType,
            'Version': self._Version,
            'VoiceSupport': self._VoiceSupport,
        }
        
        # combine base class results with these results.
        resultBase.update(result)
        
        # return an unsorted dictionary.
        return resultBase
        

    def ToString(self, includeTitle:bool=True) -> str:
        """
        Returns a displayable string representation of the class.
        
        Args:
            includeTitle (str):
                True to include the class name title prefix.
        """
        msg:str = ''
        if includeTitle: 
            msg = 'ZeroconfGetInfo: '
            
        # get base class result.
        msg = '%s%s' % (msg, super().ToString(False))

        # get our attribute results.
        if self._AccountReq is not None: msg = '%s\n AccountReq="%s"' % (msg, str(self._AccountReq))
        if self._ActiveUser is not None: msg = '%s\n ActiveUser="%s"' % (msg, str(self._ActiveUser))
        if self._Aliases is not None: msg = '%s\n Aliases=%s' % (msg, str(self._Aliases))
        if self._Availability is not None: msg = '%s\n Availability="%s"' % (msg, str(self._Availability))
        if self._BrandDisplayName is not None: msg = '%s\n BrandDisplayName="%s"' % (msg, str(self._BrandDisplayName))
        if self._ClientId is not None: msg = '%s\n ClientId="%s"' % (msg, str(self._ClientId))
        if self._DeviceId is not None: msg = '%s\n DeviceId="%s"' % (msg, str(self._DeviceId))
        if self._DeviceType is not None: msg = '%s\n DeviceType="%s"' % (msg, str(self._DeviceType))
        if self._GroupStatus is not None: msg = '%s\n GroupStatus="%s"' % (msg, str(self._GroupStatus))
        if self._LibraryVersion is not None: msg = '%s\n LibraryVersion="%s"' % (msg, str(self._LibraryVersion))
        if self._ModelDisplayName is not None: msg = '%s\n ModelDisplayName="%s"' % (msg, str(self._ModelDisplayName))
        if self._ProductId is not None: msg = '%s\n ProductId="%s"' % (msg, str(self._ProductId))
        if self._PublicKey is not None: msg = '%s\n PublicKey="%s"' % (msg, str(self._PublicKey))
        if self._RemoteName is not None: msg = '%s\n RemoteName="%s"' % (msg, str(self._RemoteName))
        if self._ResolverVersion is not None: msg = '%s\n ResolverVersion="%s"' % (msg, str(self._ResolverVersion))
        if self._Scope is not None: msg = '%s\n Scope="%s"' % (msg, str(self._Scope))
        if self._SupportedCapabilities is not None: msg = '%s\n SupportedCapabilities="%s"' % (msg, str(self._SupportedCapabilities))
        if self._SupportedDrmMediaFormats is not None: msg = '%s\n SupportedDrmMediaFormats=%s' % (msg, str(self._SupportedDrmMediaFormats))
        if self._TokenType is not None: msg = '%s\n TokenType="%s"' % (msg, str(self._TokenType))
        if self._Version is not None: msg = '%s\n Version="%s"' % (msg, str(self._Version))
        if self._VoiceSupport is not None: msg = '%s\n VoiceSupport="%s"' % (msg, str(self._VoiceSupport))
        return msg 
