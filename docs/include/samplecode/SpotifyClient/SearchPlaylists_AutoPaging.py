from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = \
    [
        'user-read-email',
        'user-library-read',
        'user-library-modify',
        'playlist-modify-private',
        'playlist-modify-public'
    ]

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # get Spotify catalog information about Playlists that match a keyword string.
    criteria:str = 'MercyMe'
    print('\nSearching for Playlists - criteria: "%s" ...\n' % criteria)
    pageObj:SearchResponse = spotify.SearchPlaylists(criteria, limitTotal=75)

    # display paging details.
    print(str(pageObj))
    print(str(pageObj.Playlists))
    print('\nPlaylists in this page of results (%d items):' % pageObj.Playlists.ItemsCount)

    # display playlist details.
    playlist:PlaylistSimplified
    for playlist in pageObj.Playlists.Items:
        print('- "{name}" ({uri})'.format(name=playlist.Name, uri=playlist.Uri))

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
