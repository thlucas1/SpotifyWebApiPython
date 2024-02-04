# external package imports.

# our package imports.
from ..sautils import export

@export
class Narrator:
    """
    Spotify Web API Content Narrator object.
    
    Contains information about content narrators.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._Name:str = None
        
        if (root is None):

            pass
        
        else:

            self._Name = root.get('name', None)


    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Name(self) -> str:
        """ 
        The narrator name for this content.
        """
        return self._Name
    

    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        result:dict = \
        {
            'name': self._Name,
        }
        return result
        

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'Narrator:'
        if self._Name is not None: msg = '%s\n Name="%s"' % (msg, str(self._Name))
        return msg 
