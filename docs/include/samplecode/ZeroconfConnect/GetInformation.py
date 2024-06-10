from spotifywebapipython import *
from spotifywebapipython.zeroconfapi import *

try:

    # set credentials used to login to Spotify from the device.
    # username argument accepts either a username (e.g. 'yourname@gmail.com')
    # or canonical user id (e.g. '31l77548798704mns987fdf0986e')
    username = 'YourSpotifyUsername' 
    password = 'YourSpotifyPassword'
    
    # create Spotify Zeroconf API connection object for the device.
    zconn:ZeroconfConnect = ZeroconfConnect('192.168.1.81', 8200, '/zc', useSSL=False)
            
    # get Spotify Zeroconf information for the device.
    print('\nGetting Spotify Zeroconf information for device:%s' % zconn.ToString())
    result:ZeroconfGetInfo = zconn.GetInformation()
    print('\nResult - %s' % result.ToString())

except Exception as ex:

    print("** Exception: %s" % str(ex))
