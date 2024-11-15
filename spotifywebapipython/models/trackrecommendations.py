# external package imports.

# our package imports.
from ..sautils import export
from .recommendationseed import RecommendationSeed
from .track import Track

@export
class TrackRecommendations:
    """
    Spotify Web API TrackRecommendations object.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._Seeds:list[RecommendationSeed] = []
        self._Tracks:list[Track] = []
        
        if (root is None):

            pass
        
        else:

            # process all collections and objects.
            items:list = root.get('seeds', [])
            if items is not None:
                for item in items:
                    self._Seeds.append(RecommendationSeed(root=item))
        
            items:list = root.get('tracks', [])
            if items is not None:
                for item in items:
                    self._Tracks.append(Track(root=item))

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Seeds(self) -> list[RecommendationSeed]:
        """ 
        A list of recommendation seed objects. 
        """
        return self._Seeds


    @property
    def Tracks(self) -> list[Track]:
        """ 
        A list of Track objects, ordered according to the parameters supplied
        to the `GetTrackRecommendations` method.
        """
        return self._Tracks


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        result:dict = \
        {
            'seeds': [ item.ToDictionary() for item in self._Seeds ],
            'tracks': [ item.ToDictionary() for item in self._Tracks ],
        }
        return result
        

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'TrackRecommendations:'
        if self._Seeds is not None: msg = '%s\n Seeds Count=%s' % (msg, str(len(self._Seeds)))
        if self._Tracks is not None: msg = '%s\n Tracks Count=%s' % (msg, str(len(self._Tracks)))
        return msg 
