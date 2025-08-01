# external package imports.

# our package imports.
from ..sautils import export
from ..spotifymediatypes import SpotifyMediaTypes
from .context import Context
from .device import Device
from .episode import Episode
from .playeractions import PlayerActions
from .track import Track

@export
class PlayerPlayState:
    """
    Spotify Web API PlayerPlayState object.
    
    Information about the user's current playback state, including track or episode, 
    progress, and active device.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._Actions:PlayerActions = None
        self._Context:Context = None
        self._ItemType:str = None
        self._CurrentlyPlayingType:str = None
        self._Device:Device = None
        self._DeviceMusicSource:str = None
        self._Item:object = None
        self._IsDeviceState:bool = False
        self._IsPlaying:bool = None
        self._ProgressMS:int = None
        self._RepeatState:str = None
        self._ShuffleState:bool = None
        self._SmartShuffle:bool = None
        self._Timestamp:int = None

        # helper properties, not part of the Spotify Web API interface.
        self._IsEmpty:bool = True
        
        if (root is None):

            pass
        
        else:

            self._CurrentlyPlayingType = root.get('currently_playing_type', None)
            self._IsPlaying = root.get('is_playing', None)
            self._ProgressMS = root.get('progress_ms', None)
            self._RepeatState = root.get('repeat_state', None)
            self._ShuffleState = root.get('shuffle_state', None)
            self._SmartShuffle = root.get('smart_shuffle', None)
            self._Timestamp = root.get('timestamp', None)

            # process all collections and objects.
            item:dict = root.get('actions',None)
            if item is not None:
                disallows:dict = item.get('disallows')
                if disallows is not None:
                    self._Actions = PlayerActions(root=disallows)

            item:dict = root.get('context',None)
            if item is not None:
                self._Context = Context(root=item)

            item:dict = root.get('device',None)
            if item is not None:
                self._Device = Device(root=item)

            item:dict = root.get('item',None)
            if item is not None:
                if self._CurrentlyPlayingType == SpotifyMediaTypes.TRACK.value:
                    self._Item = Track(root=item)
                elif self._CurrentlyPlayingType == SpotifyMediaTypes.EPISODE.value:
                    self._Item = Episode(root=item)

            # if root contains keys, then assume it is NOT empty.
            if (len(root) > 0):
                self._IsEmpty = False

        # post load validations.
        if self._Actions is None:
            self._Actions = PlayerActions()
        if self._Device is None:
            self._Device = Device()
        if self._CurrentlyPlayingType is None:
            self._CurrentlyPlayingType = 'unknown'
        if self._IsPlaying is None:
            self._IsPlaying = False
        if self._ProgressMS is None:
            self._ProgressMS = 0
        if self._RepeatState is None:
            self._RepeatState = 'off'
        if self._ShuffleState is None:
            self._ShuffleState = False
        if self._SmartShuffle is None:
            self._SmartShuffle = False
        if self._Timestamp is None:
            self._Timestamp = 0


    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Actions(self) -> PlayerActions:
        """ 
        Allows to update the user interface based on which playback actions are 
        available within the current context.
        """
        return self._Actions


    @property
    def Context(self) -> Context:
        """ 
        A Context Object; can be null.
        """
        return self._Context
    

    @property
    def CurrentlyPlayingType(self) -> str:
        """ 
        The object type of the currently playing item, or null if nothing is playing.
        
        If not null, it can be one of `track`, `episode`, `ad` or `unknown`.
        """
        return self._CurrentlyPlayingType


    @property
    def Device(self) -> Device:
        """ 
        The device that is currently active.
        """
        return self._Device


    @property
    def DeviceMusicSource(self) -> str:
        """ 
        The device music source.
        This value is device manufacturer specific.
        For example, a Sonos source will contain values like "UNKNOWN", "SPOTIFY_CONNECT", etc.
        
        This is a helper property, and is not part of the Spotify Web API specification.
        """
        return self._DeviceMusicSource

    @DeviceMusicSource.setter
    def DeviceMusicSource(self, value:str):
        """ 
        Sets the DeviceMusicSource property value.
        """
        self._DeviceMusicSource = value


    @property
    def Item(self) -> object:
        """ 
        The currently playing track or episode; can be null.  
        
        Will be of type `Track`, `Episode`, or null.
        """
        return self._Item


    @property
    def ItemType(self) -> str:
        """ 
        The type of the currently playing episode; can be null.  
        This value will be null if the `Item` property value is null.
        
        If not null, it can be one of `audiobook` or `podcast`.
        
        Note that this is not a Spotify Web API property; it is loaded from our API so
        that the type of episode can be determined programatically (e.g. audiobook or podcast).
        """
        return self._ItemType

    @ItemType.setter
    def ItemType(self, value:str):
        """ 
        Sets the ItemType property value.
        """
        self._ItemType = value


    @property
    def IsAdvertisement(self) -> bool:
        """ 
        True if the currently playing media is an advertisement; otherwise, false.
        """
        if self._CurrentlyPlayingType == "ad":
            return True
        return False


    @property
    def IsDeviceState(self) -> bool:
        """ 
        True if playstate was built from a device playstate; 
        otherwise, false if playstate was built from a Spotify Web API playstate.
        """
        return self._IsDeviceState

    @IsDeviceState.setter
    def IsDeviceState(self, value:bool):
        """ 
        Sets the IsDeviceState property value.
        """
        if isinstance(value, bool):
            self._IsDeviceState = value


    @property
    def IsEmpty(self) -> bool:
        """ 
        True if Spotify playstate returned an empty response; otherwise, false.

        Note that for Sonos devices, the Spotify Web API reports an empty playstate since 
        the SoCo API is actually controlling player.

        This is a helper property, and is not part of the Spotify Web API specification.
        """
        return self._IsEmpty

    @IsEmpty.setter
    def IsEmpty(self, value:bool):
        """ 
        Sets the IsEmpty property value.
        """
        if isinstance(value, bool):
            self._IsEmpty = value


    @property
    def IsMuted(self) -> bool:
        """ 
        True if the player device volume is zero (muted) OR there is no device; 
        otherwise, false.
        """
        if self._Device is None:
            return True
        else:
            return self._Device.IsMuted


    @property
    def IsPlaying(self) -> bool:
        """ 
        True if something is currently playing; otherwise, false.
        """
        return self._IsPlaying

    @IsPlaying.setter
    def IsPlaying(self, value:bool):
        """ 
        Sets the IsPlaying property value.
        """
        if isinstance(value, bool):
            self._IsPlaying = value


    @property
    def IsRepeatEnabled(self) -> bool:
        """ 
        True if repeat play (one or all) is enabled; otherwise, False. 
        
        The `RepeatState` property contains the actual repeat setting.
        """
        if self._RepeatState != 'off': 
            return True
        return False


    @property
    def IsShuffleEnabled(self) -> bool:
        """ 
        True if shuffle play is enabled; otherwise, False. 
        """
        if (self.ShuffleState == 'on') or (self.ShuffleState == True):
            return True
        return False

    @IsShuffleEnabled.setter
    def IsShuffleEnabled(self, value:bool):
        """ 
        Sets the IsShuffleEnabled property value.
        """
        if isinstance(value, bool):
            self._ShuffleState = value


    @property
    def IsSmartShuffleEnabled(self) -> bool:
        """ 
        True if smart shuffle play is enabled; otherwise, False. 
        """
        if (self.SmartShuffle == 'on' or self.SmartShuffle == True):
            return True
        return False


    @property
    def ProgressMS(self) -> int:
        """ 
        Progress into the currently playing track or episode; can be null.
        """
        return self._ProgressMS

    @ProgressMS.setter
    def ProgressMS(self, value:int):
        """ 
        Sets the ProgressMS property value.
        """
        if isinstance(value, int):
            self._ProgressMS = value


    @property
    def RepeatState(self) -> str:
        """ 
        The repeat state of the playing track: `off`, `track`, or `context`.
        """
        return self._RepeatState


    @property
    def ShuffleState(self) -> bool:
        """ 
        If shuffle is enabled, True or False.
        """
        return self._ShuffleState


    @property
    def SmartShuffle(self) -> bool:
        """ 
        If smart shuffle is enabled, True or False.
        """
        return self._SmartShuffle


    @property
    def Summary(self) -> str:
        """ 
        Returns a summary of what is playing.
        """
        result:str = ''
        if self._Item is not None:
            
            if self._CurrentlyPlayingType == SpotifyMediaTypes.TRACK.value:
                track:Track = self._Item
                result = 'Track "%s" (%s)' % (track.Name, track.Id)
            elif self._CurrentlyPlayingType == SpotifyMediaTypes.EPISODE.value:
                episode:Episode = self._Item
                result = 'Episode "%s" (%s)' % (episode.Name, episode.Id)
            elif self._CurrentlyPlayingType == 'ad':
                result = 'Advertisement'
                
        elif self._CurrentlyPlayingType is None and self._Context is None:
            
            result = "unavailable"
            
        return result


    @property
    def Timestamp(self) -> int:
        """ 
        Unix Millisecond Timestamp when data was fetched.
        """
        return self._Timestamp

    @Timestamp.setter
    def Timestamp(self, value:int):
        """ 
        Sets the Timestamp property value.
        """
        if isinstance(value, int):
            self._Timestamp = value


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        actions:dict = {}
        if self._Actions is not None:
            actions = self._Actions.ToDictionary()
            
        context:dict = {}
        if self._Context is not None:
            context = self._Context.ToDictionary()
            
        device:dict = {}
        if self._Device is not None:
            device = self._Device.ToDictionary()
            
        item:dict = {}
        if self._Item is not None:
            item = self._Item.ToDictionary()
            
        result:dict = \
        {
            'is_empty': self._IsEmpty,
            'actions': actions,
            'context': context,
            'currently_playing_type': self._CurrentlyPlayingType,
            'device': device,
            'device_music_source': self._DeviceMusicSource,
            'is_device_state': self._IsDeviceState,
            'is_playing': self._IsPlaying,
            'progress_ms': self._ProgressMS,
            'repeat_state': self._RepeatState,
            'shuffle_state': self._ShuffleState,
            'smart_shuffle': self._SmartShuffle,
            'timestamp': self._Timestamp,
            'item_type': self._ItemType,
            'item': item,
        }
        return result
        

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'PlayerPlayState:'
        #if self._Actions is not None: msg = '%s\n %s' % (msg, str(self._Actions))
        if self._CurrentlyPlayingType is not None: msg = '%s\n CurrentlyPlayingType="%s"' % (msg, str(self._CurrentlyPlayingType))
        if self._ItemType is not None: msg = '%s\n ItemType="%s"' % (msg, str(self._ItemType))
        if self._Device is not None: msg = '%s\n Device Name="%s"' % (msg, str(self._Device.Name))
        if self._DeviceMusicSource is not None: msg = '%s\n DeviceMusicSource="%s"' % (msg, str(self._DeviceMusicSource))
        #if self._Context is not None: msg = '%s\n %s' % (msg, str(self._Context))
        #if self._Item is not None: msg = '%s\n %s' % (msg, str(self._Item))
        if self.IsMuted is not None: msg = '%s\n IsMuted="%s"' % (msg, str(self.IsMuted))
        if self._IsDeviceState is not None: msg = '%s\n IsDeviceState="%s"' % (msg, str(self._IsDeviceState))
        if self._IsPlaying is not None: msg = '%s\n IsPlaying="%s"' % (msg, str(self._IsPlaying))
        if self._ProgressMS is not None: msg = '%s\n ProgressMS="%s"' % (msg, str(self._ProgressMS))
        if self._RepeatState is not None: msg = '%s\n RepeatState="%s"' % (msg, str(self._RepeatState))
        if self._ShuffleState is not None: msg = '%s\n ShuffleState="%s"' % (msg, str(self._ShuffleState))
        if self._SmartShuffle is not None: msg = '%s\n SmartShuffle="%s"' % (msg, str(self._SmartShuffle))
        if self._Timestamp is not None: msg = '%s\n Timestamp="%s"' % (msg, str(self._Timestamp))
        msg = '%s\n IsEmpty="%s"' % (msg, str(self.IsEmpty))
        return msg 
