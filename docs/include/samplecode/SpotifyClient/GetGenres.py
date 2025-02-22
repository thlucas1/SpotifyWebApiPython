from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = \
    [
        'playlist-modify-private',
        'playlist-modify-public',
        'ugc-image-upload',
        'user-library-modify',
        'user-library-read',
        'user-read-email',
        'user-read-playback-position',
    ]

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
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

    # get cached configuration, refreshing from device if needed.
    genres:list[str] = spotify.GetGenres(refresh=False)
    print("\nCached configuration (count): %d" % len(genres))

    # get cached configuration directly from the configuration manager dictionary.
    if "GetGenres" in spotify.ConfigurationCache:
        genres:list[str] = spotify.ConfigurationCache["GetGenres"]
        print("\nCached configuration direct access (count): %d" % len(genres))

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
