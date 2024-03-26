# external package imports.

# our package imports.
from ..sautils import export

@export
class PlayerActions:
    """
    Spotify Web API PlayerActions object.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        # initialize storage.
        self._InterruptingPlayback:bool = None
        self._Pausing:bool = None
        self._Resuming:bool = None
        self._Seeking:bool = None
        self._SkippingNext:bool = None
        self._SkippingPrev:bool = None
        self._TogglingRepeatContext:bool = None
        self._TogglingRepeatTrack:bool = None
        self._TogglingShuffle:bool = None
        self._TransferringPlayback:bool = None
        
        if (root is None):

            pass
        
        else:

            self._InterruptingPlayback = root.get('interrupting_playback', None)
            self._Pausing = root.get('pausing', None)
            self._Resuming = root.get('resuming', None)
            self._Seeking = root.get('seeking', None)
            self._SkippingNext = root.get('skipping_next', None)
            self._SkippingPrev = root.get('skipping_prev', None)
            self._TogglingRepeatContext = root.get('toggling_repeat_context', None)
            self._TogglingRepeatTrack = root.get('toggling_shuffle', None)
            self._TogglingShuffle = root.get('toggling_repeat_track', None)
            self._TransferringPlayback = root.get('transferring_playback', None)

        # post load validations.
        if self._InterruptingPlayback is None:
            self._InterruptingPlayback = False
        if self._Pausing is None:
            self._Pausing = False
        if self._Resuming is None:
            self._Resuming = False
        if self._Seeking is None:
            self._Seeking = False
        if self._SkippingNext is None:
            self._SkippingNext = False
        if self._SkippingPrev is None:
            self._SkippingPrev = False
        if self._TogglingRepeatContext is None:
            self._TogglingRepeatContext = False
        if self._TogglingRepeatTrack is None:
            self._TogglingRepeatTrack = False
        if self._TogglingShuffle is None:
            self._TogglingShuffle = False
        if self._TransferringPlayback is None:
            self._TransferringPlayback = False


    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def InterruptingPlayback(self) -> bool:
        """ 
        Interrupting playback. Optional field.
        """
        return self._InterruptingPlayback


    @property
    def Pausing(self) -> bool:
        """ 
        Pausing. Optional field.
        """
        return self._Pausing


    @property
    def Resuming(self) -> bool:
        """ 
        Resuming. Optional field.
        """
        return self._Resuming


    @property
    def Seeking(self) -> bool:
        """ 
        Seeking playback location. Optional field.
        """
        return self._Seeking


    @property
    def SkippingNext(self) -> bool:
        """ 
        Skipping to the next context. Optional field.
        """
        return self._SkippingNext


    @property
    def SkippingPrev(self) -> bool:
        """ 
        Skipping to the previous context. Optional field.
        """
        return self._SkippingPrev


    @property
    def TogglingRepeatContext(self) -> bool:
        """ 
        Toggling repeat context flag. Optional field.
        """
        return self._TogglingRepeatContext


    @property
    def TogglingShuffle(self) -> bool:
        """ 
        Toggling shuffle flag. Optional field.
        """
        return self._TogglingShuffle


    @property
    def TogglingRepeatTrack(self) -> bool:
        """ 
        Toggling repeat track flag. Optional field.
        """
        return self._TogglingRepeatTrack


    @property
    def TransferringPlayback(self) -> bool:
        """ 
        Transfering playback between devices. Optional field.
        """
        return self._TransferringPlayback


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        result:dict = \
        {
            'interrupting_playback': self._InterruptingPlayback,
            'pausing': self._Pausing,
            'resuming': self._Resuming,
            'seeking': self._Seeking,
            'skipping_next': self._SkippingNext,
            'skipping_prev': self._SkippingPrev,
            'toggling_repeat_context': self._TogglingRepeatContext,
            'toggling_repeat_track': self._TogglingRepeatTrack,
            'toggling_shuffle': self._TogglingShuffle,
            'transferring_playback': self._TransferringPlayback,
        }
        return result
        

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'PlaybackActions:'
        if self._InterruptingPlayback is not None: msg = '%s\n InterruptingPlayback="%s"' % (msg, str(self._InterruptingPlayback))
        if self._Pausing is not None: msg = '%s\n Pausing="%s"' % (msg, str(self._Pausing))
        if self._Resuming is not None: msg = '%s\n Resuming="%s"' % (msg, str(self._Resuming))
        if self._Seeking is not None: msg = '%s\n Seeking="%s"' % (msg, str(self._Seeking))
        if self._SkippingNext is not None: msg = '%s\n SkippingNext="%s"' % (msg, str(self._SkippingNext))
        if self._SkippingPrev is not None: msg = '%s\n SkippingPrev="%s"' % (msg, str(self._SkippingPrev))
        if self._TogglingRepeatContext is not None: msg = '%s\n TogglingRepeatContext="%s"' % (msg, str(self._TogglingRepeatContext))
        if self._TogglingRepeatTrack is not None: msg = '%s\n TogglingRepeatTrack="%s"' % (msg, str(self._TogglingRepeatTrack))
        if self._TogglingShuffle is not None: msg = '%s\n TogglingShuffle="%s"' % (msg, str(self._TogglingShuffle))
        if self._TransferringPlayback is not None: msg = '%s\n TransferringPlayback="%s"' % (msg, str(self._TransferringPlayback))
        return msg 
