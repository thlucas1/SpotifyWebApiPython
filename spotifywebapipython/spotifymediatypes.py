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
    """

    EPISODE = "episode"
    """
    Episode media type.
    """

    PLAYLIST = "playlist"
    """
    Playlist media type.
    """

    SHOW = "show"
    """
    Show media type.
    """

    TRACK = "track"
    """
    Track media type.
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