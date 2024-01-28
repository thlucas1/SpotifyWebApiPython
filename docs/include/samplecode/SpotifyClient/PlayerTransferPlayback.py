from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = \
    [
        'user-modify-playback-state',
        'user-read-email',
    ]

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # transfer Spotify Connect playback control to another device.
    # the device name and id can be retrieved from `GetPlayerDevices` method.
    deviceName:str = 'Web Player (Chrome)'
    deviceId:str = '13c7b6361ab322f28c39bf7638f058290d88bb58'
    print('\nTransfer Spotify Connect playback control to:\n-Name: "%s"\nID:   %s ...' % (deviceName, deviceId))
    spotify.PlayerTransferPlayback(deviceId, True)

    print('\nSuccess - control was transferred')

    # transfer Spotify Connect playback control to another device.
    # the device name and id can be retrieved from `GetPlayerDevices` method.
    deviceName:str = 'Bose ST-10 Speaker'
    deviceId:str = '30fbc80e35598f3c242f2120413c943dfd9715fe'
    print('\nTransfer Spotify Connect playback control to:\n-Name: "%s"\nID:   %s ...' % (deviceName, deviceId))
    spotify.PlayerTransferPlayback(deviceId, True)

    print('\nSuccess - control was transferred')

except Exception as ex:

    print("** Exception: %s" % str(ex))
