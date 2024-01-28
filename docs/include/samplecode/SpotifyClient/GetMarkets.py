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

    # get the list of markets where Spotify is available.
    print('\nGetting list of markets ...')
    markets:list[str] = spotify.GetMarkets()

    # display genre details.
    print('\nAll Markets (sorted by id):')
    market:str
    for market in markets:

        print('- "{name}"'.format(name=market))

except Exception as ex:

    print("** Exception: %s" % str(ex))
