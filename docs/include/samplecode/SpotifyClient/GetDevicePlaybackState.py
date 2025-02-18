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

    # if no active spotify player device, then use the specified device.
    spotify.DefaultDeviceId = "Bose-ST10-1"
            
    # set device to control.
    #deviceId:str = "Bose-ST10-2"   # Bose SoundTouch device
    #deviceId:str = "Nest Audio 01" # Chromecast device
    deviceId:str = "Office"        # Sonos device
    #deviceId:str = "*"             # use DefaultDeviceId
    #deviceId:str = None            # use currently playing device

    # get Spotify Connect playback state.
    print('\nGetting Spotify Connect device playback state ...\n- Device = \"%s\"' % (deviceId))
    playerState:PlayerPlayState = spotify.GetDevicePlaybackState(deviceId)

    if playerState.IsEmpty:

        print('Spotify Connect device playback State is unavailable at this time')

    else:

        print(str(playerState))
        print('')
        print(str(playerState.Item))
        print('')
        print(str(playerState.Device))
        print('')
        print(str(playerState.Actions))
        print('')

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
