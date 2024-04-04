# external package imports.
from datetime import datetime

# our package imports.
from ..sautils import export

@export
class ArtistInfoTourEvent:
    """
    Artist Information Tour object.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        self._EventDateTime:str = None
        self._Title:str = None
        self._VenueName:str = None
        

    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def EventDateTime(self) -> datetime:
        """ 
        Date and time the tour event starts in the local timezone of the 
        venue location, if supplied; otherwise, null.
        """
        return self._EventDateTime
    
    @EventDateTime.setter
    def EventDateTime(self, value:datetime):
        """ 
        Sets the EventDateTime property value.
        """
        if value is None or isinstance(value, datetime):
            self._EventDateTime = value


    @property
    def Title(self) -> str:
        """ 
        Title given to the event by the promoter, if supplied; otherwise, null.
        """
        return self._Title
    
    @Title.setter
    def Title(self, value:str):
        """ 
        Sets the Title property value.
        """
        if isinstance(value, str):
            self._Title = value


    @property
    def VenueName(self) -> str:
        """ 
        The venue name of where the event will take place, if supplied; otherwise, null.
        """
        return self._VenueName
    
    @VenueName.setter
    def VenueName(self, value:str):
        """ 
        Sets the VenueName property value.
        """
        if isinstance(value, str):
            self._VenueName = value


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        result:dict = \
        {
            'event_datetime': self._EventDateTime.isoformat(),
            'title': self._Title,
            'venue_name': self._VenueName,
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
            msg = 'ArtistInfoTourEvent:'
        
        if self._EventDateTime is not None: msg = '%s\n EventDateTime="%s"' % (msg, self._EventDateTime.isoformat())
        if self._Title is not None: msg = '%s\n Title="%s"' % (msg, str(self._Title))
        if self._VenueName is not None: msg = '%s\n VenueName="%s"' % (msg, str(self._VenueName))
        return msg 
