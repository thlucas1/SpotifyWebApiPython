# external package imports.

# our package imports.
from ..sautils import export
from .artistsimplified import ArtistSimplified
from .externalurls import ExternalUrls
from .imageobject import ImageObject
from .restrictions import Restrictions

@export
class AlbumSimplified:
    """
    Spotify Web API Simplified Album object.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._AlbumType:str = None
        self._Artists:list[ArtistSimplified] = []
        self._AvailableMarkets:list[str] = []
        self._ExternalUrls:ExternalUrls = None
        self._Href:str = None
        self._Id:str = None
        self._Images:list[ImageObject] = []
        self._Name:str = None
        self._ReleaseDate:str = None
        self._ReleaseDatePrecision:str = None
        self._Restrictions:Restrictions = None
        self._TotalTracks:int = None
        self._Type:str = None
        self._Uri:str = None
        
        if (root is None):

            pass
        
        else:

            self._AlbumType = root.get('album_type', None)
            self._AvailableMarkets = root.get('available_markets', None) or []
            self._Href = root.get('href', None)
            self._Id = root.get('id', None)
            self._Name = root.get('name', None)
            self._ReleaseDate = root.get('release_date', None)
            self._ReleaseDatePrecision = root.get('release_date_precision', None)
            self._TotalTracks = root.get('total_tracks', None)
            self._Type = root.get('type', None)
            self._Uri = root.get('uri', None)

            # process all collections and objects.
            items:list = root.get('artists',None)
            if items is not None:
                for item in items:
                    self._Artists.append(ArtistSimplified(root=item))

            item:dict = root.get('external_urls',None)
            if item is not None:
                self._ExternalUrls = ExternalUrls(root=item)

            items:list = root.get('images',None)
            if items is not None:
                for item in items:
                    self._Images.append(ImageObject(root=item))

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
        except Exception:
            if (isinstance(self, AlbumSimplified )) and (isinstance(other, AlbumSimplified )):
                return self.Name == other.Name
            return False

    def __lt__(self, other):
        try:
            return self.Name < other.Name
        except Exception:
            if (isinstance(self, AlbumSimplified )) and (isinstance(other, AlbumSimplified )):
                return self.Name < other.Name
            return False


    @property
    def AlbumType(self) -> str:
        """ 
        The type of the album.
        
        Allowed values: `album`, `single`, `compilation`.
        
        Example: `album`
        """
        return self._AlbumType


    @property
    def Artists(self) -> list[ArtistSimplified]:
        """ 
        The artists of the album.  
        
        Each artist object includes a link in href to more detailed information about the artist.
        """
        return self._Artists


    @property
    def AvailableMarkets(self) -> list[str]:
        """ 
        The markets in which the album is available: ISO 3166-1 alpha-2 country codes. 
        
        NOTE: an album is considered available in a market when at least 1 of its tracks is available in that market.
        
        Example: `["CA","BR","IT"]`
        """
        return self._AvailableMarkets


    @property
    def ExternalUrls(self) -> ExternalUrls:
        """ 
        Known external URLs for the album.
        """
        return self._ExternalUrls
    

    @property
    def Href(self) -> str:
        """ 
        A link to the Web API endpoint providing full details of the album.
        """
        return self._Href


    @property
    def Id(self) -> str:
        """ 
        The Spotify ID for the album.
        
        Example: `2up3OPMp9Tb4dAKM2erWXQ`
        """
        return self._Id


    @property
    def Images(self) -> list[ImageObject]:
        """ 
        The cover art for the album in various sizes, widest first.
        """
        return self._Images


    @property
    def ImageUrl(self) -> str:
        """
        Returns the highest resolution order image from the `Images` list, if images 
        are defined; otherwise, null.
        """
        return ImageObject.GetImageHighestResolution(self._Images)
            
        
    @property
    def Name(self) -> str:
        """ 
        The name of the album.  
        
        In case of an album takedown, the value may be an empty string.
        """
        return self._Name


    @property
    def ReleaseDate(self) -> str:
        """ 
        The date the album was first released.
        
        Example: `1981-12`
        """
        return self._ReleaseDate


    @property
    def ReleaseDatePrecision(self) -> str:
        """ 
        The precision with which release_date value is known.  
        Allowed values: `year`, `month`, `day`.  
        
        Example: `year`
        """
        return self._ReleaseDatePrecision


    @property
    def Restrictions(self) -> Restrictions:
        """ 
        Included in the response when a content restriction is applied.
        """
        return self._Restrictions


    @property
    def TotalTracks(self) -> int:
        """ 
        The number of tracks in the album.
        """
        return self._TotalTracks


    @property
    def Type(self) -> str:
        """ 
        The object type: `album`.
        """
        return self._Type


    @property
    def Uri(self) -> str:
        """ 
        The Spotify URI for the album.
        
        Example: `spotify:album:2up3OPMp9Tb4dAKM2erWXQ`
        """
        return self._Uri


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        externalUrls:dict = {}
        if self._ExternalUrls is not None:
            externalUrls = self._ExternalUrls.ToDictionary()

        restrictions:dict = {}
        if self._Restrictions is not None:
            restrictions = self._Restrictions.ToDictionary()

        result:dict = \
        {
            'album_type': self._AlbumType,
            'artists': [ item.ToDictionary() for item in self._Artists ],
            'available_markets': [ item for item in self._AvailableMarkets ],
            'external_urls': externalUrls,
            'href': self._Href,
            'id': self._Id,
            'image_url': self.ImageUrl,
            'images': [ item.ToDictionary() for item in self._Images ],
            'name': self._Name,
            'release_date': self._ReleaseDate,
            'release_date_precision': self._ReleaseDatePrecision,
            'restrictions': restrictions,
            'total_tracks': self._TotalTracks,
            'type': self._Type,
            'uri': self._Uri,           
        }
        return result
        

    def ToString(self, includeTitle:bool=True) -> str:
        """
        Returns a displayable string representation of the class.
        
        Args:
            includeTitle (str):
                True to include the class name title prefix.
        """
        msg:str = ''
        if includeTitle: 
            msg = 'AlbumSimplified:'
        
        if self._Name is not None: msg = '%s\n Name="%s"' % (msg, str(self._Name))
        if self._Uri is not None: msg = '%s\n Uri="%s"' % (msg, str(self._Uri))
        if self._AlbumType is not None: msg = '%s\n AlbumType="%s"' % (msg, str(self._AlbumType))
        if self._Artists is not None: 
            cnt:int = len(self._Artists)
            if cnt > 0: 
                msg = '%s\n Artist="%s" (%s)' % (msg, str(self._Artists[0].Name), str(self._Artists[0].Id))
            msg = '%s\n Artists Count=%s' % (msg, str(cnt))
        if self._AvailableMarkets is not None: msg = '%s\n AvailableMarkets Count=%s' % (msg, str(len(self._AvailableMarkets)))
        #if self._ExternalUrls is not None: msg = '%s\n %s' % (msg, str(self._ExternalUrls))
        if self._Href is not None: msg = '%s\n Href="%s"' % (msg, str(self._Href))
        if self._Id is not None: msg = '%s\n Id="%s"' % (msg, str(self._Id))
        if self._Images is not None: msg = '%s\n Images Count=%s' % (msg, str(len(self._Images)))
        if self._ReleaseDate is not None: msg = '%s\n ReleaseDate="%s"' % (msg, str(self._ReleaseDate))
        if self._ReleaseDatePrecision is not None: msg = '%s\n ReleaseDatePrecision="%s"' % (msg, str(self._ReleaseDatePrecision))
        #if self._Restrictions is not None: msg = '%s\n %s' % (msg, str(self._Restrictions))
        if self._TotalTracks is not None: msg = '%s\n TotalTracks="%s"' % (msg, str(self._TotalTracks))
        if self._Type is not None: msg = '%s\n Type="%s"' % (msg, str(self._Type))
        return msg
