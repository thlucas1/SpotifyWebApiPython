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

    # change playlist details.
    playlistId:str = '4yptcTKnXjCu3V92tVVafS'
    print('\nChanging playlist details for id "%s" ...\n' % playlistId)
    spotify.ChangePlaylistDetails(playlistId, 
                                  name='My Updated Playlist Name',
                                  description='This is an updated playlist description with a unicode copyright \u00A9 character in it.',
                                  public=False,
                                  collaborative=True)

    print('\nSuccess - playlist details were updated')

except Exception as ex:

    print("** Exception: %s" % str(ex))
