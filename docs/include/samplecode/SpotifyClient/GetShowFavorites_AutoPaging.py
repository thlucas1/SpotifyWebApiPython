from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = ['user-read-email','user-library-read']

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # get a list of the shows saved in the current Spotify user's 'Your Library'.
    print('\nGetting ALL saved shows for current user ...\n')
    pageObj:ShowPageSaved = spotify.GetShowFavorites(limitTotal=1000)

    # display paging details.
    print(str(pageObj))
    print('\nShows in this page of results (%d items):' % pageObj.ItemsCount)

    # display show details.
    showSaved:ShowSaved
    for showSaved in pageObj.Items:
        print('- "{name}" ({uri})'.format(name=showSaved.Show.Name, uri=showSaved.Show.Uri))

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
