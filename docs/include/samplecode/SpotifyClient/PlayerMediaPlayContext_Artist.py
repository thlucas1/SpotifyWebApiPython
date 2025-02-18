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

    # if no active spotify player device, then use the specified device.
    spotify.DefaultDeviceId = "Bose-ST10-1"
            
    # set device to control.
    deviceId:str = "*"          # use DefaultDeviceId
    #deviceId:str = "Office"    # use device name (or id)
    #deviceId:str = None        # use currently active device

    # play artist on the specified Spotify Connect device.
    contextUri:str = 'spotify:artist:6APm8EjxOHSYM5B4i3vT3q'  # Artist = MercyMe
    print('\nPlaying artist on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
    spotify.PlayerMediaPlayContext(contextUri, deviceId=deviceId)

    print('\nSuccess - artist should be playing')

    # play artist and start first song played at the 25 seconds position on the specified Spotify Connect device.
    contextUri:str = 'spotify:artist:6APm8EjxOHSYM5B4i3vT3q'  # Artist = MercyMe
    print('\nPlaying artist at the 25 seconds position on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
    spotify.PlayerMediaPlayContext(contextUri, positionMS=25000, deviceId=deviceId)

    print('\nSuccess - artist should be playing')

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
