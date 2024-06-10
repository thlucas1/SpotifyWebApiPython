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
            
    # disconnect the device from Spotify Connect.
    print('\nDisconnecting device:%s' % zconn.ToString())
    result:ZeroconfResponse = zconn.Disconnect()
    print('\nResult - %s' % result.ToString())
    print("\nDevice should have been removed from the Spotify Connect device list")
            
    # connect the device to Spotify Connect, which should make it known to any available
    # Spotify Connect player clients.
    print('\nConnecting device:%s' % zconn.ToString())
    result:ZeroconfResponse = zconn.Connect(username, password)
    print('\nResult - %s' % result.ToString())
    print("\nDevice should be available in the Spotify Connect device list")

except Exception as ex:

    print("** Exception: %s" % str(ex))
