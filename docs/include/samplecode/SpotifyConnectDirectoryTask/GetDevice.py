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

    # get device info - by name.
    # exception will be raised if device was not resolved.
    device:str = "Bose-ST10-2"
    print("\nDevice info - by name \"%s\" ..." % (device))
    scDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.GetDevice(device)
    print(str(scDevice) + "\n")

    # get device info - by id.
    # exception will be raised if device was not resolved.
    device:str = "5d4931f9d0684b625d702eaa24137b2c1d99539c"
    print("\nDevice info - by id \"%s\" ..." % (device))
    scDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.GetDevice(device)
    print(str(scDevice) + "\n")

    # get device info - by * default.
    # exception will be raised if device was not resolved.
    spotify.DefaultDeviceId = "Bose-ST10-1111"
    device:str = "*"
    print("\nDevice info - by * default  \"%s\" ..." % (device))
    scDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.GetDevice(device)
    print(str(scDevice) + "\n")

    # get device info - by default.
    # exception will be raised if device was not resolved.
    device:str = None
    print("\nDevice info - by active default  \"%s\" ..." % (device))
    scDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.GetDevice(device)
    print(str(scDevice) + "\n")

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser.
    if (spotify is not None):
        spotify.StopSpotifyConnectDirectoryTask()
