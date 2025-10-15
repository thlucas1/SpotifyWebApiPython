# external package imports.

# our package imports.
from ..sautils import export
from .artistinfotourevent import ArtistInfoTourEvent
from .externalurls import ExternalUrls

@export
class ArtistInfo:
    """
    Artist Information About object.
    """

    def __init__(
        self, 
        id:str, 
        name:str, 
        typeValue:str, 
        uri:str, 
        imageUrlDefault:str, 
        externalUrls:ExternalUrls=None
        ) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            id (str):
                The Spotify ID for the artist.
            name (str):
                The name of the artist.
            typeValue (str):
                The object type.
            uri (str):
                The Spotify URI for the artist.
            imageUrlDefault (str):
                Image url of the artist, if defined.
            externalUrls (ExternalUrls):
                Known external URLs for this artist.
        """
        self._AboutUrlFacebook:str = None
        self._AboutUrlInstagram:str = None
        self._AboutUrlTwitter:str = None
        self._AboutUrlWikipedia:str = None
        self._Bio:str = None
        self._BioHtml:str = None
        self._ExternalUrls:ExternalUrls = externalUrls
        self._Id:int = id
        self._ImageUrl:str = None
        self._ImageUrlDefault:str = imageUrlDefault
        self._MonthlyListeners:int = None
        self._Name:str = name
        self._TourEvents:list[ArtistInfoTourEvent] = []
        self._Type:str = typeValue
        self._Uri:str = uri
        

    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def AboutUrlFacebook(self) -> str:
        """ 
        URL link to artist Facebook page, if supplied; otherwise, null.
        """
        return self._AboutUrlFacebook
    
    @AboutUrlFacebook.setter
    def AboutUrlFacebook(self, value:str):
        """ 
        Sets the AboutUrlFacebook property value.
        """
        if isinstance(value, str):
            self._AboutUrlFacebook = value


    @property
    def AboutUrlInstagram(self) -> str:
        """ 
        URL link to artist Instagram page, if supplied; otherwise, null.
        """
        return self._AboutUrlInstagram
    
    @AboutUrlInstagram.setter
    def AboutUrlInstagram(self, value:str):
        """ 
        Sets the AboutUrlInstagram property value.
        """
        if isinstance(value, str):
            self._AboutUrlInstagram = value


    @property
    def AboutUrlTwitter(self) -> str:
        """ 
        URL link to artist Twitter page, if supplied; otherwise, null.
        """
        return self._AboutUrlTwitter
    
    @AboutUrlTwitter.setter
    def AboutUrlTwitter(self, value:str):
        """ 
        Sets the AboutUrlTwitter property value.
        """
        if isinstance(value, str):
            self._AboutUrlTwitter = value


    @property
    def AboutUrlWikipedia(self) -> str:
        """ 
        URL link to artist Wikipedia page, if supplied; otherwise, null.
        """
        return self._AboutUrlWikipedia
    
    @AboutUrlWikipedia.setter
    def AboutUrlWikipedia(self, value:str):
        """ 
        Sets the AboutUrlWikipedia property value.
        """
        if isinstance(value, str):
            self._AboutUrlWikipedia = value


    @property
    def Bio(self) -> str:
        """ 
        Biography text, in plain-text format.
        """
        return self._Bio
    
    @Bio.setter
    def Bio(self, value:str):
        """ 
        Sets the Bio property value.
        """
        if isinstance(value, str):
            self._Bio = value


    @property
    def BioHtml(self) -> str:
        """ 
        Biography text, in html format.
        """
        return self._BioHtml
    
    @BioHtml.setter
    def BioHtml(self, value:str):
        """ 
        Sets the BioHtml property value.
        """
        if isinstance(value, str):
            self._BioHtml = value


    @property
    def ExternalUrls(self) -> list:
        """ 
        Known external URLs for this artist.
        """
        return self._ExternalUrls
    

    @property
    def Id(self) -> str:
        """ 
        The Spotify ID for the artist.
        """
        return self._Id


    @property
    def ImageUrl(self) -> str:
        """ 
        Image url of the artist, if defined; otheriwse, the `ImageUrlDefault` url value.
        """
        if (self._ImageUrl is not None) and (len(self._ImageUrl.strip()) > 0):
            return self._ImageUrl
        return self._ImageUrlDefault
    
    @ImageUrl.setter
    def ImageUrl(self, value:str):
        """ 
        Sets the ImageUrl property value.
        """
        if isinstance(value, str):
            self._ImageUrl = value


    @property
    def ImageUrlDefault(self) -> str:
        """ 
        Default Image url of the artist, if defined; otherwise, null.
        """
        return self._ImageUrlDefault
    

    @property
    def MonthlyListeners(self) -> int:
        """ 
        Monthly Listeners text.
        """
        return self._MonthlyListeners
    
    @MonthlyListeners.setter
    def MonthlyListeners(self, value:int):
        """ 
        Sets the MonthlyListeners property value.
        """
        if isinstance(value, int):
            self._MonthlyListeners = value


    @property
    def Name(self) -> str:
        """ 
        The name of the artist.
        """
        return self._Name


    @property
    def TourEvents(self) -> list[ArtistInfoTourEvent]:
        """ 
        An array of `ArtistInfoTourEvent` objects, if the artist has any upcoming tour
        dates on file; otherwise, an empty list.
        """
        return self._TourEvents
    

    @property
    def Type(self) -> str:
        """ 
        The object type: `artist`.
        """
        return self._Type


    @property
    def Uri(self) -> str:
        """ 
        The Spotify URI for the artist.
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
            'about_url_facebook': self._AboutUrlFacebook,
            'about_url_instagram': self._AboutUrlInstagram,
            'about_url_twitter': self._AboutUrlTwitter,
            'about_url_wikipedia': self._AboutUrlWikipedia,
            'bio': self._Bio,
            'bio_html': self._BioHtml,
            'external_urls': externalUrls,
            'id': self._Id,
            'image_url': self._ImageUrl,
            'image_url_default': self._ImageUrlDefault,
            'name': self._Name,
            'monthly_listeners': self._MonthlyListeners,
            'tour_events': [ item.ToDictionary() for item in self._TourEvents ],
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
            msg = 'ArtistInfo:'
        
        if self._Name is not None: msg = '%s\n Name="%s"' % (msg, str(self._Name))
        if self._Uri is not None: msg = '%s\n Uri="%s"' % (msg, str(self._Uri))
        if self._AboutUrlFacebook is not None: msg = '%s\n AboutUrlFacebook="%s"' % (msg, str(self._AboutUrlFacebook))
        if self._AboutUrlInstagram is not None: msg = '%s\n AboutUrlInstagram="%s"' % (msg, str(self._AboutUrlInstagram))
        if self._AboutUrlTwitter is not None: msg = '%s\n AboutUrlTwitter="%s"' % (msg, str(self._AboutUrlTwitter))
        if self._AboutUrlWikipedia is not None: msg = '%s\n AboutUrlWikipedia="%s"' % (msg, str(self._AboutUrlWikipedia))
        if self._Bio is not None: msg = '%s\n Bio="%s"' % (msg, str(self._Bio))
        if self._BioHtml is not None: msg = '%s\n BioHtml="%s"' % (msg, str(self._BioHtml))
        if self._ExternalUrls is not None: msg = '%s\n %s' % (msg, str(self._ExternalUrls))
        if self._Id is not None: msg = '%s\n Id="%s"' % (msg, str(self._Id))
        if self._ImageUrl is not None: msg = '%s\n ImageUrl="%s"' % (msg, str(self._ImageUrl))
        if self._ImageUrlDefault is not None: msg = '%s\n ImageUrlDefault="%s"' % (msg, str(self._ImageUrlDefault))
        if self._MonthlyListeners is not None: msg = '%s\n MonthlyListeners="%s"' % (msg, str(self._MonthlyListeners))
        msg = '%s\n TourEvents Count="%d"' % (msg, len(self._TourEvents))
        if self._Type is not None: msg = '%s\n Type="%s"' % (msg, str(self._Type))
        return msg 
