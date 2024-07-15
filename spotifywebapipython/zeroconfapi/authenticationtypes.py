# external package imports.
from enum import IntEnum

# our package imports.
from ..sautils import export


@export
class AuthenticationTypes(IntEnum):
    """
    Represents the type of authentication used.
    """

    USER_PASS = 0
    """
    UserId and Password (0x00).
    """
    
    STORED_SPOTIFY_CREDENTIALS = 1
    """
    Spotify credentials (0x01).
    """
    
    STORED_FACEBOOK_CREDENTIALS = 2
    """
    Facebook credentials (0x02).
    """
    
    SPOTIFY_TOKEN = 3
    """
    Spotify authorization token (0x03).
    """
    
    FACEBOOK_TOKEN = 4
    """
    Facebook authorization token (0x04).
    """
    