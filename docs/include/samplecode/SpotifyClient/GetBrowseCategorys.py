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

    # get a sorted list of all categories used to tag items in Spotify.
    print('\nGetting all browse categories ...')
    categories:list[Category] = spotify.GetBrowseCategorys()

    # display category details.
    print('\nAll Browse Categories (sorted by name):')
    category:Category
    for category in categories:

        print('- "{name}" ({uri})'.format(name=category.Name, uri=category.Id))

except Exception as ex:

    print("** Exception: %s" % str(ex))
