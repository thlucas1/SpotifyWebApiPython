from spotifywebapipython import *
from spotifywebapipython.models import *
from spotifywebapipython.zeroconfapi import ZeroconfConnect, ZeroconfResponse

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = \
    [
        'user-read-playback-state', 
        'user-read-email',
    ]

    # create new spotify client instance, passing the Spotify Connect user context and discovery timeout.
    spotify:SpotifyClient = SpotifyClient(
        spotifyConnectUsername="yourSpotifyConnectDeviceUsername", 
        spotifyConnectPassword="yourSpotifyConnectDevicePassword",
        spotifyConnectDiscoveryTimeout=1.5
    )

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # activate all Spotify Connect player devices on the local network
    # without switching the device user context.
    print('\nActivating Spotify Connect player devices')
    result:str = spotify.PlayerActivateDevices(verifyUserContext=False)
    print(result)
    
    # activate all Spotify Connect player devices on the local network
    # and switch the device user context to our user context.  this will
    # disconnect other users from all spotify connect player devices
    # defined to the local network.
    print('\nActivating Spotify Connect player devices for our user context')
    result:str = spotify.PlayerActivateDevices(verifyUserContext=True)
    print(result)

except Exception as ex:

    print("** Exception: %s" % str(ex))
