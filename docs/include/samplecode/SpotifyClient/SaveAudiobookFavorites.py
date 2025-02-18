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

    # save one or more audiobooks to the current user's 'Your Library'.
    audiobookIds:str = '3PFyizE2tGCSRLusl2Qizf,7iHfbu1YPACw6oZPAFJtqe'
    print('\nAdding saved audiobook(s) to the current users profile: \n- %s' % audiobookIds.replace(',','\n- '))
    spotify.SaveAudiobookFavorites(audiobookIds)
            
    print('\nSuccess - audiobook(s) were added')

    # save nowplaying audiobook to the current user's 'Your Library'.
    print('\nAdding nowplaying audiobook to the current users profile')
    spotify.SaveAudiobookFavorites()
            
    print('\nSuccess - audiobook(s) were added')

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
