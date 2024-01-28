from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = \
    [
        'user-modify-playback-state',
        'user-read-email',
        'user-read-playback-state'
    ]

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # verify that Spotify Connect has a default player active.
    defaultDeviceId:str = '236427c8c0d510caa323f84cb42bc03eec090750'
    print('\nVerifying Spotify Connect player is active; default device if not:\n- ID: %s ...' % (defaultDeviceId))
    playerState:PlayerPlayState = spotify.PlayerVerifyDeviceDefault(defaultDeviceId, False)

    print(str(playerState))
    print('')
    print(str(playerState.Item))

except Exception as ex:

    print("** Exception: %s" % str(ex))
