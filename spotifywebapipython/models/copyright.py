# external package imports.

# our package imports.
from ..sautils import export

@export
class Copyright:
    """
    Spotify Web API Content Copyright object.
    
    Contains information about content copyrights.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._Text:str = None
        self._Type:str = None
        
        if (root is None):

            pass
        
        else:

            self._Text = root.get('text', None)
            self._Type = root.get('type', None)


    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Text(self) -> str:
        """ 
        The copyright text for this content.
        """
        return self._Text
    

    @property
    def Type(self) -> str:
        """ 
        The type of copyright: C = the copyright, P = the sound recording (performance) copyright.
        """
        return self._Type


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        result:dict = \
        {
            'text': self._Text,
            'type': self._Type
        }
        return result
        

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'Copyright:'
        if self._Type is not None: msg = '%s\n Type="%s"' % (msg, str(self._Type))
        if self._Text is not None: msg = '%s\n Text="%s"' % (msg, str(self._Text))
        return msg 
