# external package imports.

# our package imports.
from ..sautils import export

@export
class PlaylistTrackSummary:
    """
    Spotify Web API PlaylistTrackSummary object.
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

            # if not building the class from json response, then initialize various properties as 
            # the playlist is probably being built manually.
            self._Total = 0
        
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
        A link to the Web API endpoint where full details of the playlist's 
        tracks can be retrieved.
        """
        return self._Href


    @property
    def Total(self) -> int:
        """ 
        Number of tracks in the playlist.
        """
        return self._Total


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        result:dict = \
        {
            'href': self._Href,
            'total': self._Total,
        }
        return result
        

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'PlaylistTrackSummary:'
        if self._Href is not None: msg = '%s\n Href="%s"' % (msg, str(self._Href))
        if self._Total is not None: msg = '%s\n Total="%s"' % (msg, str(self._Total))
        return msg 
