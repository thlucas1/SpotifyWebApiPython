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

    # remove one or more tracks from the current user's 'Your Library'.
    trackIds:str = '1kWUud3vY5ij5r62zxpTRy,2takcwOaAZWiXQijPHIx7B,4eoYKv2kDwJS7gRGh5q6SK'
    print('\nRemoving saved track(s) from the current users profile: \n- %s' % trackIds.replace(',','\n- '))
    spotify.RemoveTrackFavorites(trackIds)
            
    # remove nowplaying track from the current user's 'Your Library'.
    print('\nRemoving nowplaying track from the current users profile')
    spotify.RemoveTrackFavorites()
            
    print('\nSuccess - track(s) were removed')

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
