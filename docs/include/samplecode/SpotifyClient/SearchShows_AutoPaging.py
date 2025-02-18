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

    # get Spotify catalog information about Shows that match a keyword string.
    # note - use an Authorization type of token or the `market` argument for this
    # method, otherwise the item result are all null.
    criteria:str = 'Joe Rogan'
    print('\nSearching for Shows - criteria: "%s" ...\n' % criteria)
    pageObj:SearchResponse = spotify.SearchShows(criteria, limitTotal=75)

    # display paging details.
    print(str(pageObj))
    print(str(pageObj.Shows))
    print('\nShows in this page of results (%d items):' % pageObj.Shows.ItemsCount)

    # display show details.
    show:ShowSimplified
    for show in pageObj.Shows.Items:
        print('- "{name}" ({uri})'.format(name=show.Name, uri=show.Uri))

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
