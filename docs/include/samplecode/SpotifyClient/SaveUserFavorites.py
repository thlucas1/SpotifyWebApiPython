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

    # save one or more items to the current user's 'Your Library'.
    ids:str = 'spotify:artist:6APm8EjxOHSYM5B4i3vT3q,spotify:album:6vc9OTcyd3hyzabCmsdnwE,spotify:track:1kWUud3vY5ij5r62zxpTRy'
    print('\nAdding saved items(s) to the current users library: \n- %s' % ids.replace(',','\n- '))
    spotify.SaveUserFavorites(ids)
            
    print('\nSuccess - items(s) were added')
    
    # save nowplaying item to the current user's 'Your Library'.
    print('\nSaving nowplaying item to the current users library')
    spotify.SaveUserFavorites()

    print('\nSuccess - items(s) were added')

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
