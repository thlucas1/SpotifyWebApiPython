# external package imports.

# our package imports.
from ..sautils import export

@export
class AudioFeatures:
    """
    Spotify Web API AudioFeatures object.
    """

    def __init__(self, root:dict=None) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            root (dict):
                Spotify Web API JSON response in dictionary format, used to load object
                attributes; otherwise, None to not load attributes.
        """
        self._Acousticness:float = None
        self._AnalysisUrl:str = None
        self._Danceability:float = None
        self._DurationMS:int = None
        self._Energy:float = None
        self._Id:str = None
        self._Instrumentalness:float = None
        self._Key:int = None
        self._Liveness:float = None
        self._Loudness:float = None
        self._Mode:int = None
        self._Speechiness:float = None
        self._Tempo:float = None
        self._TimeSignature:int = None
        self._TrackHref:str = None
        self._Type:str = None
        self._Uri:str = None
        self._Valence:float = None
        
        if (root is None):

            pass
        
        else:

            self._Acousticness = root.get('acousticness', None)
            self._AnalysisUrl = root.get('analysis_url', None)
            self._Danceability = root.get('danceability', None)
            self._DurationMS = root.get('duration_ms', None)
            self._Energy = root.get('energy', None)
            self._Id = root.get('id', None)
            self._Instrumentalness = root.get('instrumentalness', None)
            self._Key = root.get('key', None)
            self._Liveness = root.get('liveness', None)
            self._Loudness = root.get('loudness', None)
            self._Mode = root.get('mode', None)
            self._Speechiness = root.get('speechiness', None)
            self._Tempo = root.get('tempo', None)
            self._TimeSignature = root.get('time_signature', None)
            self._TrackHref = root.get('track_href', None)
            self._Type = root.get('type', None)
            self._Uri = root.get('uri', None)
            self._Valence = root.get('valence', None)

        
    def __repr__(self) -> str:
        return self.ToString()


    def __str__(self) -> str:
        return self.ToString()


    @property
    def Acousticness(self) -> float:
        """ 
        A confidence measure from 0.0 to 1.0 of whether the track is acoustic.  
        1.0 represents high confidence the track is acoustic.  
        Example: `0.00242`
        """
        return self._Acousticness
    

    @property
    def AnalysisUrl(self) -> str:
        """ 
        A URL to access the full audio analysis of this track.  
        An access token is required to access this data.  
        Example: `https://api.spotify.com/v1/audio-analysis/2takcwOaAZWiXQijPHIx7B`
        """
        return self._AnalysisUrl
    

    @property
    def Danceability(self) -> float:
        """ 
        Danceability describes how suitable a track is for dancing based on a combination of musical 
        elements including tempo, rhythm stability, beat strength, and overall regularity.  
        A value of 0.0 is least danceable and 1.0 is most danceable.
        Example: `0.585`
        """
        return self._Danceability
    

    @property
    def DurationMS(self) -> int:
        """ 
        The duration of the track in milliseconds.  
        Example: `237040`
        """
        return self._DurationMS
    

    @property
    def Energy(self) -> float:
        """ 
        Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity.   
        Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, 
        while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute 
        include dynamic range, perceived loudness, timbre, onset rate, and general entropy.  
        Example: `0.842`
        """
        return self._Energy
    

    @property
    def Id(self) -> int:
        """ 
        The Spotify ID for the track.  
        Example: `2takcwOaAZWiXQijPHIx7B`
        """
        return self._Id
    

    @property
    def Instrumentalness(self) -> float:
        """ 
        Predicts whether a track contains no vocals.   
        "Ooh" and "aah" sounds are treated as instrumental in this context. Rap or spoken word 
        tracks are clearly "vocal". The closer the instrumentalness value is to 1.0, the greater 
        likelihood the track contains no vocal content. Values above 0.5 are intended to represent 
        instrumental tracks, but confidence is higher as the value approaches 1.0.  
        Example: `0.00686`
        """
        return self._Instrumentalness
    

    @property
    def Key(self) -> int:
        """ 
        The key the track is in.  
        
        Integers map to pitches using standard Pitch Class notation (e.g. 0 = C, 1 = C#, 
        2 = D, and so on).  If no key was detected, the value is -1.  
        
        Range: `-1` to `11`  
        Example: `9`
        """
        return self._Key
    

    @property
    def Liveness(self) -> float:
        """ 
        Detects the presence of an audience in the recording.  Higher liveness values represent 
        an increased probability that the track was performed live. A value above 0.8 provides 
        strong likelihood that the track is live.
        
        Example: `0.0866`
        """
        return self._Liveness
    

    @property
    def Loudness(self) -> float:
        """ 
        The overall loudness of a track in decibels (dB).  
        
        Loudness values are averaged across the entire track and are useful for comparing relative 
        loudness of tracks. Loudness is the quality of a sound that is the primary psychological 
        correlate of physical strength (amplitude). Values typically range between -60 and 0 db.  
        
        Example: `-5.883`
        """
        return self._Loudness
    

    @property
    def Mode(self) -> int:
        """ 
        Mode indicates the modality (major or minor) of a track, the type of scale from which its 
        melodic content is derived. Major is represented by 1 and minor is 0.  
        
        Example: `0`
        """
        return self._Mode
    

    @property
    def Speechiness(self) -> float:
        """ 
        Speechiness detects the presence of spoken words in a track. The more exclusively speech-like 
        the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. 
        Values above 0.66 describe tracks that are probably made entirely of spoken words.  
        Values between 0.33 and 0.66 describe tracks that may contain both music and speech, either 
        in sections or layered, including such cases as rap music. Values below 0.33 most likely 
        represent music and other non-speech-like tracks.
        
        Example: `0.0556`
        """
        return self._Speechiness
    

    @property
    def Tempo(self) -> float:
        """ 
        The overall estimated tempo of a track in beats per minute (BPM).  
        
        In musical terminology, tempo is the speed or pace of a given piece and derives directly 
        from the average beat duration.
        
        Example: `118.211`
        """
        return self._Tempo
    

    @property
    def TimeSignature(self) -> int:
        """ 
        An estimated time signature.  
        
        The time signature (meter) is a notational convention to specify how many beats are in each 
        bar (or measure). The time signature ranges from 3 to 7 indicating time signatures of "3/4", to "7/4".
        
        Range: `3` to `7`  
        Example: `4`
        """
        return self._TimeSignature
    

    @property
    def TrackHref(self) -> str:
        """ 
        A link to the Web API endpoint providing full details of the track.

        Example: `https://api.spotify.com/v1/tracks/2takcwOaAZWiXQijPHIx7B`
        """
        return self._TrackHref
    

    @property
    def Type(self) -> str:
        """ 
        The object type: `audio_features`.
        """
        return self._Type
    

    @property
    def Uri(self) -> str:
        """ 
        The Spotify URI for the track.  

        Example: `spotify:track:2takcwOaAZWiXQijPHIx7B`
        """
        return self._Uri
    

    @property
    def Valence(self) -> float:
        """ 
        A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track.   
        
        Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while 
        tracks with low valence sound more negative (e.g. sad, depressed, angry).  
        
        Range: `0` to `1`  
        Example: `0.428`
        """
        return self._Valence
    

    def ToString(self) -> str:
        """
        Returns a displayable string representation of the class.
        """
        msg:str = 'AudioFeatures:'
        if self._Uri is not None: msg = '%s\n Uri="%s"' % (msg, str(self._Uri))
        if self._Acousticness is not None: msg = '%s\n Acousticness="%s"' % (msg, str(self._Acousticness))
        if self._AnalysisUrl is not None: msg = '%s\n AnalysisUrl="%s"' % (msg, str(self._AnalysisUrl))
        if self._Danceability is not None: msg = '%s\n Danceability="%s"' % (msg, str(self._Danceability))
        if self._DurationMS is not None: msg = '%s\n DurationMS="%s"' % (msg, str(self._DurationMS))
        if self._Energy is not None: msg = '%s\n Energy="%s"' % (msg, str(self._Energy))
        if self._Id is not None: msg = '%s\n Id="%s"' % (msg, str(self._Id))
        if self._Instrumentalness is not None: msg = '%s\n Instrumentalness="%s"' % (msg, str(self._Instrumentalness))
        if self._Key is not None: msg = '%s\n Key="%s"' % (msg, str(self._Key))
        if self._Liveness is not None: msg = '%s\n Liveness="%s"' % (msg, str(self._Liveness))
        if self._Loudness is not None: msg = '%s\n Loudness="%s"' % (msg, str(self._Loudness))
        if self._Speechiness is not None: msg = '%s\n Speechiness="%s"' % (msg, str(self._Speechiness))
        if self._Tempo is not None: msg = '%s\n Tempo="%s"' % (msg, str(self._Tempo))
        if self._TimeSignature is not None: msg = '%s\n TimeSignature="%s"' % (msg, str(self._TimeSignature))
        if self._TrackHref is not None: msg = '%s\n TrackHref="%s"' % (msg, str(self._TrackHref))
        if self._Type is not None: msg = '%s\n Type="%s"' % (msg, str(self._Type))
        if self._Valence is not None: msg = '%s\n Valence="%s"' % (msg, str(self._Valence))
        return msg 
