from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = \
    [
        'user-read-email',
        'user-top-read',
    ]

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # get current user's top tracks based on calculated affinity.
    affinity:str = 'long_term'
    print('\nGetting ALL current user top tracks for "%s" affinity ...\n' % affinity)
    pageObj:TrackPage = spotify.GetUsersTopTracks(affinity, limitTotal=1000)

    # display paging details.
    print(str(pageObj))
    print('\nTracks in this page of results (%d items):' % pageObj.ItemsCount)

    # display track details.
    track:Track
    for track in pageObj.Items:
        print('- "{name}" ({uri})'.format(name=track.Name, uri=track.Uri))

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
