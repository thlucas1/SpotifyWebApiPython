# external package imports.

# our package imports.
from ..sautils import export
from .artistsimplified import ArtistSimplified
from .externalurls import ExternalUrls
from .restrictions import Restrictions

@export
class TrackSimplified:
    """
    Spotify Web API SimplifiedTrack object.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._Artists:list[ArtistSimplified] = []
        self._AvailableMarkets:list[str] = []
        self._DiscNumber:int = None
        self._DurationMS:int = None
        self._Explicit:bool = None
        self._ExternalUrls:ExternalUrls = None
        self._Href:str = None
        self._Id:int = None
        self._IsLocal:bool = None
        self._IsPlayable:bool = None
        #self._LinkedFrom:object = None
        self._Name:str = None
        self._PreviewUrl:str = None
        self._Restrictions:Restrictions = None
        self._TrackNumber:int = None
        self._Type:str = None
        self._Uri:str = None
        
        if (root is None):

            pass
        
        else:

            self._AvailableMarkets = root.get('available_markets', [])
            self._DiscNumber = root.get('disc_number', None)
            self._DurationMS = root.get('duration_ms', None)
            self._Explicit = root.get('explicit', None)
            self._Href = root.get('href', None)
            self._Id = root.get('id', None)
            self._IsPlayable = root.get('is_playable', None)
            self._IsLocal = root.get('is_local', None)
            self._Name = root.get('name', None)
            self._PreviewUrl = root.get('preview_url', None)
            self._TrackNumber = root.get('track_number', None)
            self._Type = root.get('type', None)
            self._Uri = root.get('uri', None)

            # process all collections and objects.
            items:list = root.get('artists',[])
            for item in items:
                self._Artists.append(ArtistSimplified(root=item))
        
            item:dict = root.get('external_urls',None)
            if item is not None:
                self._ExternalUrls = ExternalUrls(root=item)

            # item:dict = root.get('linked_from',None)
            # if item is not None:
            #     self._LinkedFrom = LinkedFrom(root=item)

            item:dict = root.get('restrictions',None)
            if item is not None:
                self._Restrictions = Restrictions(root=item)

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    # implement sorting support.
    def __eq__(self, other):
        try:
            return self.Name == other.Name
        except Exception as ex:
            if (isinstance(self, TrackSimplified )) and (isinstance(other, TrackSimplified )):
                return self.Name == other.Name
            return False

    def __lt__(self, other):
        try:
            return self.Name < other.Name
        except Exception as ex:
            if (isinstance(self, TrackSimplified )) and (isinstance(other, TrackSimplified )):
                return self.Name < other.Name
            return False


    @property
    def Artists(self) -> list[ArtistSimplified]:
        """ 
        A list of artists who performed the track. 
        """
        return self._Artists


    @property
    def AvailableMarkets(self) -> list[str]:
        """ 
        A list of the countries in which the track can be played, identified by their ISO 3166-1 alpha-2 code.
        """
        return self._AvailableMarkets


    @property
    def DiscNumber(self) -> int:
        """ 
        The disc number (usually 1 unless the album consists of more than one disc).
        """
        return self._DiscNumber


    @property
    def DurationMS(self) -> int:
        """ 
        The track length in milliseconds.
        """
        return self._DurationMS


    @property
    def Explicit(self) -> bool:
        """ 
        Whether or not the track has explicit lyrics (true = yes it does; false = no it does not OR unknown).
        """
        return self._Explicit


    @property
    def ExternalUrls(self) -> ExternalUrls:
        """ 
        Known external URLs for the track.
        """
        return self._ExternalUrls
    

    @property
    def Href(self) -> str:
        """ 
        A link to the Web API endpoint providing full details of the track.
        """
        return self._Href


    @property
    def Id(self) -> str:
        """ 
        The Spotify ID for the track.
        """
        return self._Id


    @property
    def IsLocal(self) -> bool:
        """ 
        Whether or not the track is from a local file.
        """
        return self._IsLocal


    @property
    def IsPlayable(self) -> bool:
        """ 
        Part of the response when Track Relinking is applied.  
        If true, the track is playable in the given market. Otherwise false.
        """
        return self._IsPlayable


    @property
    def Name(self) -> str:
        """ 
        The name of the artist.
        """
        return self._Name


    # @property
    # def LinkedFrom(self) -> object:
    #     """ 
    #     Part of the response when Track Relinking is applied, and the requested track has been replaced 
    #     with different track.  The track in the LinkedFrom object contains information about the originally 
    #     requested track.
    #     """
    #     return self._LinkedFrom


    @property
    def Name(self) -> str:
        """ 
        The name of the track.
        """
        return self._Name


    @property
    def PreviewUrl(self) -> str:
        """ 
        A link to a 30 second preview (MP3 format) of the track. Can be null.
        
        Important policy note:
        - Spotify Audio preview clips can not be a standalone service.
        """
        return self._PreviewUrl


    @property
    def Restrictions(self) -> Restrictions:
        """ 
        Included in the response when a content restriction is applied.
        """
        return self._Restrictions


    @property
    def TrackNumber(self) -> int:
        """ 
        The number of the track. 
        
        If an album has several discs, the track number is the number on the specified disc.
        """
        return self._TrackNumber


    @property
    def Type(self) -> str:
        """ 
        The object type: `track`.
        """
        return self._Type


    @property
    def Uri(self) -> str:
        """ 
        The Spotify URI for the track.
        """
        return self._Uri


    def ToString(self, includeTitle:bool=True) -> str:
        """
        Returns a displayable string representation of the class.
        
        Args:
            includeTitle (str):
                True to include the class name title prefix.
        """
        msg:str = ''
        if includeTitle: 
            msg = 'TrackSimplified:'
        
        if self._Name is not None: msg = '%s\n Name="%s"' % (msg, str(self._Name))
        if self._Uri is not None: msg = '%s\n Uri="%s"' % (msg, str(self._Uri))
        if self._Artists is not None: 
            cnt:int = len(self._Artists)
            if cnt > 0: 
                msg = '%s\n Artist="%s" (%s)' % (msg, str(self._Artists[0].Name), str(self._Artists[0].Id))
            msg = '%s\n Artists Count=%s' % (msg, str(cnt))
        if self._AvailableMarkets is not None: msg = '%s\n AvailableMarkets Count=%s' % (msg, str(len(self._AvailableMarkets)))
        if self._DiscNumber is not None: msg = '%s\n DiscNumber="%s"' % (msg, str(self._DiscNumber))
        if self._DurationMS is not None: msg = '%s\n DurationMS="%s"' % (msg, str(self._DurationMS))
        if self._Explicit is not None: msg = '%s\n Explicit="%s"' % (msg, str(self._Explicit))
        #if self._ExternalUrls is not None: msg = '%s\n %s' % (msg, str(self._ExternalUrls))
        if self._Href is not None: msg = '%s\n Href="%s"' % (msg, str(self._Href))
        if self._Id is not None: msg = '%s\n Id="%s"' % (msg, str(self._Id))
        if self._IsLocal is not None: msg = '%s\n IsLocal="%s"' % (msg, str(self._IsLocal))
        if self._IsPlayable is not None: msg = '%s\n IsPlayable="%s"' % (msg, str(self._IsPlayable))
        #if self._LinkedFrom is not None: msg = '%s\n LinkedFrom="%s"' % (msg, str(self._LinkedFrom))
        if self._PreviewUrl is not None: msg = '%s\n PreviewUrl="%s"' % (msg, str(self._PreviewUrl))
        #if self._Restrictions is not None: msg = '%s\n %s' % (msg, str(self._Restrictions))
        if self._TrackNumber is not None: msg = '%s\n TrackNumber="%s"' % (msg, str(self._TrackNumber))
        if self._Type is not None: msg = '%s\n Type="%s"' % (msg, str(self._Type))
        return msg 
