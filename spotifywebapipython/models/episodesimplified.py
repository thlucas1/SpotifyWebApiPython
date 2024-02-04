# external package imports.

# our package imports.
from ..sautils import export
from .externalurls import ExternalUrls
from .imageobject import ImageObject
from .restrictions import Restrictions
from .resumepoint import ResumePoint

@export
class EpisodeSimplified:
    """
    Spotify Web API Simplified Episode object.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._AudioPreviewUrl:str = None
        self._Description:str = None
        self._DurationMS:int = None
        self._Explicit:bool = None
        self._ExternalUrls:ExternalUrls = None
        self._Href:str = None
        self._HtmlDescription:str = None
        self._Id:str = None
        self._Images:list[ImageObject] = []
        self._IsExternallyHosted:bool = None
        self._IsPlayable:bool = None
        self._Languages:list[str] = []
        self._Name:str = None
        self._ReleaseDate:str = None
        self._ReleaseDatePrecision:str = None
        self._Restrictions:Restrictions = None
        self._ResumePoint:ResumePoint = None
        self._Type:str = None
        self._Uri:str = None

        if (root is None):

            pass
        
        else:

            self._AudioPreviewUrl = root.get('audio_preview_url', None)
            self._Description = root.get('description', None)
            self._DurationMS = root.get('duration_ms', None)
            self._Explicit = root.get('explicit', None)
            self._Href = root.get('href', None)
            self._HtmlDescription = root.get('html_description', None)
            self._Id = root.get('id', None)
            self._IsExternallyHosted = root.get('is_externally_hosted', None)
            self._IsPlayable = root.get('is_playable', None)
            self._Languages = root.get('languages', [])
            self._Name = root.get('name', None)
            self._ReleaseDate = root.get('release_date', None)
            self._ReleaseDatePrecision = root.get('release_date_precision', None)
            self._Type = root.get('type', None)
            self._Uri = root.get('uri', None)

            # process all collections and objects.
            item:dict = root.get('external_urls',None)
            if item is not None:
                self._ExternalUrls = ExternalUrls(root=item)

            items:list = root.get('images',[])
            for item in items:
                self._Images.append(ImageObject(root=item))

            item:dict = root.get('restrictions',None)
            if item is not None:
                self._Restrictions = Restrictions(root=item)

            item:dict = root.get('resume_point',None)
            if item is not None:
                self._ResumePoint = ResumePoint(root=item)

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    # implement sorting support.
    def __eq__(self, other):
        try:
            return self.Name == other.Name
        except Exception as ex:
            if (isinstance(self, EpisodeSimplified )) and (isinstance(other, EpisodeSimplified )):
                return self.Name == other.Name
            return False

    def __lt__(self, other):
        try:
            return self.Name < other.Name
        except Exception as ex:
            if (isinstance(self, EpisodeSimplified )) and (isinstance(other, EpisodeSimplified )):
                return self.Name < other.Name
            return False


    @property
    def AudioPreviewUrl(self) -> str:
        """ 
        A URL to a 30 second preview (MP3 format) of the episode, or null if not available.

        Important policy note:
        Spotify Audio preview clips can not be a standalone service.
        
        Example: `https://p.scdn.co/mp3-preview/2f37da1d4221f40b9d1a98cd191f4d6f1646ad17`
        """
        return self._AudioPreviewUrl


    @property
    def Description(self) -> str:
        """ 
        A description of the episode.  
        
        HTML tags are stripped away from this field, use html_description field in case HTML tags are needed.
        """
        return self._Description


    @property
    def DurationMS(self) -> int:
        """ 
        The episode length in milliseconds.
        
        Example: `1686230`
        """
        return self._DurationMS


    @property
    def Explicit(self) -> bool:
        """ 
        Whether or not the episode has explicit content (true = yes it does; false = no it does not OR unknown).
        """
        return self._Explicit


    @property
    def ExternalUrls(self) -> ExternalUrls:
        """ 
        Known external URLs for the album.
        """
        return self._ExternalUrls
    

    @property
    def Href(self) -> str:
        """ 
        A link to the Web API endpoint providing full details of the episode.
        
        Example: `https://api.spotify.com/v1/episodes/5Xt5DXGzch68nYYamXrNxZ`
        """
        return self._Href


    @property
    def HtmlDescription(self) -> str:
        """ 
        A description of the episode. This field may contain HTML tags.
        """
        return self._HtmlDescription


    @property
    def Id(self) -> str:
        """ 
        The Spotify ID for the episode.
        
        Example: `5Xt5DXGzch68nYYamXrNxZ`
        """
        return self._Id


    @property
    def Images(self) -> list[ImageObject]:
        """ 
        The cover art for the episode in various sizes, widest first.
        """
        return self._Images


    @property
    def IsExternallyHosted(self) -> bool:
        """ 
        True if the episode is hosted outside of Spotify's CDN.
        """
        return self._IsExternallyHosted


    @property
    def IsPlayable(self) -> bool:
        """ 
        True if the episode is playable in the given market. Otherwise false.
        """
        return self._IsPlayable


    @property
    def Languages(self) -> list[str]:
        """ 
        A list of the languages used in the episode, identified by their ISO 639-1 code.
        
        Example: `[fr,en]`
        """
        return self._Languages


    @property
    def Name(self) -> str:
        """ 
        The name of the episode.  
        """
        return self._Name


    @property
    def ReleaseDate(self) -> str:
        """ 
        The date the episode was first released.
        
        Example: `1981-12`  
        Depending on the precision, it might be shown as "1981" or "1981-12".
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
    def ResumePoint(self) -> ResumePoint:
        """ 
        The user's most recent position in the episode.  
        Set if the supplied access token is a user token and has the scope 'user-read-playback-position'.
        """
        return self._ResumePoint


    @property
    def Type(self) -> str:
        """ 
        The object type: `episode`.
        """
        return self._Type


    @property
    def Uri(self) -> str:
        """ 
        The Spotify URI for the episode.
        
        Example: `spotify:episode:0zLhl3WsOCQHbe1BPTiHgr`
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

        resumePoint:dict = {}
        if self._ResumePoint is not None:
            resumePoint = self._ResumePoint.ToDictionary()

        result:dict = \
        {
            'audio_preview_url': self._AudioPreviewUrl,
            'description': self._Description,
            'duration_ms': self._DurationMS,
            'explicit': self._Explicit,
            'external_urls': externalUrls,
            'href': self._Href,
            'html_description': self._HtmlDescription,
            'id': self._Id,
            'images': [ item.ToDictionary() for item in self._Images ],
            'is_externally_hosted': self._IsExternallyHosted,
            'is_playable': self._IsPlayable,
            'languages': [ item for item in self._Languages ],
            'name': self._Name,
            'release_date': self._ReleaseDate,
            'release_date_precision': self._ReleaseDatePrecision,
            'restrictions': restrictions,
            'resume_point': resumePoint,
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
            msg = 'EpisodeSimplified:'
        
        if self._Name is not None: msg = '%s\n Name="%s"' % (msg, str(self._Name))
        if self._Uri is not None: msg = '%s\n Uri="%s"' % (msg, str(self._Uri))
        if self._AudioPreviewUrl is not None: msg = '%s\n AudioPreviewUrl="%s"' % (msg, str(self._AudioPreviewUrl))
        if self._Description is not None: msg = '%s\n Description="%s"' % (msg, str(self._Description))
        if self._DurationMS is not None: msg = '%s\n DurationMS="%s"' % (msg, str(self._DurationMS))
        if self._Explicit is not None: msg = '%s\n Explicit="%s"' % (msg, str(self._Explicit))
        #if self._ExternalUrls is not None: msg = '%s\n %s' % (msg, str(self._ExternalUrls))
        if self._Href is not None: msg = '%s\n Href="%s"' % (msg, str(self._Href))
        if self._HtmlDescription is not None: msg = '%s\n HtmlDescription="%s"' % (msg, str(self._HtmlDescription))
        if self._Id is not None: msg = '%s\n Id="%s"' % (msg, str(self._Id))
        if self._Images is not None: msg = '%s\n Images Count=%s' % (msg, str(len(self._Images)))
        if self._IsExternallyHosted is not None: msg = '%s\n IsExternallyHosted="%s"' % (msg, str(self._IsExternallyHosted))
        if self._IsPlayable is not None: msg = '%s\n IsPlayable="%s"' % (msg, str(self._IsPlayable))
        if self._Languages is not None: msg = '%s\n Languages Count=%s' % (msg, str(len(self._Languages)))
        if self._ReleaseDate is not None: msg = '%s\n ReleaseDate="%s"' % (msg, str(self._ReleaseDate))
        if self._ReleaseDatePrecision is not None: msg = '%s\n ReleaseDatePrecision="%s"' % (msg, str(self._ReleaseDatePrecision))
        if self._Restrictions is not None: msg = '%s\n %s' % (msg, str(self._Restrictions))
        if self._ResumePoint is not None: msg = '%s\n %s' % (msg, str(self._ResumePoint))
        if self._Type is not None: msg = '%s\n Type="%s"' % (msg, str(self._Type))
        return msg
