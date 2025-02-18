from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

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

    # create a playlist for the current user.
    userId:str = spotify.UserProfile.Id
    print('\nCreating new (empty) playlist for user "%s" ...\n' % userId)
    playlist:Playlist = spotify.CreatePlaylist(userId, 'My New Playlist 04',"Created from the SpotifyWebApiPython's library - test unicode \u00A9.",False,False)

    print(str(playlist))

    # create a playlist for the current user, and assign an image.
    userId:str = spotify.UserProfile.Id
    imagePath:str = './test/testdata/PlaylistCoverImage.jpg'
    print('\nCreating new (empty) playlist for user "%s" ...\n' % userId)
    playlist:Playlist = spotify.CreatePlaylist(userId, 'My New Playlist 04',"Created from the SpotifyWebApiPython's library - test unicode \u00A9.",False,False,imagePath)

    print(str(playlist))

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
