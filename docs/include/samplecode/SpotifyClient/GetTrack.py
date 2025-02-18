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

    # get Spotify catalog information for a single track.
    trackId:str = '1kWUud3vY5ij5r62zxpTRy'
    print('\nGetting details for track "%s" ...\n' % trackId)
    track:Track = spotify.GetTrack(trackId)

    print(str(track))

    print('\nArtists:')
    artist:ArtistSimplified
    for artist in track.Artists:
        print('- "{name}" ({uri})'.format(name=artist.Name, uri=artist.Uri))

    print('')
    print(str(track.Album))

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
