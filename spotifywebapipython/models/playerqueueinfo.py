# external package imports.

# our package imports.
from ..sautils import export
from .episode import Episode
from .track import Track

@export
class PlayerQueueInfo:
    """
    Spotify Web API PlayerQueueInfo object.
    
    Information about the user's current playback queue.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._CurrentlyPlaying:object = None
        self._CurrentlyPlayingType:str = None
        self._Queue:list[object] = []
        
        if (root is None):

            pass
        
        else:

            # process all collections and objects.
            item:dict = root.get('currently_playing',None)
            if item is not None:
                
                self._CurrentlyPlayingType = item.get('type','unknown')
                if self._CurrentlyPlayingType == 'track':
                    self._CurrentlyPlaying = Track(root=item)
                elif self._CurrentlyPlayingType == 'episode':
                    self._CurrentlyPlaying = Episode(root=item)

            items:list = root.get('queue',[])
            for item in items:
                itemType = item.get('type','unknown')
                if itemType == 'track':
                    self._Queue.append(Track(root=item))
                elif itemType == 'episode':
                    self._Queue.append(Episode(root=item))
        

    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def CurrentlyPlaying(self) -> object:
        """ 
        The currently playing track or episode; can be null.
        """
        return self._CurrentlyPlaying


    @property
    def CurrentlyPlayingType(self) -> str:
        """ 
        The object type of the currently playing item, or null if nothing is playing.
        
        If not null, it can be one of `track`, `episode`, `ad` or `unknown`.
        """
        return self._CurrentlyPlayingType


    @property
    def Queue(self) -> list[object]:
        """ 
        A Context Object; can be null.
        """
        return self._Queue
    

    @property
    def QueueCount(self) -> int:
        """ 
        The number of items in the `Queue` array.
        """
        if self._Queue is not None:
            return len(self._Queue)
        return 0
    

    @property
    def Summary(self) -> str:
        """ 
        Returns a summary of what is playing.
        """
        result:str = ''
        if self._CurrentlyPlaying is not None:
            
            if self._CurrentlyPlayingType == 'track':
                track:Track = self._CurrentlyPlaying
                result = 'Track "%s" (%s)' % (track.Name, track.Id)
            elif self._CurrentlyPlayingType == 'episode':
                episode:Episode = self._CurrentlyPlaying
                result = 'Episode "%s" (%s)' % (episode.Name, episode.Id)
            elif self._CurrentlyPlayingType == 'ad':
                result = 'Advertisement'
                
        elif self._CurrentlyPlayingType is None and self._Context is None:
            
            result = "unavailable"
            
        return result


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        currentlyPlaying:dict = {}
        if self._CurrentlyPlaying is not None:
            currentlyPlaying = self._CurrentlyPlaying.ToDictionary()
            
        result:dict = \
        {
            'currently_playing': currentlyPlaying,
            'currently_playing_type': self._CurrentlyPlayingType,
            'queue': [ item.ToDictionary() for item in self._Queue ],
        }
        return result
        

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'PlayerQueueInfo:'
        if self._CurrentlyPlayingType is not None: msg = '%s\n CurrentlyPlayingType="%s"' % (msg, str(self._CurrentlyPlayingType))
        if self.QueueCount is not None: msg = '%s\n QueueCount="%s"' % (msg, str(self.QueueCount))
        return msg 
