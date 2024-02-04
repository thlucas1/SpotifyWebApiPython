# external package imports.

# our package imports.
from ..sautils import export
from .explicitcontent import ExplicitContent
from .externalurls import ExternalUrls
from .followers import Followers
from .imageobject import ImageObject
from .userprofilesimplified import UserProfileSimplified

@export
class UserProfile(UserProfileSimplified):
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
        # initialize base class.
        super().__init__(root=root)
        
        # initialize storage.
        self._Country:str = None
        self._EMail:str = None
        self._ExplicitContent:ExplicitContent = None
        self._Product:str = None
        
        if (root is None):

            pass
        
        else:

            self._Country = root.get('country', None)
            self._EMail = root.get('email', None)
            self._Product = root.get('product', None)

            # process all collections and objects.
            item:dict = root.get('explicit_content',None)
            if item is not None:
                self._ExplicitContent = ExplicitContent(root=item)

        UNKNOWN:str = 'unknown'
        
        # post validations.
        # this is done, as some authorization levels will not return some of these details;
        # in this case, we will default the values to 'unknown'.
        if self._EMail is None:
            self._EMail = UNKNOWN
        if self._Product is None:
            self._Product = UNKNOWN


    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Country(self) -> str:
        """ 
        The country of the user, as set in the user's account profile. 
        
        An ISO 3166-1 alpha-2 country code. 
        
        This field is only available when the current user has granted access to 
        the `user-read-private` scope.
        
        Example: `US`
        """
        return self._Country


    @property
    def EMail(self) -> str:
        """ 
        The user's email address, as entered by the user when creating their account. 
        Important! This email address is unverified; there is no proof that it actually 
        belongs to the user. 
        
        This field is only available when the current user has granted access to 
        the `user-read-email` scope.
        
        Example: `johnsmith@example.com`
        """
        return self._EMail


    @property
    def ExplicitContent(self) -> ExternalUrls:
        """ 
        The user's explicit content settings. 
        
        This field is only available when the current user has granted access to 
        the `user-read-private` scope.
        """
        return self._ExplicitContent
    

    @property
    def Product(self) -> str:
        """ 
        The user's Spotify subscription level: `premium`, `free`, etc. 
        
        The subscription level `open` can be considered the same as `free`. 
        
        This field is only valid when the current user has granted access to 
        the `user-read-private` scope; otherwise, it is set to `unknown`.
        """
        return self._Product


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        # get base class result.
        resultBase:dict = super().ToDictionary()

        explicitContent:dict = {}
        if self._ExplicitContent is not None:
            explicitContent = self._ExplicitContent.ToDictionary()

        result:dict = \
        {
            'country': self._Country,
            'email': self._EMail,
            'explicitContent': explicitContent,
            'product': self._Product,
        }
        
        # combine base class results with these results.
        resultBase.update(result)
        
        # return a sorted dictionary.
        return dict(sorted(resultBase.items()))
        

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'UserProfile: %s' % super().ToString(False)
        if self._Country is not None: msg = '%s\n Country="%s"' % (msg, str(self._Country))
        if self._EMail is not None: msg = '%s\n EMail="%s"' % (msg, str(self._EMail))
        #if self._ExplicitContent is not None: msg = '%s\n %s' % (msg, str(self._ExplicitContent))
        if self._Product is not None: msg = '%s\n Product="%s"' % (msg, str(self._Product))
        return msg 
