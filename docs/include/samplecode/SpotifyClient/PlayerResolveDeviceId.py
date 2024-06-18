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

    # resolve Spotify Connect player device by it's Id value.
    deviceId:str = '30fbc80e35598f3c242f2120413c943dfd9715fe'
    print('\nResolving Spotify Connect player device: \n- ID = "%s" ...' % deviceId)
    deviceResult:str = spotify.PlayerResolveDeviceId(deviceId)

    if deviceResult is not None:
        print('result "%s"' % deviceResult)
    else:
        print("Device Id could not be resolved!")

    # resolve Spotify Connect player device by it's Name value.
    deviceName:str = 'Bose-ST10-2'
    print('\nResolving Spotify Connect player device: \n- Name = "%s" ...' % deviceName)
    deviceResult:str = spotify.PlayerResolveDeviceId(deviceName)

    if deviceResult is not None:
        print('  result "%s"' % deviceResult)
    else:
        print("Device Name was not found in the list of devices")
    
    # resolve Spotify Connect player device by it's Name value, using a Disconnected device.
    zconn:ZeroconfConnect = ZeroconfConnect('192.168.1.82', 8200, '/zc', useSSL=False)
    result:ZeroconfResponse = zconn.Disconnect()            
    deviceName:str = 'Bose-ST10-2'
    print('\nResolving Spotify Connect player device: \n- Name = "%s" ...' % deviceName)
    deviceResult:str = spotify.PlayerResolveDeviceId(deviceName)

    if deviceResult is not None:
        print('  result "%s"' % deviceResult)
    else:
        print("Device Name was not found in the list of devices")

except Exception as ex:

    print("** Exception: %s" % str(ex))
