# external package imports.

# our package imports.
from ..sautils import export
from .zeroconfgetinfoalias import ZeroconfGetInfoAlias
from .zeroconfgetinfodrmmediaformat import ZeroconfGetInfoDrmMediaFormat
from .zeroconfresponse import ZeroconfResponse

@export
class ZeroconfGetInfo(ZeroconfResponse):
    """
    Spotify Zeroconf API GetInfo response object.
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
        self._ActiveUser:str = ""
        self._Aliases:list[ZeroconfGetInfoAlias] = []
        self._Availability:str = ""
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
        
        # non-Spotify properties.
        self._IsActiveDevice:bool = None
        self._IsInDeviceList:bool = None
        
        if (root is None):

            pass
        
        else:

            self._AccountReq = root.get('accountReq', None)
            self._ActiveUser = root.get('activeUser', "")
            self._Availability = root.get('availability', "")
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
            #items:list = root.get('aliases', [{ "id":"aliasId","isGroup": False, "name":"aliasName" }])  # simulate an alias value (used for testing).
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
        ? (e.g. "DONTCARE").
        """
        return self._AccountReq


    @property
    def ActiveUser(self) -> str:
        """ 
        Canonical username of the logged in user (e.g. "31l77y2123456789012345678901").  
        
        This value will be an empty string if there is no user logged into the device.
        """
        return self._ActiveUser
    
    @ActiveUser.setter
    def ActiveUser(self, value:str):
        """ 
        Sets the ActiveUser property value.
        """
        if (isinstance(value, str)) or (value is None):
            self._ActiveUser = value


    @property
    def Aliases(self) -> list:
        """ 
        Device alias information, IF the device supports aliases.  
        
        Using ZeroConf, it is possible to announce multiple "virtual devices" from a device. 
        This allows the eSDK device to expose, for instance, multiroom zones as ZeroConf devices.  

        Device aliases will show up as separate devices in the Spotify app.  
        
        A maximum of 8 aliases are supported (SP_MAX_DEVICE_ALIASES).
        
        Please refer to the `RemoteName` property for more information.       
        """
        return self._Aliases


    @property
    def Availability(self) -> str:
        """ 
        The SpZeroConfVars availability field returned by SpZeroConfGetVars.  
        
        The following are values that I have encountered thus far:  
        - ""            - Device is available and ready for use.
        - "UNAVAILABLE" - Device is unavailable, and should probably be rebooted.
        - "NOT-LOADED"  - Spotify SDK / API is not loaded.
        
        The maximum length of the availability string (SP_MAX_AVAILABILITY_LENGTH) 
        is 15 characters (not counting terminating NULL).       
        """
        return self._Availability


    @property
    def BrandDisplayName(self) -> str:
        """ 
        A UTF-8-encoded brand name of the hardware device, for hardware integrations (e.g. "Bose", "Onkyo", etc).
        
        The maximum length of the brand display name (SP_MAX_BRAND_NAME_LENGTH) 
        is 32 characters (not counting terminating NULL).       
        """
        return self._BrandDisplayName

    @BrandDisplayName.setter
    def BrandDisplayName(self, value:str):
        """ 
        Sets the BrandDisplayName property value.
        """
        if (isinstance(value, str)) or (value is None):
            self._BrandDisplayName = value


    @property
    def ClientId(self) -> str:
        """ 
        Client id of the application (e.g. "79ebcb219e8e4e123456789000123456").
        
        The maximum length of the client ID value (SP_MAX_CLIENT_ID_LENGTH) 
        is 32 characters (not counting terminating NULL).
        """
        return self._ClientId


    @property
    def DeviceId(self) -> str:
        """ 
        Unique device ID used for ZeroConf logins (e.g. "30fbc80e35598f3c242f2120413c943dfd9715fe").

        The maximum length of the device ID value used for ZeroConf logins (SP_MAX_DEVICE_ID_LENGTH) 
        is 64 characters (not counting terminating NULL).
        """
        return self._DeviceId
    
    @DeviceId.setter
    def DeviceId(self, value:str):
        """ 
        Sets the DeviceId property value.
        """
        if (isinstance(value, str)) or (value is None):
            self._DeviceId = value


    @property
    def DeviceType(self) -> str:
        """ 
        Type of the device (e.g. "SPEAKER", "AVR", etc).
        
        Can be any of the following `SpDeviceType` devices:
        - Computer	    Laptop or desktop computer device.
        - Tablet	    Tablet PC device.
        - Smartphone	Smartphone device.
        - Speaker	    Speaker device.
        - TV	        Television device.
        - AVR	        Audio/Video receiver device.
        - STB	        Set-Top Box device.
        - AudioDongle	Audio dongle device.
        - GameConsole	Game console device.
        - CastVideo	    Chromecast Video.
        - CastAudio	    Chromecast Audio.
        - Automobile	Automobile.
        - Smartwatch	Smartwatch.
        - Chromebook	Chromebook.        
        
        The maximum length of the device type string (SP_MAX_DEVICE_TYPE_LENGTH) 
        is 15 characters (not counting terminating NULL).
        """
        return self._DeviceType
    
    @DeviceType.setter
    def DeviceType(self, value:str):
        """ 
        Sets the DeviceType property value.
        """
        if (isinstance(value, str)) or (value is None):
            self._DeviceType = value


    @property
    def GroupStatus(self) -> str:
        """ 
        The SpZeroConfVars group_status field returned by SpZeroConfGetVars (e.g. "NONE").

        The maximum length of the group status string (SP_MAX_GROUP_STATUS_LENGTH) 
        is 15 characters (not counting terminating NULL).
        """
        return self._GroupStatus


    @property
    def HasActiveUser(self) -> bool:
        """
        Returns True if the device has an active user account specified;
        otherwise, False.
        """
        return (self._ActiveUser != "")


    @property
    def HasAliases(self) -> bool:
        """
        Returns True if the device has alias entries defined;
        otherwise, False.
        """
        return (len(self._Aliases) > 0)


    @property
    def IsAvailable(self) -> bool:
        """ 
        Returns True if the device is available; otherwise, False.
        
        Determination is made based upon the `Availability` property value.
        """
        if (self._Availability is None) or (self._Availability == ""):
            return True
        return False
    

    @property
    def IsBrandSonos(self) -> bool:
        """ 
        Returns True if the device is a 'Sonos' branded device; otherwise, False.
        
        Determination is made based upon the `BrandDisplayName` property value.
        """
        result:bool = False
        if (isinstance(self._BrandDisplayName, str)) and (self._BrandDisplayName.lower().strip() == 'sonos'):
            result = True
        return result
    

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
        
        The maximum length of the model display name (SP_MAX_MODEL_NAME_LENGTH) 
        is 30 characters (not counting terminating NULL).
        """
        return self._ModelDisplayName

    @ModelDisplayName.setter
    def ModelDisplayName(self, value:str):
        """ 
        Sets the ModelDisplayName property value.
        """
        if (isinstance(value, str)) or (value is None):
            self._ModelDisplayName = value


    @property
    def ProductId(self) -> str:
        """ 
        An integer enumerating the product for this partner (e.g. 12345).
        """
        return self._ProductId

    @ProductId.setter
    def ProductId(self, value:str):
        """ 
        Sets the ProductId property value.
        """
        if (isinstance(value, str)) or (value is None):
            self._ProductId = value


    @property
    def PublicKey(self) -> str:
        """ 
        Public key used in ZeroConf logins (e.g. "G+ZM4irhc...").
        
        The maximum length of the public key used in ZeroConf logins (SP_MAX_PUBLIC_KEY_LENGTH) 
        is 149 characters (not counting terminating NULL).
        """
        return self._PublicKey

    @PublicKey.setter
    def PublicKey(self, value:str):
        """ 
        Sets the PublicKey property value.
        """
        if (isinstance(value, str)) or (value is None):
            self._PublicKey = value


    @property
    def RemoteName(self) -> str:
        """ 
        Name to be displayed for the device (e.g. "BOSE-ST10-1").
        
        This value will be null if the response is from a device using device aliases,
        as the displayed name for respective alias is defined in the aliases field.  
        
        Please refer to the `Aliases` property for more information.
        """
        return self._RemoteName
    
    @RemoteName.setter
    def RemoteName(self, value:str):
        """ 
        Sets the RemoteName property value.
        """
        if (isinstance(value, str)) or (value is None):
            self._RemoteName = value


    @property
    def ResolverVersion(self) -> str:
        """ 
        The SpZeroConfVars resolver_version field returned by SpZeroConfGetVars (e.g. "0").
        """
        return self._ResolverVersion


    @property
    def Scope(self) -> str:
        """ 
        OAuth scope requested when authenticating with the Spotify backend (e.g. "streaming").
        
        The maximum length of the token type string (SP_MAX_SCOPE_LENGTH) 
        is 64 characters (not counting terminating NULL).
        """
        return self._Scope


    @property
    def SupportedCapabilities(self) -> int:
        """ 
        Bitmasked integer representing list of device capabilities (e.g. 0).
        """
        return self._SupportedCapabilities


    @property
    def SupportedDrmMediaFormats(self) -> list:
        """ 
        The SpZeroConfVars supported_drm_media_formats field returned by SpZeroConfGetVars (e.g. []).
        
        A maximum of 8 formats are supported (SP_MAX_SUPPORTED_FORMATS).
        """
        return self._SupportedDrmMediaFormats


    @property
    def TokenType(self) -> str:
        """ 
        Token type provided by the client:
        - "accesstoken"         Access token.
        - "authorization_code"  OAuth Authorization Code token.
        - "default"             Default access token.
        
        The maximum length of the token type string (SP_MAX_TOKEN_TYPE_LENGTH) 
        is 30 characters (not counting terminating NULL).
        """
        return self._TokenType


    @property
    def Version(self) -> str:
        """ 
        ZeroConf API version number (e.g. "2.10.0").
        
        The maximum length of the library version string (SP_MAX_VERSION_LENGTH) 
        is 30 characters (not counting terminating NULL).
        """
        return self._Version


    @property
    def VoiceSupport(self) -> str:
        """ 
        Indicates if the device supports voice commands (e.g. "YES").
        """
        return self._VoiceSupport


    # non-Spotify properties.

    @property
    def IsActiveDevice(self) -> bool:
        """ 
        Returns True if this device is the currently active device;
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
    def IsInDeviceList(self) -> bool:
        """ 
        Returns the status of active device list verification:  
        * None - device list verification has not been performed for this device.  
        * True - device is a member of the active device list.  
        * False - device is NOT a member of the active device list.  
        """
        return self._IsInDeviceList
    
    @IsInDeviceList.setter
    def IsInDeviceList(self, value:bool):
        """ 
        Sets the IsInDeviceList property value.
        """
        if isinstance(value, bool):
            self._IsInDeviceList = value


    def Equals(self, obj) -> bool:
        """
        Returns true if the specified object instance contains the same argument
        values as our object instance values; otherwise, False.

        Args:
            obj (ZeroconfGetInfo):
                Object instance to compare.
        """
        result:bool = False
        if (not isinstance(obj, type(self))):
            return result

        # compare attributes for equality.
        if (self._AccountReq != obj._AccountReq): return result
        if (self._ActiveUser != obj._ActiveUser): return result
        if (self._Availability != obj._Availability): return result
        if (self._BrandDisplayName != obj._BrandDisplayName): return result
        if (self._ClientId != obj._ClientId): return result
        if (self._DeviceId != obj._DeviceId): return result
        if (self._DeviceType != obj._DeviceType): return result
        if (self._GroupStatus != obj._GroupStatus): return result
        if (self._LibraryVersion != obj._LibraryVersion): return result
        if (self._ModelDisplayName != obj._ModelDisplayName): return result
        if (self._ProductId != obj._ProductId): return result
        if (self._PublicKey != obj._PublicKey): return result
        if (self._RemoteName != obj._RemoteName): return result
        if (self._ResolverVersion != obj._ResolverVersion): return result
        if (self._Scope != obj._Scope): return result
        if (self._SupportedCapabilities != obj._SupportedCapabilities): return result
        if (self._TokenType != obj._TokenType): return result
        if (self._Version != obj._Version): return result
        if (self._VoiceSupport != obj._VoiceSupport): return result

        # don't compare the following:
        # self._Aliases:list[ZeroconfGetInfoAlias] = []
        # self._IsActiveDevice:bool = None
        # self._IsInDeviceList:bool = None
        # self._SupportedDrmMediaFormats:list[ZeroconfGetInfoDrmMediaFormat] = []
        
        # objects attributes are equal.
        return True


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
            # helper property(s), not part of the Spotify Web API interface:
            'HasActiveUser': self.HasActiveUser,
            'HasAliases': self.HasAliases,
            'IsAvailable': self.IsAvailable,
            'IsBrandSonos': self.IsBrandSonos,
            'IsActiveDevice': self._IsActiveDevice,
            'IsInDeviceList': self._IsInDeviceList,
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
        if self._IsActiveDevice is not None: msg = '%s\n IsActiveDevice="%s"' % (msg, str(self._IsActiveDevice))
        if self._IsInDeviceList is not None: msg = '%s\n IsInDeviceList="%s"' % (msg, str(self._IsInDeviceList))
        return msg 
