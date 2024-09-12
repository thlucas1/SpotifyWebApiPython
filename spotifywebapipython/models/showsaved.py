# external package imports.

# our package imports.
from ..sautils import export
from .showsimplified import ShowSimplified

@export
class ShowSaved:
    """
    Spotify Web API SavedShow object.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._Show:ShowSimplified = None
        self._AddedAt:str = None
        
        if (root is None):

            pass
        
        else:

            self._AddedAt = root.get('added_at', None)

            # process all collections and objects.
            item:dict = root.get('show',None)
            if item is not None:
                self._Show = ShowSimplified(root=item)

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def AddedAt(self) -> str:
        """ 
        The date and time the show was saved. 
        
        Timestamps are returned in ISO 8601 format as Coordinated Universal Time (UTC) with a zero 
        offset: YYYY-MM-DDTHH:MM:SSZ. If the time is imprecise (for example, the date/time of an 
        episode release), an additional field indicates the precision; see for example, release_date 
        in an episode object.
        """
        return self._AddedAt


    @property
    def Show(self) -> ShowSimplified:
        """ 
        Information about the show.
        """
        return self._Show
    

    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        show:dict = {}
        if self._Show is not None:
            show = self._Show.ToDictionary()

        result:dict = \
        {
            'added_at': self._AddedAt,
            'show': show
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
        msg:str = 'ShowSaved:'
        if self._AddedAt is not None: msg = '%s\n AddedAt="%s"' % (msg, str(self._AddedAt))
        
        if (includeItems):
            if self._Show is not None: msg = '%s\n %s' % (msg, str(self._Show))
            
        return msg 
