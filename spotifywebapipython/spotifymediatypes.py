from enum import StrEnum

class SpotifyMediaTypes(StrEnum):
    """
    Spotify media types enumeration.
    """

    ALBUM = "album"
    """
    Album media type.
    """

    ARTIST = "artist"
    """
    Artist media type.
    """

    AUDIOBOOK = "audiobook"
    """
    Audiobook media type.

    This value is not part of the Spotify Web API specification.
    It is loaded from our API so that the type of item can be determined programatically.
    """

    EPISODE = "episode"
    """
    Episode media type.
    """

    PLAYLIST = "playlist"
    """
    Playlist media type.
    """

    PODCAST = "podcast"
    """
    Podcast episode type.

    This value is not part of the Spotify Web API specification.
    It is loaded from our API so that the type of item can be determined programatically.
    """

    SHOW = "show"
    """
    Show media type.
    """

    TRACK = "track"
    """
    Track media type.
    """

    UNKNOWN = "unknown"
    """
    Unknown media type.

    This value is not part of the Spotify Web API specification.
    It is loaded from our API so that the type of item can be determined programatically.
    """


    def __eq__(self, other):
        """
        Override __eq__ so that we can compare enum members directly to their raw values 
        without explicitly accessing the ".value".
        """
        if isinstance(other, self.__class__):
            return self is other
        elif isinstance(other, type(self.value)):
            return self.value == other
        return False