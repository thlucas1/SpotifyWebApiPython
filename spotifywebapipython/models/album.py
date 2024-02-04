# external package imports.

# our package imports.
from ..sautils import export
from .albumsimplified import AlbumSimplified
from .copyright import Copyright
from .externalids import ExternalIds
from .externalurls import ExternalUrls
from .trackpagesimplified import TrackPageSimplified

@export
class Album(AlbumSimplified):
    """
    Spotify Web API Album object.
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
        self._Copyrights:list[Copyright] = []
        self._ExternalIds:ExternalIds = None
        self._Genres:list[str] = []
        self._Label:str = None
        self._Popularity:int = None
        self._Tracks:TrackPageSimplified = None
        
        if (root is None):

            pass
        
        else:

            self._Label = root.get('label', None)
            self._Popularity = root.get('popularity', None)

            # process all collections and objects.
            items:list = root.get('copyrights',[])
            for item in items:
                self._Copyrights.append(Copyright(root=item))

            item:dict = root.get('external_ids',None)
            if item is not None:
                self._ExternalIds = ExternalIds(root=item)

            items:list[str] = root.get('genres',[])
            for item in items:
                self._Genres.append(item)
        
            item:dict = root.get('tracks',None)
            if item is not None:
                self._Tracks = TrackPageSimplified(root=item)

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Copyrights(self) -> list[Copyright]:
        """ 
        The copyright statements of the album.
        """
        return self._Copyrights
    

    @property
    def ExternalIds(self) -> ExternalUrls:
        """ 
        Known external IDs for the album.
        """
        return self._ExternalIds
    

    @property
    def Genres(self) -> list[str]:
        """ 
        A list of the genres the album is associated with. If not yet classified, the array is empty.  
        
        Example: `["Egg punk","Noise rock"]`
        """
        return self._Genres


    @property
    def Label(self) -> str:
        """ 
        The label associated with the album.
        """
        return self._Label


    @property
    def Popularity(self) -> int:
        """ 
        The popularity of the album.  
        
        The value will be between 0 and 100, with 100 being the most popular.
        """
        return self._Popularity


    @property
    def Tracks(self) -> TrackPageSimplified:
        """ 
        The tracks of the album.
        
        This is a `TrackPageSimplified` object, meaning only 50 tracks max are listed per request.
        """
        return self._Tracks


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        # get base class result.
        resultBase:dict = super().ToDictionary()

        externalIds:dict = {}
        if self._ExternalIds is not None:
            externalIds = self._ExternalIds.ToDictionary()

        result:dict = \
        {
            'copyrights': [ item.ToDictionary() for item in self._Copyrights ],
            'external_ids': externalIds,
            'genres': [ item for item in self._Genres ],
            'label': self._Label,
            'popularity': self._Popularity,
        }
        
        # only add the tracks key if data is present.
        if self._Tracks is not None:
            tracks:dict = self._Tracks.ToDictionary()
            result['tracks'] = tracks
       
        # combine base class results with these results.
        resultBase.update(result)
        
        # return a sorted dictionary.
        return dict(sorted(resultBase.items()))
        

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'Album: %s' % super().ToString(False)
        #if self._Copyrights is not None: msg = '%s\n %s' % (msg, str(self._Copyrights))
        #if self._ExternalIds is not None: msg = '%s\n %s' % (msg, str(self._ExternalIds))
        if self._Genres is not None: msg = '%s\n Genres Count=%s' % (msg, str(len(self._Genres)))
        if self._Label is not None: msg = '%s\n Label="%s"' % (msg, str(self._Label))
        if self._Popularity is not None: msg = '%s\n Popularity="%s"' % (msg, str(self._Popularity))
        return msg 
