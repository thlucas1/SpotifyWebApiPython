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

    # get Spotify catalog information for several artists.
    artistIds:str = '6APm8EjxOHSYM5B4i3vT3q,22sg0OT5BG5eWLBN97WPIZ,1LmsXfZSt1nutb8OCvt00G'
    print('\nGetting details for multiple artists: \n- %s \n' % artistIds.replace(',','\n- '))
    artists:list[Artist] = spotify.GetArtists(artistIds)

    artist:Artist
    for artist in artists:
                
        print(str(artist))
        print('')

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
