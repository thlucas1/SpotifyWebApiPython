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

    # remove the current user as a follower of a playlist.
    playlistId:str = '3cEYpjA9oz9GiPac4AsH4n'
    print('\nUnfollowing playlist id "%s" ...' % playlistId)
    spotify.UnfollowPlaylist(playlistId)
            
    print('\nSuccess - playlist is now unfollowed')

    # remove the current user as a follower of the nowplaying playlist.
    print('\nUnfollowing nowplaying playlist ...')
    spotify.UnfollowPlaylist()
            
    print('\nSuccess - nowplaying playlist is now unfollowed')

except Exception as ex:

    print("** Exception: %s" % str(ex))
