# external package imports.

# our package imports.
from ..sautils import export
from .albumsimplified import AlbumSimplified
from .pageobject import PageObject

@export
class AlbumPageSimplified(PageObject):
    """
    Spotify Web API SimplifiedAlbumPage object.
    
    This allows for multiple pages of `AlbumSimplified` objects to be navigated.
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
        self._Items:list[AlbumSimplified] = []
        
        if (root is None):

            self._Total = 0
        
        else:

            # process all collections and objects.
            items:list = root.get('items',None)
            if items is not None:
                for item in items:
                    self._Items.append(AlbumSimplified(root=item))

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Items(self) -> list[AlbumSimplified]:
        """ 
        Array of `AlbumSimplified` objects.
        """
        return self._Items
    

    def ContainsId(self, itemId:str=False) -> bool:
        """
        Checks the `Items` collection to see if an item already exists with the
        specified Id value.
        
        Returns True if the itemId exists in the collection; otherwise, False.
        """
        result:bool = False
        
        item:AlbumSimplified
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
        return 'AlbumPageSimplified: %s' % super().ToString(includeItems)
