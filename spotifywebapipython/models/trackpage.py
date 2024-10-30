# external package imports.

# our package imports.
from ..sautils import export
from .track import Track
from .pageobject import PageObject

@export
class TrackPage(PageObject):
    """
    Spotify Web API TrackPage object.
    
    This allows for multiple pages of `Track` objects to be navigated.
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
        self._Items:list[Track] = []
        
        if (root is None):

            pass
        
        else:

            # process all collections and objects.
            items:list = root.get('items',None)
            if items is not None:
                for item in items:
                    if item is not None:
                        self._Items.append(Track(root=item))

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Items(self) -> list[Track]:
        """ 
        Array of `Track` objects.
        """
        return self._Items
    

    def GetUris(self, afterUri:str=None) -> str:
        """ 
        Gets a comma-delimited list of uri's contained in the underlying `Items` list.
        
        args:
            afterUri (str):
                If specified, the process will look for this uri before adding subsequent
                uri's to the returned results.  This allows you to skip uri's that have
                recently been played.
        
        This is a convenience method so one does not have to loop through the `Items`
        array of PlayHistory objects to get the list of uri's.
        """
        result:str = ""
        addUri:bool = False
        item:Track

        # add uri's from the beginning if no `afterUri` argument was passed.
        if (afterUri is None) or (len(afterUri.strip()) == 0):
            addUri = True
        
        for item in self._Items:

            if (not addUri):

                # check for `afterUri` match; if found, we will start adding uri's
                # to the list with the next item.
                if (afterUri == item.Uri):
                    addUri = True
                    
            elif (addUri):
                
                # add item uri to the list.
                if (len(result) > 0):
                    result += ","
                result += item.Uri
                
        return result
    

    def ToString(self, includeItems:bool=False) -> str:
        """
        Returns a displayable string representation of the class.
        
        Args:
            includeItems (bool):
                True to include the Items collection of objects; otherwise, False
                to only return base properties.
        """
        return 'TrackPage: %s' % super().ToString(includeItems)
