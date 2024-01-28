# external package imports.

# our package imports.
from ..sautils import export

@export
class Followers:
    """
    Spotify Web API Followers object.
    
    Contains information about the followers of an artist.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._Href:str = None
        self._Total:int = None
        
        if (root is None):

            pass
        
        else:

            self._Href = root.get('href', None)
            self._Total = root.get('total', None)


    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Href(self) -> str:
        """ 
        This will always be set to null, as the Web API does not support it at the moment.
        """
        return self._Href
    

    @property
    def Total(self) -> int:
        """ 
        The total number of followers.
        
        Example: `31288`
        """
        return self._Total


    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'Followers:'
        if self._Total is not None: msg = '%s\n Total=%s' % (msg, str(self._Total))
        if self._Href is not None: msg = '%s\n Href="%s"' % (msg, str(self._Href))
        return msg 
