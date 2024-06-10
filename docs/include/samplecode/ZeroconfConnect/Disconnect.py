from spotifywebapipython import *
from spotifywebapipython.zeroconfapi import *

try:

    # create Spotify Zeroconf API connection object for the device.
    zconn:ZeroconfConnect = ZeroconfConnect('192.168.1.81', 8200, '/zc', useSSL=False)
            
    # disconnect the device from Spotify Connect.
    print('\nDisconnecting device:%s' % zconn.ToString())
    result:ZeroconfResponse = zconn.Disconnect()
    print('\nResult - %s' % result.ToString())
    print("\nDevice should have been removed from the Spotify Connect device list")
            
except Exception as ex:

    print("** Exception: %s" % str(ex))
