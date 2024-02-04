# external package imports.

# our package imports.
from ..sautils import export

@export
class ImageObject:
    """
    Spotify Web API Image object.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._Height:int = None
        self._Url:str = None
        self._Width:int = None
        
        if (root is None):

            pass
        
        else:

            self._Height = root.get('height', None)
            self._Url = root.get('url', None)
            self._Width = root.get('width', None)

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Height(self) -> int:
        """ 
        The image height in pixels.
        
        Example: `300`
        """
        return self._Height


    @property
    def Url(self) -> str:
        """ 
        The source URL of the image.
        
        Example: `https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228`
        """
        return self._Url
    

    @property
    def Width(self) -> int:
        """ 
        The image width in pixels.
        
        Example: `300`
        """
        return self._Width


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        result:dict = \
        {
            'url': self._Url,
            'height': self._Height,
            'width': self._Width,
        }
        return result
        

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'ImageObject:'
        if self._Width is not None: msg = '%s\n Width="%s"' % (msg, str(self._Width))
        if self._Height is not None: msg = '%s\n Height="%s"' % (msg, str(self._Height))
        if self._Url is not None: msg = '%s\n Url="%s"' % (msg, str(self._Url))
        return msg 
