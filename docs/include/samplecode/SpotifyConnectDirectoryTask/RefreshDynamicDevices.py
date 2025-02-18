from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = \
    [
        'user-read-currently-playing',
        'user-read-playback-state',
        'user-read-email',
    ]

    # Spotify Connect credentials and timeout:
    spotifyConnectUsername:str = 'your_spotify_username'    # (e.g. "MyUserName@yahoo.com")
    spotifyConnectPassword:str = 'your_spotify_password'    # (e.g. "MyPassword")
    spotifyConnectLoginId:str  = 'your_spotify_loginid'     # (e.g. "31l88dfjhgnnhh44f7vjj67jdjfc")
    spotifyConnectDiscoveryTimeout:float = 4.0              # seconds

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient(
        tokenStorageDir='./test/testdata', 
        spotifyConnectUsername=spotifyConnectUsername, 
        spotifyConnectPassword=spotifyConnectPassword, 
        spotifyConnectLoginId=spotifyConnectLoginId,
        spotifyConnectDiscoveryTimeout=spotifyConnectDiscoveryTimeout
        )

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # log all spotify connect devices.
    scDevices = spotify.GetSpotifyConnectDevices(refresh=True)
    print('\nSpotify Connect device list (before) ...')
    scDevice:SpotifyConnectDevice
    for idx in range(len(scDevices)):
        scDevice:SpotifyConnectDevice = scDevices[idx]
        isActive:str = " (active)" if (scDevice.IsActiveDevice) else ""
        print("%s - %s [%s]%s" % (str(idx), scDevice.Title, scDevice.DiscoveryResult.Description, isActive))

    # refresh the player device list, and return the active device.
    scActiveDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.RefreshDynamicDevices()

    # log all spotify connect devices.
    scDevices = spotify.GetSpotifyConnectDevices(refresh=True)
    print('\nSpotify Connect device list (after) ...')
    scDevice:SpotifyConnectDevice
    for idx in range(len(scDevices)):
        scDevice:SpotifyConnectDevice = scDevices[idx]
        isActive:str = " (active)" if (scDevice.IsActiveDevice) else ""
        print("%s - %s [%s]%s" % (str(idx), scDevice.Title, scDevice.DiscoveryResult.Description, isActive))

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
