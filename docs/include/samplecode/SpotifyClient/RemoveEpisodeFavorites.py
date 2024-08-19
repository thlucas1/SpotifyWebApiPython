from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = \
    [
        'user-library-modify',
        'user-read-email',
    ]

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # remove one or more episodes from the current user's 'Your Library'.
    episodeIds:str = '1hPX5WJY6ja6yopgVPBqm4,3F97boSWlXi8OzuhWClZHQ'
    print('\nRemoving saved episode(s) from the current users profile: \n- %s' % episodeIds.replace(',','\n- '))
    spotify.RemoveEpisodeFavorites(episodeIds)
            
    print('\nSuccess - episode(s) were removed')

    # remove nowplaying episode from the current user's 'Your Library'.
    print('\nRemoving nowplaying episode from the current users profile')
    spotify.RemoveEpisodeFavorites()

    print('\nSuccess - episode(s) were removed')

except Exception as ex:

    print("** Exception: %s" % str(ex))
