# external package imports.

# our package imports.
from ..sautils import export
from .copyright import Copyright
from .externalurls import ExternalUrls
from .imageobject import ImageObject

@export
class ShowSimplified:
    """
    Spotify Web API SimplifiedShow object.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._AvailableMarkets:list[str] = []
        self._Copyrights:list[Copyright] = []
        self._Description:str = None
        self._Explicit:bool = None
        self._ExternalUrls:ExternalUrls = None
        self._Href:str = None
        self._HtmlDescription:str = None
        self._Id:int = None
        self._Images:list[ImageObject] = []
        self._IsExternallyHosted:bool = None
        self._Languages:list[str] = []
        self._MediaType:str = None
        self._Name:str = None
        self._Publisher:str = None
        self._TotalEpisodes:int = None
        self._Type:str = None
        self._Uri:str = None
        
        if (root is None):

            pass
        
        else:

            self._AvailableMarkets = root.get('available_markets', None) or []
            self._Description = root.get('description', None)
            self._Explicit = root.get('explicit', None)
            self._Href = root.get('href', None)
            self._HtmlDescription = root.get('html_description', None)
            self._Id = root.get('id', None)
            self._IsExternallyHosted = root.get('is_externally_hosted', None)
            self._Languages = root.get('languages', None) or []
            self._MediaType = root.get('media_type', None)
            self._Name = root.get('name', None)
            self._Publisher = root.get('publisher', None)
            self._TotalEpisodes = root.get('total_episodes', None)
            self._Type = root.get('type', None)
            self._Uri = root.get('uri', None)

            # process all collections and objects.
            items:list = root.get('copyrights',None)
            if items is not None:
                for item in items:
                    self._Copyrights.append(Copyright(root=item))

            item:dict = root.get('external_urls',None)
            if item is not None:
                self._ExternalUrls = ExternalUrls(root=item)

            items:list = root.get('images',None)
            if items is not None:
                for item in items:
                    self._Images.append(ImageObject(root=item))

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    # implement sorting support.
    def __eq__(self, other):
        try:
            return self.Name == other.Name
        except Exception:
            if (isinstance(self, ShowSimplified )) and (isinstance(other, ShowSimplified )):
                return self.Name == other.Name
            return False

    def __lt__(self, other):
        try:
            return self.Name < other.Name
        except Exception:
            if (isinstance(self, ShowSimplified )) and (isinstance(other, ShowSimplified )):
                return self.Name < other.Name
            return False


    @property
    def AvailableMarkets(self) -> list[str]:
        """ 
        A list of the countries in which the show can be played, identified by their ISO 3166-1 alpha-2 code.
        """
        return self._AvailableMarkets


    @property
    def Copyrights(self) -> list[Copyright]:
        """ 
        The copyright statements of the show.
        """
        return self._Copyrights
    

    @property
    def Description(self) -> str:
        """ 
        A description of the show.  
        HTML tags are stripped away from this field, use `HtmlDescription` property in case HTML tags are needed.
        """
        return self._Description


    @property
    def Explicit(self) -> bool:
        """ 
        Whether or not the show has explicit lyrics (true = yes it does; false = no it does not OR unknown).
        """
        return self._Explicit


    @property
    def ExternalUrls(self) -> ExternalUrls:
        """ 
        Known external URLs for the show.
        """
        return self._ExternalUrls
    

    @property
    def Href(self) -> str:
        """ 
        A link to the Web API endpoint providing full details of the show.
        """
        return self._Href


    @property
    def HtmlDescription(self) -> str:
        """ 
        A description of the show.  
        This field may contain HTML tags.
        """
        return self._HtmlDescription


    @property
    def Id(self) -> str:
        """ 
        The Spotify ID for the show.
        """
        return self._Id


    @property
    def Images(self) -> list[ImageObject]:
        """ 
        The cover art for the show in various sizes, widest first.
        """
        return self._Images


    @property
    def ImageUrl(self) -> str:
        """
        Gets the first image url in the `Images` list, if images are defined;
        otherwise, null.
        """
        if len(self._Images) > 0:
            return self._Images[0].Url
        return None
            
        
    @property
    def IsExternallyHosted(self) -> bool:
        """ 
        True if all of the shows episodes are hosted outside of Spotify's CDN.  
        This field might be null in some cases.
        """
        return self._IsExternallyHosted


    @property
    def Languages(self) -> list[str]:
        """ 
        A list of the languages used in the show, identified by their ISO 639-1 code.
        
        Example: `[fr,en]`
        """
        return self._Languages


    @property
    def MediaType(self) -> str:
        """ 
        The media type of the show.
        """
        return self._MediaType


    @property
    def Name(self) -> str:
        """ 
        The name of the show.
        """
        return self._Name


    @property
    def Publisher(self) -> str:
        """ 
        The publisher of the show.
        """
        return self._Publisher


    @property
    def TotalEpisodes(self) -> int:
        """ 
        The total number of episodes in the show.
        """
        return self._TotalEpisodes


    @property
    def Type(self) -> str:
        """ 
        The object type: `show`.
        """
        return self._Type


    @property
    def Uri(self) -> str:
        """ 
        The Spotify URI for the show.
        """
        return self._Uri


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        externalUrls:dict = {}
        if self._ExternalUrls is not None:
            externalUrls = self._ExternalUrls.ToDictionary()

        result:dict = \
        {
            'available_markets': [ item for item in self._AvailableMarkets ],
            'copyrights': [ item.ToDictionary() for item in self._Copyrights ],
            'description': self._Description,
            'explicit': self._Explicit,
            'external_urls': externalUrls,
            'href': self._Href,
            'html_description': self._HtmlDescription,
            'id': self._Id,
            'images': [ item.ToDictionary() for item in self._Images ],
            'is_externally_hosted': self._IsExternallyHosted,
            'languages': [ item for item in self._Languages ],
            'media_type': self._MediaType,
            'name': self._Name,
            'publisher': self._Publisher,
            'total_episodes': self._TotalEpisodes,
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
            msg = 'ShowSimplified:'
        
        if self._Name is not None: msg = '%s\n Name="%s"' % (msg, str(self._Name))
        if self._Uri is not None: msg = '%s\n Uri="%s"' % (msg, str(self._Uri))
        if self._AvailableMarkets is not None: msg = '%s\n AvailableMarkets Count=%s' % (msg, str(len(self._AvailableMarkets)))
        #if self._Copyrights is not None: msg = '%s\n %s' % (msg, str(self._Copyrights))
        if self._Description is not None: msg = '%s\n Description="%s"' % (msg, str(self._Description))
        if self._Explicit is not None: msg = '%s\n Explicit="%s"' % (msg, str(self._Explicit))
        #if self._ExternalUrls is not None: msg = '%s\n %s' % (msg, str(self._ExternalUrls))
        if self._Href is not None: msg = '%s\n Href="%s"' % (msg, str(self._Href))
        if self._HtmlDescription is not None: msg = '%s\n HtmlDescription="%s"' % (msg, str(self._HtmlDescription))
        if self._Id is not None: msg = '%s\n Id="%s"' % (msg, str(self._Id))
        if self._Images is not None: msg = '%s\n Images Count=%s' % (msg, str(len(self._Images)))
        if self._IsExternallyHosted is not None: msg = '%s\n IsExternallyHosted="%s"' % (msg, str(self._IsExternallyHosted))
        if self._Languages is not None: msg = '%s\n Languages="%s"' % (msg, str(self._Languages))
        if self._MediaType is not None: msg = '%s\n MediaType="%s"' % (msg, str(self._MediaType))
        if self._Publisher is not None: msg = '%s\n Publisher="%s"' % (msg, str(self._Publisher))
        if self._TotalEpisodes is not None: msg = '%s\n TotalEpisodes="%s"' % (msg, str(self._TotalEpisodes))
        if self._Type is not None: msg = '%s\n Type="%s"' % (msg, str(self._Type))
        return msg 
