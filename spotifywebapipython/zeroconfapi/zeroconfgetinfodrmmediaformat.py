# external package imports.

# our package imports.
from ..sautils import export

@export
class ZeroconfGetInfoDrmMediaFormat:
    """
    Spotify Zeroconf API GetInfo DRM Media Format object.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._Drm:int = None
        self._Formats:int = None
        
        if (root is None):

            pass
        
        else:

            self._Drm = root.get('drm', None)
            self._Formats = root.get('formats', None)

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Drm(self) -> int:
        """ 
        DRM format which the integration supports (SpDrmFormat).
        
        kSpDrmFormatUnknown	    Unknown DRM.
        kSpDrmFormatUnencrypted	No DRM, unencrypted.
        kSpDrmFormatFairPlay	FairPlay.
        kSpDrmFormatWidevine	Widevine.
        kSpDrmFormatPlayReady	PlayReady.        
        """
        return self._Drm


    @property
    def Formats(self) -> int:
        """ 
        Supported media formats for a DRM.
        """
        return self._Formats


    def ToDictionary(self) -> dict:
        """
        Returns a dictionary representation of the class.
        """
        result:dict = \
        {
            'Drm': self._Drm,
            'Formats': self._Formats,
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
            msg = 'ZeroconfGetInfoDrmMediaFormat:'
        
        if self._Drm is not None: msg = '%s\n Drm=%s' % (msg, str(self._Drm))
        if self._Formats is not None: msg = '%s\n Formats=%s' % (msg, str(self._Formats))
        return msg 
