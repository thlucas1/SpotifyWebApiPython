# our package imports.
from .authenticationtypes import AuthenticationTypes

class Credentials:
    """
    Credentials used by the Spotify SpConnectionLoginBlob method.
    """

    def __init__(
            self, 
            username:str, 
            password:str,
            authenticationType:AuthenticationTypes=AuthenticationTypes.USER_PASS,
            ):
        """
        Initializes a new instance of the class.
        
        Args:
            username (str):
                Spotify Connect user name to login with.  
            password (str):
                Spotify Connect user password to login with.  
            authenticationType (AuthenticationTypes):
                Authentication type.
        """
        # validations.
        if (authenticationType is None) or (not isinstance(authenticationType, AuthenticationTypes)):
            authenticationType = AuthenticationTypes.USER_PASS

        if (username is None):
            username = ""
        if (password is None):
            password = ""
        
        # initialize storage.
        self.username: bytes = username.encode('utf-8')

        if (isinstance(password, bytes)):
            self.password: bytes = password
        else:
            self.password: bytes = password.encode('utf-8')
        self.auth_type: AuthenticationTypes = authenticationType
        