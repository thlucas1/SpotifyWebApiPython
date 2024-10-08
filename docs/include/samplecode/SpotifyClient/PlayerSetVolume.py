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

    # set the volume for the user's current playback device.
    volumePercent:int = 100
    deviceId:str = None   # use currently playing device
    #deviceId:str = "Web Player (Chrome)" # or device name
    #deviceId:str = "0d1841b0976bae2a3a310dd74c0f3df354899bc8" # or device id
    print('\nSet %d%% volume on Spotify Connect device:\n- "%s" ...' % (volumePercent, str(deviceId)))
    spotify.PlayerSetVolume(volumePercent, deviceId)

    print('\nSuccess - volume was set')

except Exception as ex:

    print("** Exception: %s" % str(ex))
