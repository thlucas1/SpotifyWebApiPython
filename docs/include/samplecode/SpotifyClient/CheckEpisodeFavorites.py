from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

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

    # check if one or more episodes is already saved in the current Spotify user's 'Your Library'.
    episodeIds:str = '1hPX5WJY6ja6yopgVPBqm4,3F97boSWlXi8OzuhWClZHQ'
    print('\nChecking if episodes are saved by the current user: \n- %s' % episodeIds.replace(',','\n- '))
    result:dict = spotify.CheckEpisodeFavorites(episodeIds)
            
    print('\nResults:')
    for key in result.keys():
        print('- %s = %s' % (key, result[key]))

    # check if nowplaying episode is saved in the current Spotify user's 'Your Library'.
    print('\nChecking if nowplaying episode is saved by the current user ...')
    result:dict = spotify.CheckEpisodeFavorites()
            
    print('\nResults:')
    for key in result.keys():
        print('- %s = %s' % (key, result[key]))

except Exception as ex:

    print("** Exception: %s" % str(ex))
