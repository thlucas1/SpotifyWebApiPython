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

    # play album on the specified Spotify Connect device.
    deviceId:str = None   # use currently playing device
    #deviceId:str = "Web Player (Chrome)" # or device name
    #deviceId:str = "0d1841b0976bae2a3a310dd74c0f3df354899bc8" # or device id
    contextUri:str = 'spotify:album:6vc9OTcyd3hyzabCmsdnwE'  # Album = Welcome to the New
    print('\nPlaying album on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
    spotify.PlayerMediaPlayContext(contextUri, deviceId=deviceId)

    print('\nSuccess - album should be playing')

    # play album starting at track #7 on the specified Spotify Connect device.
    deviceId:str = None   # use currently playing device
    contextUri:str = 'spotify:album:6vc9OTcyd3hyzabCmsdnwE'  # Album = Welcome to the New
    print('\nPlaying album starting at track #7 on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
    spotify.PlayerMediaPlayContext(contextUri, offsetPosition=6, deviceId=deviceId)

    print('\nSuccess - album should be playing')

    # play album starting at track #5 and 25 seconds position on the specified Spotify Connect device.
    deviceId:str = None   # use currently playing device
    contextUri:str = 'spotify:album:6vc9OTcyd3hyzabCmsdnwE'  # Album = Welcome to the New
    print('\nPlaying album starting at track #5 (25 seconds) on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
    spotify.PlayerMediaPlayContext(contextUri, offsetPosition=4, positionMS=25000, deviceId=deviceId)

    print('\nSuccess - album should be playing')

    # play album starting at track id #7 on the specified Spotify Connect device.
    deviceId:str = None   # use currently playing device
    contextUri:str = 'spotify:album:6vc9OTcyd3hyzabCmsdnwE'  # Album = Welcome to the New
    offsetUri:str = 'spotify:track:1kWUud3vY5ij5r62zxpTRy'   # Track = Flawless
    print('\nPlaying album starting at track #7 on Spotify Connect device: \nID: %s \n- %s' % (deviceId, contextUri))
    spotify.PlayerMediaPlayContext(contextUri, offsetUri=offsetUri, deviceId=deviceId)

    print('\nSuccess - album should be playing')

except Exception as ex:

    print("** Exception: %s" % str(ex))
