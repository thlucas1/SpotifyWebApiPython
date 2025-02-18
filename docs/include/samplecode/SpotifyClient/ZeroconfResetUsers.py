from spotifywebapipython import *
from spotifywebapipython.zeroconfapi import *

try:

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # get Spotify zeroconf api action "resetUsers" response.
    actionUrl:str = 'http://192.168.1.82:8200/zc?action=resetUsers&VERSION=1.0'
    print('\nGetting Spotify zeroconf resetUsers response:\n- "%s" ...\n' % actionUrl)
    zcfResponse:ZeroconfResponse = spotify.ZeroconfResetUsers(actionUrl)
                        
    print(zcfResponse.ToString())
            
except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
