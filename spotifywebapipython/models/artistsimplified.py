# external package imports.

# our package imports.
from ..sautils import export
from .externalurls import ExternalUrls

@export
class ArtistSimplified:
    """
    Spotify Web API SimplifiedArtist object.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._ExternalUrls:ExternalUrls = None
        self._Href:str = None
        self._Id:int = None
        self._Name:str = None
        self._Type:str = None
        self._Uri:str = None
        
        if (root is None):

            pass
        
        else:

            self._Href = root.get('href', None)
            self._Id = root.get('id', None)
            self._Name = root.get('name', None)
            self._Type = root.get('type', None)
            self._Uri = root.get('uri', None)

            # process all collections and objects.
            item:dict = root.get('external_urls',None)
            if item is not None:
                self._ExternalUrls = ExternalUrls(root=item)

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    # implement sorting support.
    def __eq__(self, other):
        try:
            return self.Name == other.Name
        except Exception as ex:
            if (isinstance(self, ArtistSimplified )) and (isinstance(other, ArtistSimplified )):
                return self.Name == other.Name
            return False

    def __lt__(self, other):
        try:
            return self.Name < other.Name
        except Exception as ex:
            if (isinstance(self, ArtistSimplified )) and (isinstance(other, ArtistSimplified )):
                return self.Name < other.Name
            return False


    @property
    def ExternalUrls(self) -> list:
        """ 
        Known external URLs for this artist.
        """
        return self._ExternalUrls
    

    @property
    def Href(self) -> str:
        """ 
        A link to the Web API endpoint providing full details of the artist.
        """
        return self._Href


    @property
    def Id(self) -> str:
        """ 
        The Spotify ID for the artist.
        """
        return self._Id


    @property
    def Name(self) -> str:
        """ 
        The name of the artist.
        """
        return self._Name


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
            'external_urls': externalUrls,
            'href': self._Href,
            'id': self._Id,
            'name': self._Name,
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
            msg = 'Artist:'
        
        if self._Name is not None: msg = '%s\n Name="%s"' % (msg, str(self._Name))
        if self._Uri is not None: msg = '%s\n Uri="%s"' % (msg, str(self._Uri))
        if self._ExternalUrls is not None: msg = '%s\n %s' % (msg, str(self._ExternalUrls))
        if self._Href is not None: msg = '%s\n Href="%s"' % (msg, str(self._Href))
        if self._Id is not None: msg = '%s\n Id="%s"' % (msg, str(self._Id))
        if self._Type is not None: msg = '%s\n Type="%s"' % (msg, str(self._Type))
        return msg 
