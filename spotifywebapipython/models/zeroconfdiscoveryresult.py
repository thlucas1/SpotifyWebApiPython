# our package imports.
from ..sautils import export
from .zeroconfproperty import ZeroconfProperty

@export
class ZeroconfDiscoveryResult:
    """
    Zeroconf Discovery Result object.
    
    Information about the Zeroconf entry for a SpotifyConnect device as found by Zeroconf (mDNS).
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        self._DeviceName:str = None
        self._Domain:str = '.'
        self._HostIpAddresses:list = []
        self._HostIpPort:int = None
        self._HostTTL:int = None
        self._IsChromeCast:bool = False
        self._Id:str = None
        self._Key:str = None
        self._Name:str = None
        self._OtherTTL:int = None
        self._Priority:int = None
        self._Properties:list = []
        self._Server:str = None
        self._ServerKey:str = None
        self._ServiceType:str = None
        self._Weight:int = None

        # Spotify Connect specific properties:
        self._SpotifyConnectCPath:str = None
        self._SpotifyConnectVersion:str = None


    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Description(self) -> bool:
        """
        Returns a basic description of the device, and how source info was obtained.

        This is a helper property, and not part of the Zeroconf ServiceInfo result.
        """
        result:str = "Spotify Connect Zeroconf Device"
        if (self.IsChromeCast):
            result = "Chromecast Zeroconf Device"
        elif (self.IsDynamicDevice):
            result = "Dynamic Device"
        return result


    @property
    def DeviceName(self) -> str:
        """ 
        Device name (e.g. "Bose-ST10-1").
        """
        return self._DeviceName
    
    @DeviceName.setter
    def DeviceName(self, value:str):
        """ 
        Sets the DeviceName property value.
        """
        if isinstance(value, str):
            self._DeviceName = value


    @property
    def Domain(self) -> str:
        """ 
        Domain on which the service is located, which should match the one passed in during the query (e.g. "local.").
        """
        return self._Domain
    
    @Domain.setter
    def Domain(self, value:str):
        """ 
        Sets the Domain property value.
        """
        if isinstance(value, str):
            self._Domain = value


    @property
    def HostIpAddress(self) -> str:
        """ 
        IP address at which the host can be reached (e.g. "192.168.1.81").
        
        This value may also contain a DNS alias, if no IP addresses were discovered
        for the device.  This is very rare, but possible.
        """
        # return server alias by default.
        result:str = self._Server
        
        # if ip addresses present, then return the first one that was detected.
        # note that addresses are in LIFO order as detected by zeroconf discovery.
        if (len(self._HostIpAddresses) > 0):
            result = self._HostIpAddresses[len(self._HostIpAddresses) - 1]
            
        return result
    
    @HostIpAddress.setter
    def HostIpAddress(self, value:str):
        """ 
        Sets the HostIpAddress property value.
        """
        if isinstance(value, str):
            
            # if ip addresses present, then update the first one that was detected
            # as it is the address referenced by the `HostIpAddress` get method.
            # note that addresses are in LIFO order as detected by zeroconf discovery.
            if (len(self._HostIpAddresses) > 0):
                self._HostIpAddresses[len(self._HostIpAddresses) - 1] = value


    @property
    def HostIpAddresses(self) -> list:
        """ 
        IP address(es) at which the host can be reached (e.g. ["192.168.1.81", "172.30.32.1"]).
        
        Note that this value can contain multiple addresses.
        """
        return self._HostIpAddresses
    
    @HostIpAddresses.setter
    def HostIpAddresses(self, value:list):
        """ 
        Sets the HostIpAddresses property value.
        """
        if value is not None:
            if isinstance(value, list):
                self._HostIpAddresses = value


    @property
    def HostIpPort(self) -> int:
        """ 
        Port number (as an integer) for the service on the host (e.g. 8080).
        """
        return self._HostIpPort
    
    @HostIpPort.setter
    def HostIpPort(self, value:int):
        """ 
        Sets the HostIpPort property value.
        """
        if isinstance(value, int):
            self._HostIpPort = value


    @property
    def HostIpTitle(self) -> int:
        """ 
        Host IP Address and Port number for the service on the host (e.g. 8080).

        Note that this value is a convenience property derived from the following
        properties: `HostIpAddress`,`HostIpPort`.
        """
        return "%s:%s" % (self.HostIpAddress or "", self.HostIpPort or "")
    

    @property
    def HostTTL(self) -> int:
        """ 
        Host Time-To-Live value (as an integer) for the service on the host (e.g. 1200).
        """
        return self._HostTTL
    
    @HostTTL.setter
    def HostTTL(self, value:int):
        """ 
        Sets the HostTTL property value.
        """
        if isinstance(value, int):
            self._HostTTL = value


    @property
    def Id(self) -> str:
        """ 
        Result ID (e.g. "Bose-ST10-1" (192.168.1.81:8200)).

        This is a helper property, and not part of the Zeroconf interface.
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
    def IsDynamicDevice(self) -> bool:
        """
        Returns True if the device is a dynamic device;
        otherwise, False.
        
        Dynamic devices are Spotify Connect devices that are not found in Zeroconf discovery
        process, but still exist in the player device list.  These are usually Spotify Connect
        web or mobile players with temporary device id's.       
        """
        return (self._HostIpPort == 0) and (self._ServiceType is None)


    @property
    def IsChromeCast(self) -> bool:
        """ 
        True if the device is a Google ChromeCast device; otherwise, False.
        """
        return self._IsChromeCast
    
    @IsChromeCast.setter
    def IsChromeCast(self, value:bool):
        """ 
        Sets the IsChromeCast property value.
        """
        if isinstance(value, bool):
            self._IsChromeCast = value


    @property
    def IsChromeCastGroup(self) -> bool:
        """ 
        True if the device is a Google ChromeCast Group device; otherwise, False.

        This is indicated by the ServerKey value starting with "Google-Cast-Group-".
        """
        serverKey:str = self._ServerKey or ""
        return (serverKey.lower().startswith("google-cast-group-"))
    

    @property
    def IsHostIpV6(self) -> bool:
        """
        Returns True if the `HostIpAddress` is a IPV6 formatted address;
        otherwise, False.
        """
        ipaddr:str = self.HostIpAddress or ""
        if (ipaddr.find(":")):
            return True
        return False


    @property
    def Key(self) -> str:
        """ 
        Service key (e.g. "bose-st10-2._spotify-connect._tcp.local.").
        """
        return self._Key
    
    @Key.setter
    def Key(self, value:str):
        """ 
        Sets the Key property value.
        """
        if isinstance(value, str):
            self._Key = value


    @property
    def Name(self) -> str:
        """ 
        Service name (e.g. "Bose-ST10-2._spotify-connect._tcp.local.").
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
    def Priority(self) -> int:
        """ 
        Priority value (as an integer) for the service on the host (e.g. 0).
        """
        return self._Priority
    
    @Priority.setter
    def Priority(self, value:int):
        """ 
        Sets the Priority property value.
        """
        if isinstance(value, int):
            self._Priority = value


    @property
    def OtherTTL(self) -> int:
        """ 
        Other Time-To-Live value (as an integer) for the service on the host (e.g. 5400).
        """
        return self._OtherTTL
    
    @OtherTTL.setter
    def OtherTTL(self, value:int):
        """ 
        Sets the OtherTTL property value.
        """
        if isinstance(value, int):
            self._OtherTTL = value


    @property
    def Properties(self) -> list[ZeroconfProperty]:
        """ 
        Discovered properties.
        """
        return self._Properties

    
    @property
    def Server(self) -> str:
        """ 
        Server name (e.g. "Bose-SM2-341513fbeeae.local.").
        """
        return self._Server
    
    @Server.setter
    def Server(self, value:str):
        """ 
        Sets the Server property value.
        """
        if isinstance(value, str):
            self._Server = value


    @property
    def ServerKey(self) -> str:
        """ 
        Server key (e.g. "bose-sm2-341513fbeeae.local.").
        """
        return self._ServerKey
    
    @ServerKey.setter
    def ServerKey(self, value:str):
        """ 
        Sets the ServerKey property value.
        """
        if isinstance(value, str):
            self._ServerKey = value


    @property
    def ServiceType(self) -> str:
        """ 
        Service type, which should match the one passed in during the query name (e.g. "_spotify-connect._tcp.").
        """
        return self._ServiceType
    
    @ServiceType.setter
    def ServiceType(self, value:str):
        """ 
        Sets the ServiceType property value.
        """
        if isinstance(value, str):
            self._ServiceType = value


    @property
    def Weight(self) -> int:
        """ 
        Weight value (as an integer) for the service on the host (e.g. 0).
        """
        return self._Weight
    
    @Weight.setter
    def Weight(self, value:int):
        """ 
        Sets the Weight property value.
        """
        if isinstance(value, int):
            self._Weight = value

    # *****************************************************************************
    # The following are Spotify Connect specific properties.
    # *****************************************************************************

    @property
    def SpotifyConnectCPath(self) -> str:
        """ 
        Spotify Connect CPath property value (e.g. "/zc").
        """
        return self._SpotifyConnectCPath
    
    @SpotifyConnectCPath.setter
    def SpotifyConnectCPath(self, value:str):
        """ 
        Sets the SpotifyConnectCPath property value.
        """
        if isinstance(value, str):
            self._SpotifyConnectCPath = value


    @property
    def SpotifyConnectVersion(self) -> str:
        """ 
        Spotify Connect Version property value (e.g. null, "1.0").

        """
        return self._SpotifyConnectVersion
    
    @SpotifyConnectVersion.setter
    def SpotifyConnectVersion(self, value:str):
        """ 
        Sets the SpotifyConnectVersion property value.
        """
        if (isinstance(value, str)) or (value is None):
            self._SpotifyConnectVersion = value


    @property
    def ZeroconfApiEndpointAddUser(self) -> str:
        """ 
        Zeroconf API endpoint to add a user to a Spotify Connect device (e.g. "http://192.168.1.81:8200/zc?action=addUser&version=2.10.0").
        """
        return self.GetEndpointUrl('addUser')
    

    @property
    def ZeroconfApiEndpointGetInformation(self) -> str:
        """ 
        Zeroconf API endpoint to retrieve device information for a Spotify Connect device (e.g. "http://192.168.1.81:8200/zc?action=getInfo&version=2.10.0").
        """
        return self.GetEndpointUrl('getInfo')
    

    @property
    def ZeroconfApiEndpointResetUsers(self) -> str:
        """ 
        Zeroconf API endpoint to reset users (e.g. Logoff) currently active on a Spotify Connect device (e.g. "http://192.168.1.81:8200/zc?action=resetUsers&version=2.10.0").
        """
        return self.GetEndpointUrl('resetUsers')
    

    def Equals(self, obj) -> bool:
        """
        Returns true if the specified object instance contains the same argument
        values as our object instance values; otherwise, False.

        Args:
            obj (ZeroconfDiscoveryResult):
                Object instance to compare.
        """
        result:bool = False
        if (not isinstance(obj, type(self))):
            return result

        # compare attributes for equality.
        if (self._DeviceName != obj._DeviceName): return result
        if (self._Domain != obj._Domain): return result
        if (self.HostIpAddress != obj.HostIpAddress): return result
        if (self._HostIpPort != obj._HostIpPort): return result
        if (self._HostTTL != obj._HostTTL): return result
        if (self._IsChromeCast != obj._IsChromeCast): return result
        if (self._Id != obj._Id): return result
        if (self._Key != obj._Key): return result
        if (self._Name != obj._Name): return result
        if (self._OtherTTL != obj._OtherTTL): return result
        if (self._Priority != obj._Priority): return result
        if (self._Server != obj._Server): return result
        if (self._ServerKey != obj._ServerKey): return result
        if (self._ServiceType != obj._ServiceType): return result
        if (self._Weight != obj._Weight): return result
        if (self._SpotifyConnectCPath != obj._SpotifyConnectCPath): return result
        if (self._SpotifyConnectVersion != obj._SpotifyConnectVersion): return result

        # don't compare the following:
        # self._Properties:list = []

        # objects attributes are equal.
        return True


    def GetEndpointUrl(self, action:str) -> str:
        """
        Gets a Spotify Zeroconf API endpoint url for the specified action key.
        
        Args:
            action (str):
                Spotify Zeroconf endpoint action to formulate (e.g. 'getInfo', 'addUser', 'resetUsers', etc).

        Returns:
            A string containing the endpoint url for the specified action key.
        """
        return "http://{ip}:{port}{cpath}?action={action}&version={version}".format(
            ip=self.HostIpAddress, 
            port=self.HostIpPort, 
            cpath=self.SpotifyConnectCPath, 
            action=action, 
            version=self.SpotifyConnectVersion or ''
            )


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        result:dict = \
        {
            'Id': self._Id,
            'DeviceName': self._DeviceName,
            'Domain': self._Domain,
            'HostIpAddress': self.HostIpAddress,
            'HostIpAddresses': [ str(item) for item in self._HostIpAddresses ],
            'HostIpPort': self._HostIpPort,
            'HostTTL': self._HostTTL,
            'IsChromeCast': self._IsChromeCast,
            'IsDynamicDevice': self.IsDynamicDevice,
            'Key': self._Key,
            'Name': self._Name,
            'Priority': self._Priority,
            'OtherTTL': self._OtherTTL,
            'Server': self._Server,
            'ServerKey': self._ServerKey,
            'ServiceType': self._ServiceType,
            'Weight': self._Weight,
            'Description': self.Description,
            'Properties': [ item.ToDictionary() for item in self._Properties ],
            'SpotifyConnectCPath': self._SpotifyConnectCPath,
            'SpotifyConnectVersion': self._SpotifyConnectVersion,
            'ZeroconfApiEndpointAddUser': self.ZeroconfApiEndpointAddUser,
            'ZeroconfApiEndpointGetInformation': self.ZeroconfApiEndpointGetInformation,
            'ZeroconfApiEndpointResetUsers': self.ZeroconfApiEndpointResetUsers,
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
            msg = 'ZeroconfDiscoveryResult:'
           
        # get dynamically generated property values.
        description:str = self.Description
        hostIpAddress:str = self.HostIpAddress
        isDynamicDevice:bool = self.IsDynamicDevice
        zeroconfApiEndpointAddUser:str = self.ZeroconfApiEndpointAddUser
        zeroconfApiEndpointGetInformation:str = self.ZeroconfApiEndpointGetInformation
        zeroconfApiEndpointResetUsers:str = self.ZeroconfApiEndpointResetUsers

        # build result.
        if self._Id is not None: msg = '%s\n Id="%s"' % (msg, str(self._Id))
        if self._DeviceName is not None: msg = '%s\n DeviceName="%s"' % (msg, str(self._DeviceName))
        if self._Domain is not None: msg = '%s\n Domain="%s"' % (msg, str(self._Domain))
        if self._HostIpAddresses is not None: msg = '%s\n HostIpAddresses Count=%s' % (msg, str(len(self._HostIpAddresses)))
        if hostIpAddress is not None: msg = '%s\n HostIpAddress="%s"' % (msg, str(hostIpAddress))
        if self._HostIpPort is not None: msg = '%s\n HostIpPort="%s"' % (msg, str(self._HostIpPort))
        if self._HostTTL is not None: msg = '%s\n HostTTL="%s"' % (msg, str(self._HostTTL))
        if isDynamicDevice is not None: msg = '%s\n IsDynamicDevice="%s"' % (msg, str(isDynamicDevice))
        if self._IsChromeCast is not None: msg = '%s\n IsChromeCast="%s"' % (msg, str(self._IsChromeCast))
        if self._Key is not None: msg = '%s\n Key="%s"' % (msg, str(self._Key))
        if self._Name is not None: msg = '%s\n Name="%s"' % (msg, str(self._Name))
        if self._Priority is not None: msg = '%s\n Priority="%s"' % (msg, str(self._Priority))
        if self._OtherTTL is not None: msg = '%s\n OtherTTL="%s"' % (msg, str(self._OtherTTL))
        if self._Server is not None: msg = '%s\n Server="%s"' % (msg, str(self._Server))
        if self._ServerKey is not None: msg = '%s\n ServerKey="%s"' % (msg, str(self._ServerKey))
        if self._ServiceType is not None: msg = '%s\n ServiceType="%s"' % (msg, str(self._ServiceType))
        if self._Weight is not None: msg = '%s\n Weight="%s"' % (msg, str(self._Weight))
        if description is not None: msg = '%s\n Description="%s"' % (msg, str(description))
        if self._Properties is not None: msg = '%s\n Properties Count=%s' % (msg, str(len(self._Properties)))
        if self._SpotifyConnectCPath is not None: msg = '%s\n SpotifyConnectCPath="%s"' % (msg, str(self._SpotifyConnectCPath))
        if self._SpotifyConnectVersion is not None: msg = '%s\n SpotifyConnectVersion="%s"' % (msg, str(self._SpotifyConnectVersion))
        if zeroconfApiEndpointAddUser is not None: msg = '%s\n ZeroconfApiEndpointAddUser="%s"' % (msg, zeroconfApiEndpointAddUser)
        if zeroconfApiEndpointGetInformation is not None: msg = '%s\n ZeroconfApiEndpointGetInformation="%s"' % (msg, zeroconfApiEndpointGetInformation)
        if zeroconfApiEndpointResetUsers is not None: msg = '%s\n ZeroconfApiEndpointResetUsers="%s"' % (msg, zeroconfApiEndpointResetUsers)
        return msg 
