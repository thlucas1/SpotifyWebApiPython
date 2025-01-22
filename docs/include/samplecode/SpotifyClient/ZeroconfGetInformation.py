from spotifywebapipython import *
from spotifywebapipython.zeroconfapi import *

try:

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # get Spotify zeroconf api action "getInfo" response.
    actionUrl:str = 'http://192.168.1.82:8200/zc?action=getInfo&VERSION=1.0'
    print('\nGetting Spotify zeroconf getInfo response:\n- "%s" ...\n' % actionUrl)
    zcfGetInfo:ZeroconfGetInfo = spotify.ZeroconfGetInformation(actionUrl)
            
    print(zcfGetInfo.ToString())
            
except Exception as ex:

    print("** Exception: %s" % str(ex))
