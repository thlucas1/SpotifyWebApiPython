# our package imports.
from spotifywebapipython import SpotifyApiError


class SpotifyConnectZeroconfLaunchError(Exception):
    """
    Exception raised when a cast app fails to launch.
    """


class SpotifyConnectZeroconfPlaybackTransferError(Exception):
    """
    Exception raised when a cast app fails to receive transfer of playback control.
    """


class SpotifyConnectDeviceNotFound(SpotifyApiError):
    """
    Exception raised when a Spotify Connect device could not be resolved.
    """
