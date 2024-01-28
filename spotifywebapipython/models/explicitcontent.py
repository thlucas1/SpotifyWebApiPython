# external package imports.

# our package imports.
from ..sautils import export

@export
class ExplicitContent:
    """
    Spotify Web API Explicit Content object.
    
    Contains information about explicit content settings.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._FilterEnabled:bool = None
        self._FilterLocked:bool = None
        
        if (root is None):

            pass
        
        else:

            self._FilterEnabled = root.get('filter_enabled', None)
            self._FilterLocked = root.get('filter_locked', None)


    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def FilterEnabled(self) -> bool:
        """ 
        When true, indicates that explicit content should not be played.
        """
        return self._FilterEnabled
    

    @property
    def FilterLocked(self) -> bool:
        """ 
        When true, indicates that the explicit content setting is locked and 
        can't be changed by the user.
        """
        return self._FilterLocked


    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'ExplicitContent:'
        if self._FilterEnabled is not None: msg = '%s\n FilterEnabled="%s"' % (msg, str(self._FilterEnabled))
        if self._FilterLocked is not None: msg = '%s\n FilterLocked=%s' % (msg, str(self._FilterLocked))
        return msg 
