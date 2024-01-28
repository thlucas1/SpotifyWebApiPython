# external package imports.

# our package imports.
from ..sautils import export
from .tracksaved import TrackSaved
from .pageobject import PageObject

@export
class TrackPageSaved(PageObject):
    """
    Spotify Web API TrackPageSaved object.
    
    This allows for multiple pages of `TrackSaved` objects to be navigated.
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
        self._Items:list[TrackSaved] = []
        
        if (root is None):

            pass
        
        else:

            # process all collections and objects.
            items:list = root.get('items',[])
            for item in items:
                self._Items.append(TrackSaved(root=item))

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Items(self) -> list[TrackSaved]:
        """ 
        Array of `TrackSaved` objects.
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
        return 'TrackPageSaved: %s' % super().ToString(includeItems)
