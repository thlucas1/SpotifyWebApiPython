# external package imports.
from smartinspectpython.sisession import SISession

# our package imports.
from .sautils import export
from .saappmessages import SAAppMessages


@export
class SpotifyWebApiError(Exception):
    """
    Exception thrown when a Spotify Web API Regular Error occurs.
    """
    
    def __init__(self, status:int, message:str, methodName:str, reason:str, logsi:SISession=None) -> None:
        """
        Initializes a new instance of the class.

        Args:
            status (int):
                HTTP status code that is also returned in the response header.  
                For further information, see Response Status Codes.
            message (str):
                A short description of the cause of the error.
            methodName (str):
                Name of the client method that executed the request.
            reason (str):
                HTTP reason code for the error.
            logsi (SISession):
                Trace session object that this exception will be logged to, or null to bypass trace logging.  
                Default is None.
        """
        
        # initialize base class.
        super().__init__(message)
        
        # initialize class instance.
        self._HttpReason:str = reason
        self._Message:str = message
        self._MethodName:str = methodName
        self._Status:int = status

        # trace.
        if logsi is not None:
            if (isinstance(logsi, SISession)):
                logsi.LogException(str(self), self, logToSystemLogger=False)


    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def HttpReason(self) -> str:
        """ 
        HTTP reason code for the error.
        
        Example: `Bad Request`.
        """
        return self._HttpReason


    @property
    def Message(self) -> str:
        """ 
        A short description of the cause of the error.
        
        Example: `invalid id`.
        """
        return self._Message


    @property
    def MethodName(self) -> str:
        """ 
        The method being executed when the error occured.
        
        Example: `GetArtist`.
        """
        return self._MethodName


    @property
    def Status(self) -> int:
        """ 
        HTTP status code that is also returned in the response header.  
        For further information, see Response Status Codes.
        
        Example: `400`
        """
        return self._Status


    def ToString(self) -> str:
        """
        Returns a UI-friendly string representation of the class.
        """
        msg:str = SAAppMessages.MSG_SPOTIFY_WEB_API_ERROR.format(methodname=self._MethodName, 
                                                                 status=self._Status, 
                                                                 httpreason=self._HttpReason, 
                                                                 message=self._Message)
        return msg 
