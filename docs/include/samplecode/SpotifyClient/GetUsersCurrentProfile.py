from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = \
    [
        'user-library-read',
        'user-read-email',
    ]

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # note - the spotify.UserProfile contains the same object, but you can also do it this way ...

    # get detailed profile information about the current user.
    print('\nGetting user profile for current user ...\n')
    userProfile:UserProfile = spotify.GetUsersCurrentProfile()

    print(str(userProfile))

    # get cached configuration, refreshing from device if needed.
    userProfile:UserProfile = spotify.GetUsersCurrentProfile(refresh=False)
    print("\nCached configuration:\n%s" % str(userProfile))

    # get cached configuration directly from the configuration manager dictionary.
    if "GetUsersCurrentProfile" in spotify.ConfigurationCache:
        userProfile:UserProfile = spotify.ConfigurationCache["GetUsersCurrentProfile"]
        print("\nCached configuration direct access:\n%s" % str(userProfile))

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
