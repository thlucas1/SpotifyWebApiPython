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

    # add items to end of a playlist.
    playlistId:str = '4yptcTKnXjCu3V92tVVafS'
    itemUris:str = 'spotify:track:2takcwOaAZWiXQijPHIx7B, spotify:track:4eoYKv2kDwJS7gRGh5q6SK'
    print('\nAdding items to end of playlist id "%s" ...\n' % playlistId)
    result:str = spotify.AddPlaylistItems(playlistId, itemUris)

    print('Playlist updated successfully:\n- snapshot ID = "%s"' % result)

    # add items to begining of a playlist.
    playlistId:str = '4yptcTKnXjCu3V92tVVafS'
    itemUris:str = 'spotify:track:1kWUud3vY5ij5r62zxpTRy'
    print('\nAdding items to beginning of playlist id "%s" ...\n' % playlistId)
    result:str = spotify.AddPlaylistItems(playlistId, itemUris, 0)

    print('Playlist updated successfully:\n- snapshot ID = "%s"' % result)

    # add nowplaying item to end of a playlist.
    playlistId:str = '4yptcTKnXjCu3V92tVVafS'
    print('\nAdding nowplaying item to end of playlist id "%s" ...\n' % playlistId)
    result:str = spotify.AddPlaylistItems(playlistId)

    print('Playlist updated successfully:\n- snapshot ID = "%s"' % result)

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
