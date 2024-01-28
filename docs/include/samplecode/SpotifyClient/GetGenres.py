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

    # get a list of available genre seed parameter values for recommendations.
    print('\nGetting list of genres ...')
    genres:list[str] = spotify.GetGenres()

    # display genre details.
    print('\nAll Genres (sorted by name):')
    genre:str
    for genre in genres:

        print('- "{name}"'.format(name=genre))

except Exception as ex:

    print("** Exception: %s" % str(ex))
