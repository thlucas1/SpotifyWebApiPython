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

    # remove items from current playlist.
    playlistId:str = '4yptcTKnXjCu3V92tVVafS'
    itemUris:str = 'spotify:track:2takcwOaAZWiXQijPHIx7B,spotify:track:4eoYKv2kDwJS7gRGh5q6SK'
    print('\nRemoving items from playlist id "%s": \n- %s' % (playlistId, itemUris.replace(',','\n- ')))
    result:str = spotify.RemovePlaylistItems(playlistId, itemUris)

    print('\nPlaylist updated successfully:\n- snapshot ID = "%s"' % result)

    # remove items from a playlist snapshot.
    playlistId:str = '4yptcTKnXjCu3V92tVVafS'
    snapshotId:str = 'NDQsMGI2ZjJhMTcyNWY3NmMyZDZhNTkxNTc5ODI0ZGFjOWRkYWM2N2QyMw===='
    itemUris:str = 'spotify:track:2takcwOaAZWiXQijPHIx7B,spotify:track:4eoYKv2kDwJS7gRGh5q6SK'
    print('\nRemoving items from snapshot playlist id "%s": \n- %s' % (playlistId, itemUris.replace(',','\n- ')))
    result:str = spotify.RemovePlaylistItems(playlistId, itemUris, snapshotId)

    print('\nPlaylist updated successfully:\n- snapshot ID = "%s"' % result)

except Exception as ex:

    print("** Exception: %s" % str(ex))
