# external package imports.

# our package imports.
from ..sautils import export
from .episodesimplified import EpisodeSimplified
from .showsimplified import ShowSimplified

@export
class Episode(EpisodeSimplified):
    """
    Spotify Web API Episode object.
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
        
        self._Show:ShowSimplified = None
        
        if (root is None):

            pass
        
        else:

            # process all collections and objects.
            item:dict = root.get('show',None)
            if item is not None:
                self._Show = ShowSimplified(root=item)

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Show(self) -> ShowSimplified:
        """ 
        The show on which the episode belongs.
        
        This is a `ShowSimplified` object.
        """
        return self._Show


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        # get base class result.
        resultBase:dict = super().ToDictionary()

        result:dict = \
        {
            'show': self._Show.ToDictionary(),
        }
        
        # combine base class results with these results.
        resultBase.update(result)
        
        # return a sorted dictionary.
        return dict(sorted(resultBase.items()))
        

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'Episode: %s' % super().ToString(False)
        if self._Show is not None: msg = '%s\n Show Name="%s"' % (msg, str(self._Show.Name))
        return msg

