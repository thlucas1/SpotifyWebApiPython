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
            items:list = root.get('items',None)
            if items is not None:
                for item in items:
                    if item is not None:
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
    

    def ContainsId(self, itemId:str=False) -> bool:
        """
        Checks the `Items` collection to see if an item already exists with the
        specified Id value.
        
        Returns True if the itemId exists in the collection; otherwise, False.
        """
        result:bool = False
        
        item:PlaylistSimplified
        for item in self._Items:
            if item.Id == itemId:
                result = True
                break
            
        return result
        

    def GetSpotifyOwnedItems(self) -> list[PlaylistSimplified]:
        """ 
        Gets a list of all items contained in the `Items` list that are owned 
        by `spotify:user:spotify`.
        """
        result:list[PlaylistSimplified] = []
        item:PlaylistSimplified
        for item in self._Items:
            if item.Owner is not None:
                if item.Owner.Uri == "spotify:user:spotify":
                    result.append(item)

        # sort items on Name property, ascending order.
        if len(result) > 0:
            result.sort(key=lambda x: (x.Name or "").lower(), reverse=False)

        return result
    
        
    def ToString(self, includeItems:bool=False) -> str:
        """
        Returns a displayable string representation of the class.
        
        Args:
            includeItems (bool):
                True to include the Items collection of objects; otherwise, False
                to only return base properties.
        """
        return 'PlaylistPageSimplified: %s' % super().ToString(includeItems)
