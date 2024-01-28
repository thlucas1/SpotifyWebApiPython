from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = ['user-read-email','user-library-read']

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # check if one or more albums is already saved in the current Spotify user's 'Your Library'.
    albumIds:str = '382ObEPsp2rxGrnsizN5TX,6vc9OTcyd3hyzabCmsdnwE,382ObEPsp2rxGrnsizN5TY'
    print('\nChecking if albums are saved by the current user: \n- %s' % albumIds.replace(',','\n- '))
    result:dict = spotify.CheckAlbumFavorites(albumIds)
            
    print('\nResults:')
    for key in result.keys():
        print('- %s = %s' % (key, result[key]))

except Exception as ex:

    print("** Exception: %s" % str(ex))
