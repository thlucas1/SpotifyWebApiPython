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

    # create new spotify client instance, passing the Spotify Connect user context and discovery timeout.
    spotify:SpotifyClient = SpotifyClient(
        spotifyConnectUsername="yourSpotifyUsername", # (e.g. 'yourname@gmail.com', '1234567890', etc)
        spotifyConnectPassword="yourSpotifyPassword",
        spotifyConnectLoginId="yourSpotifyLoginId",   # (e.g. '31l77548798704mns987fdf0986e')
        spotifyConnectDiscoveryTimeout=1.5,
        tokenStorageDir='./yourTokenStorageDir',
    )

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # get information about all available Spotify Connect player devices.
    print('\nRetrieving Spotify Connect player devices')
    result:SpotifyConnectDevices = spotify.GetSpotifyConnectDevices()

    # log device summary.
    print('\nDevice Summary:')
    device:Device
    for device in result.GetDeviceList():
        print('- "%s"' % device.SelectItemNameAndId)
        print(' SelectItemNameAndId = "%s"' % device.SelectItemNameAndId)
        print(' GetIdFromSelectItem = "%s"' % Device.GetIdFromSelectItem(device.SelectItemNameAndId))
        print(' GetNameFromSelectItem = "%s"' % Device.GetNameFromSelectItem(device.SelectItemNameAndId))
    
    # log device details.
    print('\nDevice Details:\n')
    device:SpotifyConnectDevice
    for device in result:
        print(str(device))
        print('')

    # get cached configuration, refreshing from device if needed.
    result:SpotifyConnectDevices = spotify.GetSpotifyConnectDevices(refresh=False)    
    print("\nCached configuration (count): %d" % result.ItemsCount)

    # get cached configuration directly from the configuration manager dictionary.
    if "GetSpotifyConnectDevices" in spotify.ConfigurationCache:
        result:SpotifyConnectDevices = spotify.ConfigurationCache["GetSpotifyConnectDevices"]
        print("\nCached configuration direct access (count): %d" % result.ItemsCount)

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
