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

    # get Spotify catalog information for a single album.
    albumId:str = '6vc9OTcyd3hyzabCmsdnwE'
    print('\nGetting details for Album "%s" ...\n' % albumId)
    album:Album = spotify.GetAlbum(albumId)
            
    print(str(album))

    print('\nArtists:')
    artist:ArtistSimplified
    for artist in album.Artists:
        print('- "{name}" ({uri})'.format(name=artist.Name, uri=artist.Uri))

    print('\nTracks:')
    track:TrackSaved
    for track in album.Tracks.Items:
        print('- "{name}" ({uri})'.format(name=track.Name, uri=track.Uri))

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
