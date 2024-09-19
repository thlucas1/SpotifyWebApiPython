# external package imports.

# our package imports.
from ..sautils import export
from .show import Show
from .showsaved import ShowSaved
from .pageobject import PageObject

@export
class ShowPageSaved(PageObject):
    """
    Spotify Web API ShowPageSaved object.
    
    This allows for multiple pages of `ShowSaved` objects to be navigated.
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
        self._Items:list[ShowSaved] = []
        
        if (root is None):

            pass
        
        else:

            # process all collections and objects.
            items:list = root.get('items',None)
            if items is not None:
                for item in items:
                    if item is not None:
                        self._Items.append(ShowSaved(root=item))

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Items(self) -> list[ShowSaved]:
        """ 
        Array of `ShowSaved` objects.
        """
        return self._Items
    

    def GetShows(self) -> list[Show]:
        """ 
        Gets a list of all shows contained in the underlying `Items` list.
        
        This is a convenience method so one does not have to loop through the `Items`
        array of ShowSaved objects to get the list of shows.
        """
        result:list[Show] = []
        item:ShowSaved
        for item in self._Items:
            result.append(item.Show)
        return result
    

    def ToString(self, includeItems:bool=False) -> str:
        """
        Returns a displayable string representation of the class.
        
        Args:
            includeItems (bool):
                True to include the Items collection of objects; otherwise, False
                to only return base properties.
        """
        return 'ShowPageSaved: %s' % super().ToString(includeItems)
