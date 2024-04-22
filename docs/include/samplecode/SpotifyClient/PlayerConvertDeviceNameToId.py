from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = \
    [
        'user-read-email',
        'user-read-playback-state'
    ]

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # get device id for specified device name.
    deviceName:str = 'Web Player (Chrome)'
    print('\nGetting Spotify Connect Player device id for name:\n- Name: %s ...' % (deviceName))
    deviceId:str = spotify.PlayerConvertDeviceNameToId(deviceName, True)
    print('- ID:   %s' % (deviceId))

except Exception as ex:

    print("** Exception: %s" % str(ex))
