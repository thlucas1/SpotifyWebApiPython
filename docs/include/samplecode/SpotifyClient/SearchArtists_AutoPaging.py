from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    CLIENT_ID:str = 'your_client_id'
    CLIENT_SECRET:str = 'your_client_secret'

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify client credentials access token (no scope, public data use only).
    spotify.SetAuthTokenClientCredentials(CLIENT_ID, CLIENT_SECRET)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # get Spotify catalog information about Artists that match a keyword string.
    criteria:str = 'MercyMe'
    print('\nSearching for Artists - criteria: "%s" ...\n' % criteria)
    pageObj:SearchResponse = spotify.SearchArtists(criteria, limitTotal=75)

    # display paging details.
    print(str(pageObj))
    print(str(pageObj.Artists))
    print('\nArtists in this page of results (%d items):' % pageObj.Artists.ItemsCount)

    # display artist details.
    artist:Artist
    for artist in pageObj.Artists.Items:
        print('- "{name}" ({uri})'.format(name=artist.Name, uri=artist.Uri))

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
