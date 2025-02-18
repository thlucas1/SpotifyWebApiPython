from spotifywebapipython import *
from spotifywebapipython.models import *
from spotifywebapipython.zeroconfapi import ZeroconfConnect, ZeroconfResponse

try:

    # this sample requires an authorization token, as it accesses protected data.

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = \
    [
        'user-read-playback-state', 
        'user-read-email',
    ]

    # create new spotify client instance, passing the Spotify Connect user context and discovery timeout.
    spotify:SpotifyClient = SpotifyClient(
        spotifyConnectUsername="yourSpotifyUsername", # (e.g. 'yourname@gmail.com', '1234567890', etc)
        spotifyConnectPassword="yourSpotifyPassword",
        spotifyConnectLoginId="yourSpotifyLoginId",   # (e.g. '31l77548798704mns987fdf0986e')
        spotifyConnectDiscoveryTimeout=1.5,
        tokenStorageDir='./yourTokenStorageDir',
    )

    # generate a spotify authorization code with PKCE access token.
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)

    # log user profile info.
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    device:SpotifyConnectDevice = None

    # resolve Spotify Connect player device by it's Id value.
    deviceId:str = '30fbc80e35598f3c242f2120413c943dfd9715fe'
    print('\nResolving Spotify Connect player device: \n- ID = "%s" ...\n' % deviceId)
    device = spotify.GetSpotifyConnectDevice(deviceId)
    if device is not None:
        print(str(device))

    # resolve Spotify Connect player device by it's Name value.
    deviceName:str = 'Bose-ST10-2'
    print('\nResolving Spotify Connect player device: \n- Name = "%s" ...\n' % deviceName)
    device = spotify.GetSpotifyConnectDevice(deviceName)
    if device is not None:
        print(str(device))
    
    # resolve Spotify Connect player device by it's Name value, using a Disconnected device.
    deviceName:str = 'Bose-ST10-2'
    print('\nForcing disconnect of Spotify Connect device: \n- Name = "%s" ...\n' % deviceName)
    zconn:ZeroconfConnect = ZeroconfConnect('192.168.1.82', 8200, '/zc', useSSL=False, tokenStorageDir=spotify.TokenStorageDir)
    result:ZeroconfResponse = zconn.Disconnect()            

    print('\nResolving Spotify Connect player disconnected device: \n- Name = "%s" ...\n' % deviceName)
    device = spotify.GetSpotifyConnectDevice(deviceName)
    if device is not None:
        print(str(device))

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
