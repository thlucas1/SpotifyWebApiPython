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

    # get Spotify catalog information about artists similar to a given artist.
    artistId:str = '6APm8EjxOHSYM5B4i3vT3q'
    print('\nGetting artists similar to artist "%s" ...\n' % artistId)
    artists:list[Artist] = spotify.GetArtistRelatedArtists(artistId, True)

    artist:Artist
    for artist in artists:
                
        print(str(artist))
        print('')

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
