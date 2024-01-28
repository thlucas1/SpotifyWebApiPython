# external package imports.

# our package imports.
from ..sautils import export
from .album import Album
from .externalids import ExternalIds
from .tracksimplified import TrackSimplified

@export
class Track(TrackSimplified):
    """
    Spotify Web API Track object.
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
        
        self._Album:Album = None
        self._ExternalIds:ExternalIds = None
        self._Popularity:int = None
        
        if (root is None):

            pass
        
        else:

            self._Popularity = root.get('popularity', None)

            # process all collections and objects.
            item:dict = root.get('album',None)
            if item is not None:
                self._Album = Album(root=item)

            item:dict = root.get('external_ids',None)
            if item is not None:
                self._ExternalIds = ExternalIds(root=item)

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Album(self) -> Album:
        """ 
        The album on which the track appears. 
        
        The album object includes a link in href to full information about the album.
        """
        return self._Album


    @property
    def ExternalIds(self) -> ExternalIds:
        """ 
        Known external ID's for the track.
        """
        return self._ExternalIds
    

    @property
    def Popularity(self) -> int:
        """ 
        The popularity of the track.  The value will be between 0 and 100, with 100 being the most popular.
        
        The popularity of a track is a value between 0 and 100, with 100 being the most popular. 
        The popularity is calculated by algorithm and is based, in the most part, on the total number 
        of plays the track has had and how recent those plays are. Generally speaking, songs that are 
        being played a lot now will have a higher popularity than songs that were played a lot in the past. 
        
        Duplicate tracks (e.g. the same track from a single and an album) are rated independently. 
        Artist and album popularity is derived mathematically from track popularity. 
        
        Note: the popularity value may lag actual popularity by a few days: the value is not updated in real time.
        """
        return self._Popularity


    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'Track: %s' % super().ToString(False)
        if self._Album is not None: msg = '%s\n Album="%s"' % (msg, str(self._Album.Name))
        #if self._ExternalIds is not None: msg = '%s\n %s' % (msg, str(self._ExternalIds))
        if self._Popularity is not None: msg = '%s\n Popularity="%s"' % (msg, str(self._Popularity))
        return msg 
