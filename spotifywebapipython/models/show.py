# external package imports.

# our package imports.
from ..sautils import export
from .showsimplified import ShowSimplified
from .episodepagesimplified import EpisodePageSimplified

@export
class Show(ShowSimplified):
    """
    Spotify Web API Show object.
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
        
        self._Episodes:EpisodePageSimplified = None
        
        if (root is None):

            pass
        
        else:

            # process all collections and objects.
            item:dict = root.get('episodes',None)
            if item is not None:
                self._Episodes = EpisodePageSimplified(root=item)

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Episodes(self) -> EpisodePageSimplified:
        """ 
        The episodes of the show.
        
        This is a `EpisodePageSimplified` object.
        """
        return self._Episodes


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        # get base class result.
        resultBase:dict = super().ToDictionary()

        episodes:dict = {}
        if self._Episodes is not None:
            episodes = self._Episodes.ToDictionary()

        result:dict = \
        {
            'episodes': episodes
        }
        
        # combine base class results with these results.
        resultBase.update(result)
        
        # return an unsorted dictionary.
        return resultBase
        

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'Show: %s' % super().ToString(False)
        if self._Episodes is not None: msg = '%s\n Episode Count=%s' % (msg, str(self._Episodes.Total))
        return msg 
