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
    deviceId:str = "Web Player (Chrome)" # or device name
    print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % deviceId)
    spotify.PlayerTransferPlayback(deviceId, True)

    print('\nSuccess - control was transferred')

    # transfer Spotify Connect playback control to another device.
    # the device name and id can be retrieved from `GetPlayerDevices` method.
    deviceId:str = 'Bose-ST10-1'
    print('\nTransfer Spotify Connect playback control to:\n-Name: "%s" ...' % deviceId)
    spotify.PlayerTransferPlayback(deviceId, True)

    print('\nSuccess - control was transferred')

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
