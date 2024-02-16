from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = \
    [
        'user-read-playback-state', 
        'user-read-email',
    ]

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # get Spotify Connect player device by it's Id value.
    deviceId:str = '30fbc80e35598f3c242f2120413c943dfd9715fe'
    print('\nGetting Spotify Connect player device: \n- ID = "%s" ...\n' % deviceId)
    device:Device = spotify.GetPlayerDevice(deviceId)

    if device is not None:
        print(str(device))
    else:
        print("Device Id was not found in the list of devices")

    # get Spotify Connect player device by it's Name value.
    deviceName:str = 'Bose-ST10-1'
    print('\nGetting Spotify Connect player device: \n- Name = "%s" ...\n' % deviceName)
    device:Device = spotify.GetPlayerDevice(deviceName)

    if device is not None:
        print(str(device))
    else:
        print("Device Name was not found in the list of devices")
    
    # get cached configuration, refreshing from device if needed.
    device:Device = spotify.GetPlayerDevice(deviceId, refresh=False)
    print("\nCached configuration (by Id):\n%s" % str(device))

    # get cached configuration, refreshing from device if needed.
    device:Device = spotify.GetPlayerDevice(deviceName, refresh=False)
    print("\nCached configuration (by Name):\n%s" % str(device))

except Exception as ex:

    print("** Exception: %s" % str(ex))
