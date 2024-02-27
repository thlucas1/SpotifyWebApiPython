# external package imports.

# our package imports.
from ..sautils import export
from .explicitcontent import ExplicitContent
from .externalurls import ExternalUrls
from .followers import Followers
from .imageobject import ImageObject

@export
class UserProfileSimplified:
    """
    Spotify Web API User Profile object.
    
    Information about the user from their account profile.
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
        self._Images:list[ImageObject] = []
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
        
            items:list = root.get('images',None)
            if items is not None:
                for item in items:
                    self._Images.append(ImageObject(root=item))

        UNKNOWN:str = 'unknown'
        
        # post validations.
        # this is done, as some authorization levels will not return some of these details;
        if self._DisplayName is None or len(self._DisplayName.strip()) == 0:
            self._DisplayName = self._Id
        if self._Type is None or len(self._Type.strip()) == 0:
            self._Type = 'user'


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
        Known external URLs for this user.
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
    def Images(self) -> list[ImageObject]:
        """ 
        The user's profile image.
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
            'images': [ item.ToDictionary() for item in self._Images ],
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
            msg = 'UserProfileSimplified:'
        
        if self._DisplayName is not None: msg = '%s\n DisplayName="%s"' % (msg, str(self._DisplayName))
        if self._Uri is not None: msg = '%s\n Uri="%s"' % (msg, str(self._Uri))
        #if self._ExternalUrls is not None: msg = '%s\n %s' % (msg, str(self._ExternalUrls))
        if self._Followers is not None: msg = '%s\n Followers Count=%s' % (msg, str(self._Followers.Total))
        if self._Href is not None: msg = '%s\n Href="%s"' % (msg, str(self._Href))
        if self._Id is not None: msg = '%s\n Id="%s"' % (msg, str(self._Id))
        if self._Images is not None: msg = '%s\n Images Count=%s' % (msg, str(len(self._Images)))
        if self._Type is not None: msg = '%s\n Type="%s"' % (msg, str(self._Type))
        return msg 
