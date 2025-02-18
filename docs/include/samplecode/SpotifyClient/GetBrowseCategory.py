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

    # get a single category used to tag items in Spotify.
    categoryId:str = '0JQ5DAqbMKFy0OenPG51Av' # "Christian and Gospel" category id
    print('\nGetting details for category "%s" ...\n' % categoryId)
    category:Category = spotify.GetBrowseCategory(categoryId)

    print(str(category))
            
    print('\nIcons(s):')
    for icon in category.Icons:
        print(str(icon))

    # get cached configuration, refreshing from device if needed.
    spotify.GetBrowseCategorys()  # load cache
    category:Category = spotify.GetBrowseCategory(categoryId, refresh=False)
    print("\nCached configuration:\n%s" % str(category))

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
