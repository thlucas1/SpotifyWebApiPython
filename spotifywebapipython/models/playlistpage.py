# external package imports.

# our package imports.
from ..sautils import export
from .pageobject import PageObject
from .playlisttrack import PlaylistTrack
from .track import Track

@export
class PlaylistPage(PageObject):
    """
    Spotify Web API PlaylistPage object.
    
    This allows for multiple pages of `PlaylistTrack` objects to be navigated.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        # initialize base class.
        super().__init__(root=root)
        
        # initialize storage.
        self._Items:list[PlaylistTrack] = []
        
        if (root is None):

            pass
        
        else:

            # process all collections and objects.
            items:list = root.get('items',None)
            if items is not None:
                for item in items:
                    if item is not None:
                        self._Items.append(PlaylistTrack(root=item))

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Items(self) -> list[PlaylistTrack]:
        """ 
        Array of `PlaylistTrack` objects.
        """
        return self._Items
    

    def GetTracks(self) -> list[Track]:
        """ 
        Gets a list of all tracks contained in the underlying `Items` list.
        
        This is a convenience method so one does not have to loop through the `Items`
        array of PlaylistTrack objects to get the list of tracks.
        """
        result:list[Track] = []
        item:PlaylistTrack
        for item in self._Items:
            result.append(item.Track)
        return result
    

    def ToString(self, includeItems:bool=False) -> str:
        """
        Returns a displayable string representation of the class.
        
        Args:
            includeItems (bool):
                True to include the Items collection of objects; otherwise, False
                to only return base properties.
        """
        return 'PlaylistPage: %s' % super().ToString(includeItems)
