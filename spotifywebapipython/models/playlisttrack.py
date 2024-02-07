# external package imports.

# our package imports.
from ..sautils import export
from .owner import Owner
from .track import Track

@export
class PlaylistTrack:
    """
    Spotify Web API PlaylistTrack object.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._AddedAt:str = None
        self._AddedBy:Owner = None
        self._IsLocal:bool = None
        self._Track:Track = None
        
        if (root is None):

            pass
        
        else:

            self._AddedAt = root.get('added_at', None)
            self._IsLocal = root.get('is_local', None)

            # process all collections and objects.
            item:dict = root.get('added_by',None)
            if item is not None:
                self._AddedBy = Owner(root=item)

            item:dict = root.get('track',None)
            if item is not None:
                self._Track = Track(root=item)

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def AddedAt(self) -> str:
        """ 
        The date and time the track or episode was added.  
        
        Note: some very old playlists may return null in this field.
        """
        return self._AddedAt


    @property
    def AddedBy(self) -> Owner:
        """ 
        The Spotify user who added the track or episode.  
        
        Note: some very old playlists may return null in this field.
        """
        return self._AddedBy


    @property
    def ImageUrl(self) -> str:
        """
        Gets the first image url in the underlying track album `Images` list, if images are defined;
        otherwise, null.
        """
        if self._Track is not None:
            if self._Track.Album is not None:
                return self._Track.Album.ImageUrl
        return None
            
        
    @property
    def IsLocal(self) -> bool:
        """ 
        Whether this track or episode is a local file (True) or not False).
        """
        return self._IsLocal


    @property
    def Track(self) -> Track:
        """ 
        Information about the track.
        """
        return self._Track
    

    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        addedBy:dict = {}
        if self._AddedBy is not None:
            addedBy = self._AddedBy.ToDictionary()

        track:dict = {}
        if self._Track is not None:
            track = self._Track.ToDictionary()

        result:dict = \
        {
            'added_at': self._AddedAt,
            'added_by': addedBy,
            'is_local': self._IsLocal,
            'track': track
        }
        return result
        

    def ToString(self, includeItems:bool=False) -> str:
        """
        Returns a displayable string representation of the class.
        
        Args:
            includeItems (bool):
                True to include the Items collection of objects; otherwise, False
                to only return base properties.
        """
        msg:str = 'PlaylistTrack:'
        if self._AddedAt is not None: msg = '%s\n AddedAt="%s"' % (msg, str(self._AddedAt))
        if self._AddedBy is not None: msg = '%s\n AddedBy="%s"' % (msg, str(self._AddedBy.Uri))
        if self._IsLocal is not None: msg = '%s\n IsLocal="%s"' % (msg, str(self._IsLocal))
        
        if (includeItems):
            if self._Track is not None: msg = '%s\n %s' % (msg, str(self._Track))
            
        return msg 
