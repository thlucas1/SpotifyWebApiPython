from spotifywebapipython import *
from spotifywebapipython.zeroconfapi import *

try:

    # set credentials used to login to Spotify from the device.
    # username is your Spotify username (e.g. 'yourname@gmail.com', '1234567890', etc).
    # loginid is your Spotify canonical login id (e.g. '31l77548798704mns987fdf0986e').
    username = 'YourSpotifyUsername'    
    password = 'YourSpotifyPassword'
    loginid  = 'YourSpotifyLoginId'
    
    # you must copy the librespot `credentials.json` file from the spotifyd cache location
    # directory (e.g. /home/<user>/.cache/spotifyd/credentials.json) to the spotifywebapiPython
    # token storage directory (e.g. ./test/testdata/spotifywebapiPython_librespot_credentials.json).
    # the file must be refreshed if your Spotify password is ever changed.
    
    # create Spotify Zeroconf API connection object for the device.
    zconn:ZeroconfConnect = ZeroconfConnect('192.168.1.81', 8200, '/', useSSL=False, tokenStorageDir='./test/testdata')
            
    # NOTE - do not issue a Disconnect call, as librespot does not implement the Spotify Connect
    # Zeroconf `resetUsers` endpoint; a 404 request error will result if you do.
            
    # connect the device to Spotify Connect on the spotifyd instance.
    print('\nConnecting device:%s' % zconn.ToString())
    result:ZeroconfResponse = zconn.Connect(username, password, loginid)
    print('\nResult - %s' % result.ToString())
    print("\nDevice should be available in the Spotify Connect device list")

except Exception as ex:

    print("** Exception: %s" % str(ex))
