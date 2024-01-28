# external package imports.

# our package imports.
from ..sautils import export
from .album import Album

@export
class AlbumSaved:
    """
    Spotify Web API SavedAlbum object.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._Album:Album = None
        self._AddedAt:str = None
        
        if (root is None):

            pass
        
        else:

            self._AddedAt = root.get('added_at', None)

            # process all collections and objects.
            item:dict = root.get('album',None)
            if item is not None:
                self._Album = Album(root=item)

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def AddedAt(self) -> str:
        """ 
        The date and time the album was saved. 
        
        Timestamps are returned in ISO 8601 format as Coordinated Universal Time (UTC) with a zero 
        offset: YYYY-MM-DDTHH:MM:SSZ. If the time is imprecise (for example, the date/time of an 
        album release), an additional field indicates the precision; see for example, release_date 
        in an album object.
        """
        return self._AddedAt


    @property
    def Album(self) -> Album:
        """ 
        Information about the album.
        """
        return self._Album
    

    def ToString(self, includeItems:bool=False) -> str:
        """
        Returns a displayable string representation of the class.

        Args:
            includeItems (bool):
                True to include the Items collection of objects; otherwise, False
                to only return base properties.
        """
        msg:str = 'AlbumSaved:'
        if self._AddedAt is not None: msg = '%s\n AddedAt="%s"' % (msg, str(self._AddedAt))
        
        if self._Album is not None:
            if (includeItems):
                msg = '%s\n %s' % (msg, str(self._Album))
            else:
                msg = '%s, Album Name="%s"' % (msg, self._Album.Name)
            
        return msg 
