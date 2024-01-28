from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = \
    [
        'user-modify-playback-state',
        'user-read-email',
    ]

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # seek to the given position in the on the specified Spotify Connect device.
    positionMS:int = 25000
    deviceId:str = None   # use currently playing device
    print('\nSeeking to %d milliseconds on Spotify Connect device:\n- "%s" ...' % (positionMS, deviceId))
    spotify.PlayerMediaSeek(positionMS, deviceId)

    print('\nSuccess - seek to position in track')

except Exception as ex:

    print("** Exception: %s" % str(ex))
