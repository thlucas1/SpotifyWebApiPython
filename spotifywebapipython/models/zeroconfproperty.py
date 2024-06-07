# external package imports.

# our package imports.
from ..sautils import export

@export
class ZeroconfProperty:
    """
    Zeroconf Property object.
    
    Information about a Zeroconf property.
    """

    def __init__(self, name:str, value:str) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            name (str):
                Property name.
            value (str):
                Property value.
        """
        self._Name:str = name
        self._Value:str = value
        
        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Name(self) -> str:
        """ 
        Property name.
        """
        return self._Name
    
    @Name.setter
    def Name(self, value:str):
        """ 
        Sets the Name property value.
        """
        if isinstance(value, str):
            self._Name = value


    @property
    def Value(self) -> str:
        """ 
        Property value.
        """
        return self._Value
    
    @Value.setter
    def Value(self, value:str):
        """ 
        Sets the Value property value.
        """
        self._Value = value


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        result:dict = \
        {
            'Name': self._Name,
            'Value': self._Value,
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
            msg = 'ZeroconfProperty:'
        
        if self._Name is not None: msg = '%s\n Name="%s"' % (msg, str(self._Name))
        if self._Value is not None: msg = '%s\n Value="%s"' % (msg, str(self._Value))
        return msg 
