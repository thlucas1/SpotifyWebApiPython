# external package imports.

# our package imports.
from ..sautils import export
from .externalurls import ExternalUrls

@export
class Context:
    """
    Spotify Web API Context object.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        # initialize storage.
        self._ExternalUrls:ExternalUrls = None
        self._Href:str = None
        self._Type:str = None
        self._Uri:str = None
        
        if (root is None):

            pass
        
        else:

            self._Href = root.get('href', None)
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


    @property
    def ExternalUrls(self) -> ExternalUrls:
        """ 
        External URLs for this context.
        """
        return self._ExternalUrls
    

    @property
    def Href(self) -> str:
        """ 
        A link to the Web API endpoint providing full details of the track.
        """
        return self._Href


    @property
    def Type(self) -> str:
        """ 
        Object type, such as `artist`, `playlist`, `album` or `show`.
        
        Example: `computer`
        """
        return self._Type


    @property
    def Uri(self) -> str:
        """ 
        The Spotify URI for the context.
        
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

        result:dict = \
        {
            'external_urls': externalUrls,
            'href': self._Href,
            'type': self._Type,
            'uri': self._Uri,           
        }
        return result
        

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'Context:'
        if self._Uri is not None: msg = '%s\n Uri="%s"' % (msg, str(self._Uri))
        #if self._ExternalUrls is not None: msg = '%s\n %s' % (msg, str(self._ExternalUrls))
        if self._Href is not None: msg = '%s\n Href="%s"' % (msg, str(self._Href))
        if self._Type is not None: msg = '%s\n Type="%s"' % (msg, str(self._Type))
        return msg 
