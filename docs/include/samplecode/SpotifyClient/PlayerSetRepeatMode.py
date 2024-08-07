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

    # set repeat mode CONTEXT for the user's current playback device.
    deviceId:str = None   # use currently playing device
    #deviceId:str = "Web Player (Chrome)" # or device name
    #deviceId:str = "0d1841b0976bae2a3a310dd74c0f3df354899bc8" # or device id
    print('\nSet repeat mode CONTEXT for Spotify Connect device:\n- "%s" ...' % (str(deviceId)))
    spotify.PlayerSetRepeatMode('context', deviceId)

    print('\nSuccess - repeat mode CONTEXT was set')

    # set repeat mode TRACK for the user's current playback device.
    deviceId:str = None   # use currently playing device
    print('\nSet repeat mode to single track for Spotify Connect device:\n- "%s" ...' % (str(deviceId)))
    spotify.PlayerSetRepeatMode('track', deviceId)

    print('\nSuccess - repeat mode TRACK was set')

    # set repeat mode OFF for the user's current playback device.
    deviceId:str = None   # use currently playing device
    print('\nSet repeat mode OFF for Spotify Connect device:\n- "%s" ...' % (str(deviceId)))
    spotify.PlayerSetRepeatMode('off', deviceId)

    print('\nSuccess - repeat mode OFF was set')

except Exception as ex:

    print("** Exception: %s" % str(ex))
