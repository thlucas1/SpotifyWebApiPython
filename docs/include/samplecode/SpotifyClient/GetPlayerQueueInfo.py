from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = \
    [
        'user-read-currently-playing',
        'user-read-email',
        'user-read-playback-state',
    ]

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # get Spotify Connect player queue info for the current user.
    print('\nGetting Spotify Connect player queue info ...\n')
    queueInfo:PlayerQueueInfo = spotify.GetPlayerQueueInfo()

    print(str(queueInfo))
            
    if queueInfo.CurrentlyPlaying is not None:
        print('\nCurrently Playing:\n%s' % queueInfo.CurrentlyPlaying)

    print('\nQueue: (%s items)' % queueInfo.QueueCount)
    for item in queueInfo.Queue:
        print('- {type}: "{name}" ({uri})'.format(type=item.Type, name=item.Name, uri=item.Uri))

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
