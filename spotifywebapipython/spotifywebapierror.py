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
        self._RetryAfter:int = 0

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


    @property
    def RetryAfter(self) -> int:
        """ 
        The number of seconds to wait before retrying a method call that resulted in
        an HTTP status of 429 (rate-limit exceeded).

        This value is only valid if the HTTP response headers contained a `retry-after` key.
        This usually only happens when HTTP status code = 429.
        
        Example: `21`
        """
        return self._RetryAfter

    @RetryAfter.setter
    def RetryAfter(self, value:int):
        """ 
        Sets the RetryAfter property value.
        """
        if isinstance(value, int):
            if (value > 0):
                self._RetryAfter = value


    def ToString(self) -> str:
        """
        Returns a UI-friendly string representation of the class.
        """
        msg:str = SAAppMessages.MSG_SPOTIFY_WEB_API_ERROR.format(methodname=self._MethodName, 
                                                                 status=self._Status, 
                                                                 httpreason=self._HttpReason, 
                                                                 message=self._Message)
        return msg 
