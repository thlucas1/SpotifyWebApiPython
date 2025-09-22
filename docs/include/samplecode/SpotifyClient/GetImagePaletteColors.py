from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = \
    [
        'user-read-playback-state',
        'user-read-email',
    ]

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # get the palette colors for an image https url.
    imageSource:str = "https://i.scdn.co/image/ab67616d0000b2733deaee5f76ab2da15dd8db86"
    print('\nGetting palette colors for image https url:\n- "%s" ...' % imageSource)
    result:ImagePaletteColors = spotify.GetImagePaletteColors(imageSource)
    print(result.ToString())

    # get the palette colors for an image http url.
    imageSource:str = "http://i.scdn.co/image/ab67616d0000b2733deaee5f76ab2da15dd8db86"
    print('\nGetting palette colors for image http url:\n- "%s" ...' % imageSource)
    result:ImagePaletteColors = spotify.GetImagePaletteColors(imageSource)
    print(result.ToString())

    # get the palette colors for an image on the file system.
    imageSource:str = './test/testdata/PlaylistCoverImage.jpg'
    print('\nGetting palette colors for image file:\n- "%s" ...' % imageSource)
    result:ImagePaletteColors = spotify.GetImagePaletteColors(imageSource)
    print(result.ToString())

    # get the palette colors for the currently playing Spotify item image url.
    print('\nGetting palette colors for currently playing image url ...')
    result:ImagePaletteColors = spotify.GetImagePaletteColors()
    print(result.ToString())

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
