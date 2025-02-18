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

    # the following examples were run for a playlist that contains 9 tracks.

    # reorder items in current playlist - move track #5 to position #1 in the list.
    playlistId:str = '4yptcTKnXjCu3V92tVVafS'
    print('\nReordering items in playlist id "%s": \n- move track #5 to position #1 in the list' % (playlistId))
    result:str = spotify.ReorderPlaylistItems(playlistId, 5, 1)
    print('\nPlaylist updated successfully:\n- snapshot ID = "%s"' % result)

    # reorder items in current playlist - move tracks #5,6,7 to position #1 in the list.
    playlistId:str = '4yptcTKnXjCu3V92tVVafS'
    print('\nReordering items in playlist id "%s": \n- move tracks #5,6,7 to position #1 in the list' % (playlistId))
    result:str = spotify.ReorderPlaylistItems(playlistId, 5, 1, 3)
    print('\nPlaylist updated successfully:\n- snapshot ID = "%s"' % result)

    # reorder items in current playlist - move track #7 to position #6 in the list.
    playlistId:str = '4yptcTKnXjCu3V92tVVafS'
    print('\nReordering items in playlist id "%s": \n- move track #7 to position #6 in the list' % (playlistId))
    result:str = spotify.ReorderPlaylistItems(playlistId, 7, 6)
    print('\nPlaylist updated successfully:\n- snapshot ID = "%s"' % result)

    # reorder items in current playlist - move track #5 to position #10 in the list.
    playlistId:str = '4yptcTKnXjCu3V92tVVafS'
    print('\nReordering items in playlist id "%s": \n- move track #5 to position #10 in the list' % (playlistId))
    result:str = spotify.ReorderPlaylistItems(playlistId, 5, 10)
    print('\nPlaylist updated successfully:\n- snapshot ID = "%s"' % result)

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
