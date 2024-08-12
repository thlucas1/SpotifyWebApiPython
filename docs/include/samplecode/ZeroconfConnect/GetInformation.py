from spotifywebapipython import *
from spotifywebapipython.zeroconfapi import *

try:

    # create Spotify Zeroconf API connection object for the device.
    zconn:ZeroconfConnect = ZeroconfConnect('192.168.1.81', 8200, '/zc', useSSL=False, tokenStorageDir='./test/testdata')
            
    # get Spotify Zeroconf information for the device.
    print('\nGetting Spotify Zeroconf information for device:%s' % zconn.ToString())
    result:ZeroconfGetInfo = zconn.GetInformation()
    print('\nResult - %s' % result.ToString())

except Exception as ex:

    print("** Exception: %s" % str(ex))
