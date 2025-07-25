# external package imports.

# our package imports.
from ..sautils import export
from ..spotifymediatypes import SpotifyMediaTypes
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
        self._DateLastRefreshed:float = 0
        self._Queue:list[object] = []
        
        if (root is None):

            pass
        
        else:

            # process all collections and objects.
            item:dict = root.get('currently_playing',None)
            if item is not None:
                
                self._CurrentlyPlayingType = item.get('type','unknown')
                if self._CurrentlyPlayingType == SpotifyMediaTypes.TRACK.value:
                    self._CurrentlyPlaying = Track(root=item)
                elif self._CurrentlyPlayingType == SpotifyMediaTypes.EPISODE.value:
                    self._CurrentlyPlaying = Episode(root=item)

            # for some reason, the Spotify Web API will return up to 10 duplicate items 
            # with the same information!  for example:
            # - if there is only 1 item in the queue, then 10 duplicate items are returned by the Spotify Web API.
            # - if there are 5 items in the queue, then 5 duplicate items are returned by the Spotify Web API.
            # we will check for this scenario, and only return non-duplicate items if so.
            items:list = root.get('queue',None)
            if items is not None:
                for item in items:
                    
                    itemType = item.get('type','unknown')
                    if itemType == SpotifyMediaTypes.TRACK.value:
                        track:Track = Track(root=item)
                        if (track) and (not self.ContainsUri(track.Uri)):
                            self._Queue.append(track)
                    elif itemType == SpotifyMediaTypes.EPISODE.value:
                        episode:Episode = Episode(root=item)
                        if (episode) and (not self.ContainsUri(episode.Uri)):
                            self._Queue.append(episode)
                        

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
    def DateLastRefreshed(self) -> float:
        """ 
        Date and time items were was last refreshed, in unix epoch format (e.g. 1669123919.331225).
        A value of zero indicates the date was unknown.
        
        Note that this attribute does not exist in the Spotify Web API; 
        it was added here for convenience.
        """
        return self._DateLastRefreshed
    
    @DateLastRefreshed.setter
    def DateLastRefreshed(self, value:float):
        """ 
        Sets the DateLastRefreshed property value.
        """
        if (value is None):
            self._DateLastRefreshed = 0
        elif isinstance(value, float):
            self._DateLastRefreshed = value
        elif isinstance(value, int):
            self._DateLastRefreshed = float(value)


    @property
    def Queue(self) -> list[object]:
        """ 
        The tracks or episodes in the queue. Can be empty.
        
        Will be one of the following: `Track` or `Episode`
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
            
            if self._CurrentlyPlayingType == SpotifyMediaTypes.TRACK.value:
                track:Track = self._CurrentlyPlaying
                result = 'Track "%s" (%s)' % (track.Name, track.Id)
            elif self._CurrentlyPlayingType == SpotifyMediaTypes.EPISODE.value:
                episode:Episode = self._CurrentlyPlaying
                result = 'Episode "%s" (%s)' % (episode.Name, episode.Id)
            elif self._CurrentlyPlayingType == 'ad':
                result = 'Advertisement'
                
        elif self._CurrentlyPlayingType is None:
            
            result = 'unavailable'
            
        return result


    def ContainsUri(self, uri:str) -> bool:
        """
        Checks the `Queue` collection to see if an item already exists with the
        specified Uri value.
        
        Returns True if the specified Uri value exists in the collection; otherwise, False.
        """
        result:bool = False
        
        if (uri is None):
            return result
        
        for item in self._Queue:
            if item.Uri == uri:
                result = True
                break
            
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
            'date_last_refreshed': self._DateLastRefreshed,
            'currently_playing_type': self._CurrentlyPlayingType,
            'currently_playing': currentlyPlaying,
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
        msg = '%s\n DateLastRefreshed=%s' % (msg, str(self._DateLastRefreshed))
        return msg 
