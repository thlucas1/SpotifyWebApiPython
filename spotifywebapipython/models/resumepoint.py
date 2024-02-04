# external package imports.

# our package imports.
from ..sautils import export

@export
class ResumePoint:
    """
    Spotify Web API Content ResumePoint object.
    
    Contains information about the user's most recent position in the episode.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._FullyPlayed:bool = None
        self._ResumePositionMS:int = None
        
        if (root is None):

            pass
        
        else:

            self._FullyPlayed = root.get('fully_played', None)
            self._ResumePositionMS = root.get('resume_position_ms', None)


    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def FullyPlayed(self) -> bool:
        """ 
        Whether or not the episode has been fully played by the user.
        """
        return self._FullyPlayed
    

    @property
    def ResumePositionMS(self) -> int:
        """ 
        The user's most recent position in the episode in milliseconds.
        """
        return self._ResumePositionMS
    

    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        result:dict = \
        {
            'fully_played': self._FullyPlayed,
            'resume_position_ms': self._ResumePositionMS,
        }
        return result
        

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'ResumePoint:'
        if self._FullyPlayed is not None: msg = '%s\n FullyPlayed="%s"' % (msg, str(self._FullyPlayed))
        if self._ResumePositionMS is not None: msg = '%s\n ResumePositionMS="%s"' % (msg, str(self._ResumePositionMS))
        return msg 
