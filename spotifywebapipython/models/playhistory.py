# external package imports.
from datetime import datetime

# our package imports.
from ..sautils import export
from .context import Context
from .track import Track

@export
class PlayHistory:
    """
    Spotify Web API PlayHistory object.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._Context:Context = None
        self._PlayedAt:str = None
        self._PlayedAtMS:int = None
        self._Track:Track = None
        
        if (root is None):

            pass
        
        else:

            self._PlayedAt = root.get('played_at', None)

            # process all collections and objects.
            item:dict = root.get('context',None)
            if item is not None:
                self._Context = Context(root=item)

            item:dict = root.get('track',None)
            if item is not None:
                self._Track = Track(root=item)

        # convert played at local datetime to unix milliseconds timestamp.
        if self._PlayedAt is not None:
            dtLocalIso:str = self._PlayedAt.replace('Z','+00:00')
            dtLocal:str = datetime.fromisoformat(dtLocalIso)
            dtLocalUnixTS:float = dtLocal.timestamp()
            self._PlayedAtMS = int(dtLocalUnixTS * 1000)

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def PlayedAt(self) -> str:
        """ 
        The date and time the track was played (in local time).
        
        Example: `2024-01-25T15:33:17.136Z`
        """
        return self._PlayedAt


    @property
    def PlayedAtMS(self) -> int:
        """ 
        The `PlayedAt` value in Unix millisecond timestamp format, or null if the `PlayedAt` value is null.
        
        Example: `1706213826000`
        """
        return self._PlayedAtMS


    @property
    def Context(self) -> Context:
        """ 
        The context the track was played from.
        """
        return self._Context


    @property
    def Track(self) -> Track:
        """ 
        The track the user listened to.
        """
        return self._Track
    

    def ToString(self, includeItems:bool=False) -> str:
        """
        Returns a displayable string representation of the class.
        
        Args:
            includeItems (bool):
                True to include the Items collection of objects; otherwise, False
                to only return base properties.
        """
        msg:str = 'PlayHistory:'
        if self._PlayedAt is not None: msg = '%s\n PlayedAt="%s"' % (msg, str(self._PlayedAt))
        if self._Context is not None: msg = '%s\n Context="%s"' % (msg, str(self._Context.Uri))
        
        if (includeItems):
            if self._Track is not None: msg = '%s\n %s' % (msg, str(self._Track))
            
        return msg 
