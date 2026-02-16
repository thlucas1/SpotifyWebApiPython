from enum import StrEnum

class SpotifyTypePrefixes(StrEnum):
    """
    Spotify media type prefixes enumeration.
    """

    ALBUM = "spotify:album:"
    """
    Album media type.
    """

    ARTIST = "spotify:artist:"
    """
    Artist media type.
    """

    AUDIOBOOK = "spotify:audiobook:"
    """
    Audiobook media type.

    This value is not part of the Spotify Web API specification.
    It is loaded from our API so that the type of item can be determined programatically.
    """

    EPISODE = "spotify:episode:"
    """
    Episode media type.
    """

    PLAYLIST = "spotify:playlist:"
    """
    Playlist media type.
    """

    PODCAST = "spotify:podcast:"
    """
    Podcast episode type.

    This value is not part of the Spotify Web API specification.
    It is loaded from our API so that the type of item can be determined programatically.
    """

    SHOW = "spotify:show:"
    """
    Show media type.
    """

    TRACK = "spotify:track:"
    """
    Track media type.
    """

    USER = "spotify:user:"
    """
    Track media type.
    """

    UNKNOWN = "spotify:unknown:"
    """
    Unknown media type.

    This value is not part of the Spotify Web API specification.
    It is loaded from our API so that the type of item can be determined programatically.
    """
