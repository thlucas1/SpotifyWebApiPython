# external package imports.

# our package imports.
from ..sautils import export

@export
class Restrictions:
    """
    Spotify Web API Content Restrictions object.
    
    Contains information about content restrictions.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._Reason:str = None
        
        if (root is None):

            pass
        
        else:

            self._Reason = root.get('reason', None)


    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Reason(self) -> str:
        """ 
        The reason for the restriction. Supported values:  
        - market: The content item is not available in the given market.
        - product: The content item is not available for the user's subscription type.
        - explicit: The content item is explicit and the user's account is set to not play explicit content.
        
        Additional reasons may be added in the future.  
        
        Note: If you use this field, make sure that your application safely handles unknown values.
        """
        return self._Reason
    

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'Restrictions:'
        if self._Reason is not None: msg = '%s\n Reason="%s"' % (msg, str(self._Reason))
        return msg 
