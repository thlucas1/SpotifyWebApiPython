# external package imports.

# our package imports.
from ..sautils import export
from .tracksimplified import TrackSimplified
from .pageobject import PageObject

@export
class TrackPageSimplified(PageObject):
    """
    Spotify Web API SimplifiedTrackPage object.
    
    This allows for multiple pages of `TrackSimplified` objects to be navigated.
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
        self._Items:list[TrackSimplified] = []
        
        if (root is None):

            pass
        
        else:

            # process all collections and objects.
            items:list = root.get('items',None)
            if items is not None:
                for item in items:
                    if item is not None:
                        self._Items.append(TrackSimplified(root=item))

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Items(self) -> list[TrackSimplified]:
        """ 
        Array of `TrackSimplified` objects.
        """
        return self._Items
    

    def ContainsId(self, itemId:str=False) -> bool:
        """
        Checks the `Items` collection to see if an item already exists with the
        specified Id value.
        
        Returns True if the itemId exists in the collection; otherwise, False.
        """
        result:bool = False
        
        item:TrackSimplified
        for item in self._Items:
            if item.Id == itemId:
                result = True
                break
            
        return result
        

    def ToString(self, includeItems:bool=False) -> str:
        """
        Returns a displayable string representation of the class.
        
        Args:
            includeItems (bool):
                True to include the Items collection of objects; otherwise, False
                to only return base properties.
        """
        return 'TrackPageSimplified: %s' % super().ToString(includeItems)
