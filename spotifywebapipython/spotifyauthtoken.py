# external package imports.
from datetime import datetime, timedelta
import time

# our package imports.
from .saappmessages import SAAppMessages

class SpotifyAuthToken:
    """
    Spotify Authorization Token class.
    """

    def __init__(self, authorizationType:str, profileId:str, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            authorizationType (str):
                Authorization type chosen when this token was generated.
            profileId (str):
                Profile identifier used when loading / storing the token to disk.  
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        # validation.
        if authorizationType is None or len(authorizationType.strip()) == 0:
            raise Exception(SAAppMessages.ARGUMENT_REQUIRED_ERROR % ('SpotifyAuthToken __init__','authorizationType'))
        
        # initialize storage.
        self._AccessToken:str = None
        self._AuthorizationType:str = authorizationType
        self._ExpireDateTimeUtc:datetime = None
        self._ExpiresAt:int = None
        self._ExpiresIn:int = None
        self._ProfileId:str = profileId
        self._RefreshToken:str = None
        self._Scope:str = None
        self._TokenType:str = None
        
        if (root is None):

            pass
        
        else:
            
            self._AccessToken = root.get('access_token', None)
            self._ExpiresAt = root.get('expires_at', None)
            self._ExpiresIn = root.get('expires_in', None)
            self._RefreshToken = root.get('refresh_token', None)
            self._Scope = root.get('scope', None)
            self._TokenType = root.get('token_type', None)

            # set non-JSON response properties.
            if self._ExpiresAt is not None:
                
                # calculate expire time based on ExpiresAt (epoch) seconds.
                self._ExpiresAt = int(self._ExpiresAt)  # convert from float to int, dropping microseconds.
                self._ExpireDateTimeUtc =  datetime.utcfromtimestamp(self._ExpiresAt)
                
            elif self._ExpiresIn is not None:
                
                # calculate expire time based on ExpiresIn seconds.
                unix_epoch = datetime(1970, 1, 1)
                dtUtcNow:datetime = datetime.utcnow()
                self._ExpireDateTimeUtc = dtUtcNow + timedelta(seconds=self._ExpiresIn)
                self._ExpiresAt = int((dtUtcNow - unix_epoch).total_seconds())  # seconds from epoch, current date
                self._ExpiresAt = self._ExpiresAt + self._ExpiresIn             # add ExpiresIn seconds

        # if scope is a list then convert to space-delimited value.
        if isinstance(self._Scope, list):
            self._Scope = ' '.join(self._Scope)
        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def AccessToken(self) -> str:
        """ 
        An access token that can be provided in subsequent calls to Spotify Web API services.
        """
        return self._AccessToken
    

    @property
    def AuthorizationType(self) -> str:
        """ 
        Authorization type chosen when this token was generated.
        
        It will be one of the following values:
        - "Authorization Code".
        - "Authorization Code with PKCE".
        - "Client Credentials".
        - "Implicit Grant".
        """
        return self._AuthorizationType
    

    def CreateDateTimeUtc(self) -> datetime:
        """ 
        DateTime (in UTC format) that the authorization token was created.
        """
        return self._CreateDateTimeUtc


    @property
    def ExpireDateTimeUtc(self) -> datetime:
        """ 
        DateTime (in UTC format) that the authorization token will expire.
        """
        return self._ExpireDateTimeUtc


    @property
    def ExpiresIn(self) -> int:
        """ 
        The time period (in seconds) for which the access token is valid.
        """
        return self._ExpiresIn
    

    @property
    def ExpiresAt(self) -> int:
        """ 
        DateTime (in epoch seconds) that the authorization token will expire.
        """
        return self._ExpiresAt
    

    @property
    def IsExpired(self) -> bool:
        """ 
        Returns true if the token has expired; otherwise, False if not expired.
        """
        if self._ExpiresAt is not None:
            nowsecs:int = int(time.time())
            # subtract 120 seconds (2 minutes) in case we are right at the edge of expiring.
            if (nowsecs + 120) > self._ExpiresAt:
                return True
        return False
    

    @property
    def ProfileId(self) -> str:
        """ 
        Profile identifier used when loading / storing the token to disk.
        """
        return self._ProfileId
    

    @property
    def RefreshToken(self) -> str:
        """ 
        The refresh token returned from the authorization token request.
        
        This is only set when using the "Authorization code" or "Authorization code with PKCE"
        authorization types.  
        
        There will be no refresh token for the "Client Credentials" or "Impllicit Grant"
        authorization types.  
        """
        return self._RefreshToken
    

    @property
    def Scope(self) -> str:
        """ 
        A space-separated list of scopes which have been granted for the `AccessToken`.
        
        If no scopes are specified, authorization will be granted only to access publicly available 
        information: that is, only information normally visible in the Spotify desktop, web, and 
        mobile players.
        
        Scopes can only be used with the "Authorization Code", "Authorization Code with PKCE", and
        "Implicit Grant" authorization types.

        Scopes cannot be used with the "Client Credentials" authorization type.
        """
        return self._Scope
    

    @property
    def Scopes(self) -> list[str]:
        """ 
        A list of scopes which have been granted for the `AccessToken`.       
        """
        if self._Scope is None:
            return []
        return self._Scope.split(' ')
    

    @property
    def TokenType(self) -> str:
        """ 
        How the access token may be used: always "Bearer" in this case.
        """
        return self._TokenType
    

    def GetHeaders(self) -> dict:
        """
        Returns a dictionary containing an 'Authorization': 'Bearer {token}' value,
        which can be used when makeing requests to the Spotify Web API.
        """
        headers:dict = {
            'Authorization': '{tokentype} {token}'.format(tokentype=self.TokenType, token=self.AccessToken)
        }
        return headers


    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'SpotifyAuthToken:'
        if self._AuthorizationType is not None: msg = '%s\n AuthorizationType="%s"' % (msg, str(self._AuthorizationType))
        if self._AccessToken is not None: msg = '%s\n AccessToken="%s"' % (msg, str(self._AccessToken))
        if self._ExpiresAt is not None: msg = '%s\n ExpiresAt="%s"' % (msg, str(self._ExpiresAt))
        if self._ExpiresIn is not None: msg = '%s\n ExpiresIn="%s"' % (msg, str(self._ExpiresIn))
        if self._ExpireDateTimeUtc is not None: msg = '%s\n ExpireDateTimeUtc="%s"' % (msg, str(self._ExpireDateTimeUtc))
        if self._ProfileId is not None: msg = '%s\n ProfileId="%s"' % (msg, str(self._ProfileId))
        if self._RefreshToken is not None: msg = '%s\n RefreshToken="%s"' % (msg, str(self._RefreshToken))
        if self._Scope is not None: msg = '%s\n Scope="%s"' % (msg, str(self._Scope))
        if self._TokenType is not None: msg = '%s\n TokenType="%s"' % (msg, str(self._TokenType))
        return msg 
