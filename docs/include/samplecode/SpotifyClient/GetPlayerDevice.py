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
    deviceId:str = '973896e76ca8bc1db44407c9e2990d39b189e9de'
    print('\nGetting Spotify Connect player device: \n- ID = "%s" ...\n' % deviceId)
    device:Device = spotify.GetPlayerDevice(deviceId)

    if device is not None:
        print(str(device))

    # get Spotify Connect player device by it's Name value.
    deviceId:str = 'Web Player (Chrome)'
    print('\nGetting Spotify Connect player device: \n- Name = "%s" ...\n' % deviceId)
    device:Device = spotify.GetPlayerDevice(deviceId)

    if device is not None:
        print(str(device))

except Exception as ex:

    print("** Exception: %s" % str(ex))
