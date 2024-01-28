from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = \
    [
        'user-read-playback-state',
        'user-read-email',
    ]

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # get Spotify Connect playback state.
    print('\nGetting Spotify Connect playback state ...\n')
    playerState:PlayerPlayState = spotify.GetPlayerPlaybackState()

    if playerState.CurrentlyPlayingType is not None:
                
        print(str(playerState))
        print('')
        print(str(playerState.Item))
               
    else:
                
        print('Spotify Connect playback State is unavailable at this time')

except Exception as ex:

    print("** Exception: %s" % str(ex))
