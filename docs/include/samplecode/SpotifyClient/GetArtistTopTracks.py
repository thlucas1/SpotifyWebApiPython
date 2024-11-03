from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    CLIENT_ID:str = 'your_client_id'
    CLIENT_SECRET:str = 'your_client_secret'

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify client credentials access token (no scope, public data use only).
    spotify.SetAuthTokenClientCredentials(CLIENT_ID, CLIENT_SECRET)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # get Spotify catalog information about an artist's top tracks by country.
    artistId:str = '6APm8EjxOHSYM5B4i3vT3q'
    print('\nGetting top tracks for artist id "%s" ...\n' % artistId)
    tracks:list[Track] = spotify.GetArtistTopTracks(artistId, 'ES', False)

    track:Track
    for track in tracks:
                
        print(str(track))
        print('')

except Exception as ex:

    print("** Exception: %s" % str(ex))
