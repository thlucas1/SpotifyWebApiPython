# external package imports.

# our package imports.
from ..sautils import export

@export
class ZeroconfGetInfoAlias:
    """
    Spotify Zeroconf API GetInfo Alias object.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._Id:str = None
        self._IsGroup:bool = None
        self._Name:str = None
        
        if (root is None):

            pass
        
        else:

            self._Id = root.get('id', None)
            self._IsGroup = root.get('isGroup', None)
            self._Name = root.get('name', None)

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Id(self) -> str:
        """ 
        Unique identifier of the alias.
        """
        return self._Id


    @property
    def IsGroup(self) -> bool:
        """ 
        True if the alias is a group; otherwise, False.
        """
        return self._IsGroup


    @property
    def Name(self) -> str:
        """ 
        Display name of the alias.
        """
        return self._Name


    @property
    def Title(self) -> str:
        """ 
        Alias name and id value (e.g. '"Bose-ST10-1" (30fbc80e35598f3c242f2120413c943dfd9715fe)').
        """
        return '"%s" (%s)' & (self._Name, self._Id)
    

    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        result:dict = \
        {
            'Id': self._Id,
            'IsGroup': self._IsGroup,
            'Name': self._Name,
        }
        return result
        

    def ToString(self, includeTitle:bool=False) -> str:
        """
        Returns a displayable string representation of the class.
        
        Args:
            includeTitle (str):
                True to include the class name title prefix.
        """
        msg:str = ''
        if includeTitle: 
            msg = 'ZeroconfGetInfoAlias:'
        
        if self._Name is not None: msg = '%s\n Name="%s"' % (msg, str(self._Name))
        if self._Id is not None: msg = '%s\n Id="%s"' % (msg, str(self._Id))
        if self._IsGroup is not None: msg = '%s\n IsGroup="%s"' % (msg, str(self._IsGroup))
        return msg 
