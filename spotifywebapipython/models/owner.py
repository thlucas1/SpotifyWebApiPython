# external package imports.

# our package imports.
from ..sautils import export
from .externalurls import ExternalUrls
from .followers import Followers

@export
class Owner:
    """
    Spotify Web API Owner object.
    
    Information about the owner of an object (e.g. playlist, etc).
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._DisplayName:str = None
        self._ExternalUrls:ExternalUrls = None
        self._Followers:Followers = None
        self._Href:str = None
        self._Id:str = None
        self._Type:str = None
        self._Uri:str = None
        
        if (root is None):

            pass
        
        else:

            self._DisplayName = root.get('display_name', None)
            self._Href = root.get('href', None)
            self._Id = root.get('id', None)
            self._Type = root.get('type', None)
            self._Uri = root.get('uri', None)

            # process all collections and objects.
            item:dict = root.get('external_urls',None)
            if item is not None:
                self._ExternalUrls = ExternalUrls(root=item)

            item:dict = root.get('followers',None)
            if item is not None:
                self._Followers = Followers(root=item)
        

    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def DisplayName(self) -> str:
        """ 
        The name displayed on the user's profile, or null if not available.
        
        Example: `John S`
        """
        return self._DisplayName


    @property
    def ExternalUrls(self) -> ExternalUrls:
        """ 
        Known public external URLs for this user.
        """
        return self._ExternalUrls
    

    @property
    def Followers(self) -> Followers:
        """ 
        Information about the followers of the user.
        """
        return self._Followers


    @property
    def Href(self) -> str:
        """ 
        A link to the Web API endpoint providing full details of the user.
        """
        return self._Href


    @property
    def Id(self) -> str:
        """ 
        The Spotify user ID for the user.
        
        Example: `2up3OPMp9Tb4dAKM2erWXQ`
        """
        return self._Id


    @property
    def Type(self) -> str:
        """ 
        The object type: `user`.
        """
        return self._Type


    @property
    def Uri(self) -> str:
        """ 
        The Spotify URI for the user.
        
        Example: `spotify:user:2up3OPMp9Tb4dAKM2erWXQ`
        """
        return self._Uri


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        externalUrls:dict = {}
        if self._ExternalUrls is not None:
            externalUrls = self._ExternalUrls.ToDictionary()

        followers:dict = {}
        if self._Followers is not None:
            followers = self._Followers.ToDictionary()

        result:dict = \
        {
            'display_name': self._DisplayName,
            'external_urls': externalUrls,
            'followers': followers,
            'href': self._Href,
            'id': self._Id,
            'type': self._Type,
            'uri': self._Uri,
        }
        return result
        

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'UserProfile:'
        if self._DisplayName is not None: msg = '%s\n DisplayName="%s"' % (msg, str(self._DisplayName))
        if self._Uri is not None: msg = '%s\n Uri="%s"' % (msg, str(self._Uri))
        #if self._ExternalUrls is not None: msg = '%s\n %s' % (msg, str(self._ExternalUrls))
        #if self._Followers is not None: msg = '%s\n %s' % (msg, str(self._Followers))
        if self._Href is not None: msg = '%s\n Href="%s"' % (msg, str(self._Href))
        if self._Id is not None: msg = '%s\n Id="%s"' % (msg, str(self._Id))
        if self._Type is not None: msg = '%s\n Type="%s"' % (msg, str(self._Type))
        return msg 
