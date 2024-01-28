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

    # get Spotify catalog information for a multiple episodes.
    episodeIds:str = '16OUc3NwQe7kJNaH8zmzfP,1hPX5WJY6ja6yopgVPBqm4,3F97boSWlXi8OzuhWClZHQ'
    print('\nGetting details for multiple episodes: \n- %s \n' % episodeIds.replace(',','\n- '))
    episodes:list[Episode] = spotify.GetEpisodes(episodeIds)

    episode:Episode
    for episode in episodes:
                
        print(str(episode))
        print('')

except Exception as ex:

    print("** Exception: %s" % str(ex))
