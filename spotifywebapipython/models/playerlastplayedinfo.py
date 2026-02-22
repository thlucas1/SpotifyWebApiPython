# external package imports.
import copy

# our package imports.
from ..sautils import export
from ..spotifymediatypes import SpotifyMediaTypes
from .context import Context
from .device import Device
from .episode import Episode
from .playerplaystate import PlayerPlayState
from .searchresultbase import SearchResultBase
from .track import Track

@export
class PlayerLastPlayedInfo:
    """
    Player Last Played Information object.

    Contains information about the content that was last playing on the Spotify Player,
    including context, item (track / episode), progress, and active device.

    This is a helper object, and is not part of the Spotify Web API specification.
    """

    def __init__(self, root:PlayerPlayState=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (PlayerPlayState):
                Spotify Web API PlayerPlayState object, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._Context:Context = None
        self._Device:Device = None
        self._DeviceMusicSource:str = None
        self._IsDeviceState:bool = False
        self._IsEmpty:bool = True
        self._Item:object = None
        self._ItemType:str = None
        self._ProgressMS:int = None
        self._RepeatState:str = None
        self._ShuffleState:bool = None
        self._Timestamp:int = None

        # is this a PlayerPlayState object? if not, then don't bother!
        if (isinstance(root, PlayerPlayState)):

            # deep copy the object
            rootCopy:PlayerPlayState = copy.deepcopy(root)

            # update individual properties.
            self._Context = rootCopy.Context
            self._Device = rootCopy.Device
            self._DeviceMusicSource = rootCopy.DeviceMusicSource
            self._IsDeviceState = rootCopy.IsDeviceState
            self._IsEmpty = rootCopy.IsEmpty
            self._Item = rootCopy.Item
            self._ItemType = rootCopy.ItemType
            self._ProgressMS = rootCopy.ProgressMS
            self._RepeatState = rootCopy.RepeatState
            self._ShuffleState = rootCopy.ShuffleState
            self._Timestamp = rootCopy.Timestamp

        # post load validations.
        # if self._Context is None:
        #     self._Context = Context()
        if self._Device is None:
            self._Device = Device()
        # if self._Item is None:
        #     self._Item = SearchResultBase()

        if self._ProgressMS is None:
            self._ProgressMS = 0
        if self._RepeatState is None:
            self._RepeatState = 'off'
        if self._ShuffleState is None:
            self._ShuffleState = False
        if self._Timestamp is None:
            self._Timestamp = 0


    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Context(self) -> Context:
        """ 
        A Context Object; can be null.
        """
        return self._Context
    

    @property
    def Device(self) -> Device:
        """ 
        The device that was active when the item was last playing.
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


    @property
    def IsAdvertisement(self) -> bool:
        """ 
        True if the item type is an advertisement; otherwise, false.
        """
        if self._Item:
            if self._Item.Type == "ad":
                return True
        return False


    @property
    def IsDeviceState(self) -> bool:
        """ 
        True if playstate was built from a device playstate; 
        otherwise, false if playstate was built from a Spotify Web API playstate.
        """
        return self._IsDeviceState

    @property
    def IsEmpty(self) -> bool:
        """ 
        True if Spotify playstate returned an empty response; otherwise, false.

        Note that for Sonos devices, the Spotify Web API reports an empty playstate since 
        the SoCo API is actually controlling player.

        This is a helper property, and is not part of the Spotify Web API specification.
        """
        return self._IsEmpty


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


    @property
    def Item(self) -> object:
        """ 
        The playing track or episode; can be null.  
        
        Will be of type `Track`, `Episode`, or null.
        """
        return self._Item


    @property
    def ItemType(self) -> str:
        """ 
        The type of the item playing; can be null.  
        This value will be null if the `Item` property value is null.
        
        If not null, it can be one of: `audiobook`, `podcast`, `track`.
        
        Note that this is not a Spotify Web API property; it is loaded from our API so
        that the type of episode can be determined programatically (e.g. audiobook or podcast).
        """
        return self._ItemType


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
    def Summary(self) -> str:
        """ 
        Returns a summary of what is playing.
        """
        result:str = ''
        if self._Item is None:

            result = "unavailable"
            
        else:
            
            if self._Item.Type == SpotifyMediaTypes.TRACK.value:
                track:Track = self._Item
                result = 'Track "%s" (%s)' % (track.Name, track.Id)
            elif self._Item.Type == SpotifyMediaTypes.EPISODE.value:
                episode:Episode = self._Item
                result = 'Episode "%s" (%s)' % (episode.Name, episode.Id)
            elif self._Item.Type == SpotifyMediaTypes.AUDIOBOOK.value:
                episode:Episode = self._Item
                result = 'Chapter "%s" (%s)' % (episode.Name, episode.Id)
            elif self._Item.Type == SpotifyMediaTypes.PODCAST.value:
                episode:Episode = self._Item
                result = 'Podcast "%s" (%s)' % (episode.Name, episode.Id)
                           
        return result


    @property
    def Timestamp(self) -> int:
        """ 
        Unix Millisecond Timestamp when data was fetched.
        """
        return self._Timestamp


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
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
            'is_empty': self.IsEmpty,
            'is_advertisement': self.IsAdvertisement,
            'is_muted': self.IsMuted,
            'is_repeat_enabled': self.IsRepeatEnabled,
            'is_shuffle_enabled': self.IsShuffleEnabled,
            'is_device_state': self.IsDeviceState,
            'progress_ms': self._ProgressMS,
            'repeat_state': self._RepeatState,
            'shuffle_state': self._ShuffleState,
            'timestamp': self._Timestamp,
            'item_type': self._ItemType,
            'item': item,
            'context': context,
            'device_music_source': self._DeviceMusicSource,
            'device': device,
        }
        return result
        

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'PlayerLastPlayedInfo:'
        if self._Device is not None: msg = '%s\n Device Name="%s"' % (msg, str(self._Device.Name))
        msg = '%s\n DeviceMusicSource="%s"' % (msg, str(self._DeviceMusicSource))
        msg = '%s\n IsEmpty="%s"' % (msg, str(self.IsEmpty))
        msg = '%s\n IsAdvertisement="%s"' % (msg, str(self.IsAdvertisement))
        msg = '%s\n IsDeviceState="%s"' % (msg, str(self.IsDeviceState))
        msg = '%s\n IsMuted="%s"' % (msg, str(self.IsMuted))
        msg = '%s\n IsRepeatEnabled="%s"' % (msg, str(self.IsRepeatEnabled))
        msg = '%s\n IsShuffleEnabled="%s"' % (msg, str(self.IsShuffleEnabled))
        msg = '%s\n ProgressMS="%s"' % (msg, str(self._ProgressMS))
        msg = '%s\n RepeatState="%s"' % (msg, str(self._RepeatState))
        msg = '%s\n ShuffleState="%s"' % (msg, str(self._ShuffleState))
        msg = '%s\n Timestamp="%s"' % (msg, str(self._Timestamp))
        msg = '%s\n ItemType="%s"' % (msg, str(self._ItemType))
        if self._Item is not None: msg = '%s\n %s' % (msg, self._Item.ToString())
        if self._Context is not None: msg = '%s\n %s' % (msg, self._Context.ToString())
        if self._Device is not None: msg = '%s\n %s' % (msg, self._Device.ToString())
        return msg 
