# external package imports.

# our package imports.
from ..sautils import export
from .album import Album
from .albumsaved import AlbumSaved
from .pageobject import PageObject

@export
class AlbumPageSaved(PageObject):
    """
    Spotify Web API AlbumPageSaved object.
    
    This allows for multiple pages of `AlbumSaved` objects to be navigated.
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
        self._Items:list[AlbumSaved] = []
        
        if (root is None):

            pass
        
        else:

            # process all collections and objects.
            items:list = root.get('items',None)
            if items is not None:
                for item in items:
                    if item is not None:
                        self._Items.append(AlbumSaved(root=item))

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Items(self) -> list[AlbumSaved]:
        """ 
        Array of `AlbumSaved` objects.
        """
        return self._Items
    

    def GetAlbums(self) -> list[Album]:
        """ 
        Gets a list of all albums contained in the underlying `Items` list.
        
        This is a convenience method so one does not have to loop through the `Items`
        array of AlbumSaved objects to get the list of albums.
        """
        result:list[Album] = []
        item:AlbumSaved
        for item in self._Items:
            result.append(item.Album)
        return result
    

    def ToString(self, includeItems:bool=False) -> str:
        """
        Returns a displayable string representation of the class.
        
        Args:
            includeItems (bool):
                True to include the Items collection of objects; otherwise, False
                to only return base properties.
        """
        return 'AlbumPageSaved: %s' % super().ToString(includeItems)
