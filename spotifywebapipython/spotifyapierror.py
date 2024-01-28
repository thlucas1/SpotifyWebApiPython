# external package imports.
from smartinspectpython.sisession import SISession

# our package imports.
from .sautils import export


@export
class SpotifyApiError(Exception):
    """
    Exception thrown when a SpotifyApi error occurs.
    """
    
    def __init__(self, message:str, ex:Exception=None, logsi:SISession=None) -> None:
        """
        Initializes a new instance of the class.

        Args:
            message (str):
                A short description of the cause of the error.
            ex (Exception):
                Inner exception that caused the current exception.  
                Default is None.
            logsi (SISession):
                Trace session object that this exception will be logged to, or null to bypass trace logging.  
                Default is None.
        """
        
        # initialize base class.
        super().__init__(message)
        
        # initialize class instance.
        self._Message:str = message

        # trace.
        if logsi is not None:
            if (isinstance(logsi, SISession)):
                if ex is None:
                    logsi.LogError(self.ToString())
                else:
                    logsi.LogException(message, ex, logToSystemLogger=False)


    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Message(self) -> str:
        """ 
        A description of the cause of the error.
        """
        return self._Message


    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'SpotifyApiError:'
        if self._Message is not None: msg = '%s %s' % (msg, str(self._Message))
        return msg 
