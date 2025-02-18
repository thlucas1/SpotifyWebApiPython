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

    # check if one or more shows is already saved in the current Spotify user's 'Your Library'.
    showIds:str = '6kAsbP8pxwaU2kPibKTuHE,4rOoJ6Egrf8K2IrywzwOMk,1y3SUbFMUSESC1N43tBleK'
    print('\nChecking if shows are saved by the current user: \n- %s' % showIds.replace(',','\n- '))
    result:dict = spotify.CheckShowFavorites(showIds)
            
    print('\nResults:')
    for key in result.keys():
        print('- %s = %s' % (key, result[key]))

    # check if nowplaying show is saved in the current Spotify user's 'Your Library'.
    print('\nChecking if nowplaying show is saved by the current user ...')
    result:dict = spotify.CheckShowFavorites()
            
    print('\nResults:')
    for key in result.keys():
        print('- %s = %s' % (key, result[key]))

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
