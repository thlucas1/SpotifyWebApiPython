# external package imports.

# our package imports.
from ..sautils import export

@export
class ExternalIds:
    """
    Spotify Web API ExternalIds object.
    
    Contains known external ID's for various object types: artist, track, etc.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._Ean:str = None
        self._Isrc:str = None
        self._Upc:str = None
        
        if (root is None):

            pass
        
        else:

            self._Ean = root.get('ean', None)
            self._Isrc = root.get('isrc', None)
            self._Upc = root.get('upc', None)
            

    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Ean(self) -> str:
        """ 
        International Article Number.
        """
        return self._Ean
    

    @property
    def Isrc(self) -> str:
        """ 
        International Standard Recording Code.
        """
        return self._Isrc
    

    @property
    def Upc(self) -> str:
        """ 
        Universal Product Code.
        """
        return self._Upc
    

    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        result:dict = \
        {
            'ean': self._Ean,
            'isrc': self._Isrc,
            'upc': self._Upc,
        }
        return result
        

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'ExternalIds:'
        if self._Ean is not None: msg = '%s\n Ean="%s"' % (msg, str(self._Ean))
        if self._Isrc is not None: msg = '%s\n Isrc="%s"' % (msg, str(self._Isrc))
        if self._Upc is not None: msg = '%s\n Upc="%s"' % (msg, str(self._Upc))
        return msg 
