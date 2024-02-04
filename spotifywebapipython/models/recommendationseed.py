# external package imports.

# our package imports.
from ..sautils import export

@export
class RecommendationSeed:
    """
    Spotify Web API Content RecommendationSeed object.
    
    Contains information about recommended tracks.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._AfterFilteringSize:int = 0
        self._AfterRelinkingSize:int = 0
        self._Href:str = None
        self._Id:str = None
        self._InitialPoolSize:int = 0
        self._Type:str = None
        
        if (root is None):

            pass
        
        else:

            self._AfterFilteringSize = root.get('afterFilteringSize', 0)
            self._AfterRelinkingSize = root.get('afterRelinkingSize', 0)
            self._Href = root.get('href', None)
            self._Id = root.get('id', None)
            self._InitialPoolSize = root.get('initialPoolSize', 0)
            self._Type = root.get('type', None)


    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def AfterFilteringSize(self) -> int:
        """ 
        The number of tracks available after min_* and max_* filters have been applied.
        """
        return self._AfterFilteringSize
    

    @property
    def AfterRelinkingSize(self) -> int:
        """ 
        The number of tracks available after relinking for regional availability.
        """
        return self._AfterRelinkingSize
    

    @property
    def Href(self) -> str:
        """ 
        A link to the full track or artist data for this seed.  
        
        For tracks this will be a link to a Track Object.  
        For artists a link to an Artist Object.  
        For genre seeds, this value will be null.
        """
        return self._Href
    

    @property
    def Id(self) -> str:
        """ 
        The id used to select this seed.  
        
        This will be the same as the string used in the seedArtists, seedTracks or seedGenres parameter.
        """
        return self._Id
    

    @property
    def InitialPoolSize(self) -> int:
        """ 
        The number of recommended tracks available for this seed.
        """
        return self._InitialPoolSize
    

    @property
    def Type(self) -> str:
        """ 
        The entity type of this seed.  
        
        One of `artist`, `track` or `genre`.
        """
        return self._Type


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        result:dict = \
        {
            'after_filtering_size': self._AfterFilteringSize,
            'after_relinking_size': self._AfterRelinkingSize,
            'href': self._Href,
            'id': self._Id,
            'initial_pool_size': self._InitialPoolSize,
            'type': self._Type,
        }
        return result
        

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'RecommendationSeed:'
        if self._AfterFilteringSize is not None: msg = '%s\n AfterFilteringSize="%s"' % (msg, str(self._AfterFilteringSize))
        if self._AfterRelinkingSize is not None: msg = '%s\n AfterRelinkingSize="%s"' % (msg, str(self._AfterRelinkingSize))
        if self._Href is not None: msg = '%s\n Href="%s"' % (msg, str(self._Href))
        if self._Id is not None: msg = '%s\n Id="%s"' % (msg, str(self._Id))
        if self._InitialPoolSize is not None: msg = '%s\n InitialPoolSize="%s"' % (msg, str(self._InitialPoolSize))
        if self._Type is not None: msg = '%s\n Type="%s"' % (msg, str(self._Type))
        return msg 
