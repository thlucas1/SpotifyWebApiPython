# external package imports.
from smartinspectpython.sisession import SISession

# our package imports.
from .sautils import export
from .saappmessages import SAAppMessages


@export
class SpotifyWebApiAuthenticationError(Exception):
    """
    Exception thrown when a Spotify Web API Authentication Error occurs.
    
    Whenever the application makes requests related to authentication or authorization to Web API, 
    such as retrieving an access token or refreshing an access token, the error response follows 
    RFC 6749 on the OAuth 2.0 Authorization Framework.
    """
    
    def __init__(self, error:str, errorDescription:str, methodName:str, httpStatus:int, httpReason:str, logsi:SISession=None) -> None:
        """
        Initializes a new instance of the class.

        Args:
            error (str):
                A high level description of the error as specified in RFC 6749 Section 5.2.
            errorDescription (str):
                A more detailed description of the error as specified in RFC 6749 Section 4.1.2.1.
            methodName (str):
                Name of the client method that executed the request.
            httpStatus (str):
                HTTP status code for the error.
            httpReason (str):
                HTTP reason code for the error.
            logsi (SISession):
                Trace session object that this exception will be logged to, or null to bypass trace logging.  
                Default is None.
        """
        
        # initialize base class.
        super().__init__(errorDescription)
        
        # initialize class instance.
        self._Error:str = error
        self._ErrorDescription:str = errorDescription
        self._MethodName:str = methodName
        self._HttpReason:int = httpReason
        self._HttpStatus:str = httpStatus

        # trace.
        if logsi is not None:
            if (isinstance(logsi, SISession)):
                logsi.LogException(str(self), self, logToSystemLogger=False)


    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Error(self) -> str:
        """ 
        A high level description of the error as specified in RFC 6749 Section 5.2.
        
        Example: `invalid_client`.
        """
        return self._Error


    @property
    def ErrorDescription(self) -> str:
        """ 
        Message text, as reported by the element text of the error xml response.
        
        Example: `Invalid client secret`.
        """
        return self._ErrorDescription


    @property
    def HttpReason(self) -> str:
        """ 
        HTTP reason code for the error.
        
        Example: `Bad Request`.
        """
        return self._HttpReason


    @property
    def HttpStatus(self) -> int:
        """ 
        HTTP status code for the error.
        
        Example: `400`
        """
        return self._HttpStatus


    @property
    def MethodName(self) -> str:
        """ 
        The method being executed when the error occured.
        
        Example: `GetArtist`.
        """
        return self._MethodName


    def ToString(self) -> str:
        """
        Returns a UI-friendly string representation of the class.
        """
        msg:str = SAAppMessages.MSG_SPOTIFY_WEB_API_AUTH_ERROR.format(methodname=self._MethodName, 
                                                                      error=self._Error, 
                                                                      httpstatus=self._HttpStatus, 
                                                                      httpreason=self._HttpReason, 
                                                                      errordescription=self._ErrorDescription)
        return msg 
