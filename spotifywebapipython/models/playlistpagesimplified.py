# external package imports.

# our package imports.
from ..sautils import export
from .pageobject import PageObject
from .playlistsimplified import PlaylistSimplified

@export
class PlaylistPageSimplified(PageObject):
    """
    Spotify Web API PlaylistPageSimplified object.
    
    This allows for multiple pages of `PlaylistSimplified` objects to be navigated.
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
        self._Items:list[PlaylistSimplified] = []
        
        if (root is None):

            pass
        
        else:

            # process all collections and objects.
            items:list = root.get('items',[])
            for item in items:
                self._Items.append(PlaylistSimplified(root=item))

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Items(self) -> list[PlaylistSimplified]:
        """ 
        Array of `PlaylistSimplified` objects.
        """
        return self._Items
    

    def ToString(self, includeItems:bool=False) -> str:
        """
        Returns a displayable string representation of the class.
        
        Args:
            includeItems (bool):
                True to include the Items collection of objects; otherwise, False
                to only return base properties.
        """
        return 'PlaylistPageSimplified: %s' % super().ToString(includeItems)
