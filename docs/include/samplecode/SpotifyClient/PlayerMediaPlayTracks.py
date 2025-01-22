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

    # play single track on the specified Spotify Connect device.
    uris:str='spotify:track:1kWUud3vY5ij5r62zxpTRy'  # Flawless
    print('\nPlaying media on Spotify Connect device: \nID: %s \n- %s' % (deviceId, uris.replace(',','\n- ')))
    spotify.PlayerMediaPlayTracks(uris, 0, deviceId)

    print('\nSuccess - media should be playing')

    # play single track on the specified Spotify Connect device.
    # start playing at the 25 seconds (25000 milliseconds) point in the track.
    uris:str='spotify:track:1kWUud3vY5ij5r62zxpTRy'  # Flawless
    print('\nPlaying media on Spotify Connect device: \nID: %s \n- %s' % (deviceId, uris.replace(',','\n- ')))
    spotify.PlayerMediaPlayTracks(uris, 25000, deviceId)

    print('\nSuccess - media should be playing')

    # play multiple tracks on the specified Spotify Connect device.
    uris:str='spotify:track:1kWUud3vY5ij5r62zxpTRy,spotify:track:27JODWXo4VNa6s7HqDL9yQ,spotify:track:4iV5W9uYEdYUVa79Axb7Rh'
    print('\nPlaying media on Spotify Connect device: \nID: %s \n- %s' % (deviceId, uris.replace(',','\n- ')))
    spotify.PlayerMediaPlayTracks(uris, 0, deviceId)

    print('\nSuccess - media should be playing')

except Exception as ex:

    print("** Exception: %s" % str(ex))
