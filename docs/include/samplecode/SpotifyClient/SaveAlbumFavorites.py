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

    # save one or more albums to the current user's 'Your Library'.
    albumIds:str = '382ObEPsp2rxGrnsizN5TX,6vc9OTcyd3hyzabCmsdnwE,382ObEPsp2rxGrnsizN5TY'
    print('\nAdding saved album(s) to the current users profile: \n- %s' % albumIds.replace(',','\n- '))
    spotify.SaveAlbumFavorites(albumIds)
            
    print('\nSuccess - album(s) were added')

except Exception as ex:

    print("** Exception: %s" % str(ex))
