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

    # get player device info - by name.
    device:str = "Bose-ST10-1"
    print("\nPlayer device info - by name \"%s\" ..." % (device))
    scDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.GetPlayerDevice(device, refresh=True)
    if scDevice is not None:
        print(str(scDevice) + "\n")
    else:
        print("Player device not found: \"%s\"" % (device))

    # get player device info - by id.
    device:str = "30fbc80e35598f3c242f2120413c943dfd9715fe"
    print("\nPlayer device info - by id \"%s\" ..." % (device))
    scDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.GetPlayerDevice(device, refresh=True)
    if scDevice is not None:
        print(str(scDevice) + "\n")
    else:
        print("Player device not found: \"%s\"" % (device))

    # get player device info - by unknown name.
    device:str = "MyName"
    print("\nPlayer device info - by unknown name \"%s\" ..." % (device))
    scDevice:SpotifyConnectDevice = spotify.SpotifyConnectDirectory.GetPlayerDevice(device, refresh=True)
    if scDevice is not None:
        print(str(scDevice) + "\n")
    else:
        print("Player device not found: \"%s\"" % (device))

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
