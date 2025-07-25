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

    # get Spotify catalog information about objects that match a keyword string.
    criteria:str = 'Love'
    criteriaType:str = 'album,artist,track,playlist'
    print('\nSearch criteria types: "%s"')
    print('\nSearching for criteria: "%s" ...\n' % criteria)
    searchResp:SearchResponse = spotify.Search(criteria, criteriaType, limitTotal=5)

    # display search results.
    item:SearchResultBase
    print('\nAlbums (%d items):' % searchResp.AlbumsCount)
    for item in searchResp.Albums.Items:
        print('- "{name}" ({uri})'.format(name=item.Name, uri=item.Uri))

    print('\nArtists (%d items):' % searchResp.ArtistsCount)
    for item in searchResp.Artists.Items:
        print('- "{name}" ({uri})'.format(name=item.Name, uri=item.Uri))

    print('\nAudiobooks (%d items):' % searchResp.AudiobooksCount)
    for item in searchResp.Audiobooks.Items:
        print('- "{name}" ({uri})'.format(name=item.Name, uri=item.Uri))

    print('\nEpisodes (%d items):' % searchResp.EpisodesCount)
    for item in searchResp.Episodes.Items:
        print('- "{name}" ({uri})'.format(name=item.Name, uri=item.Uri))

    print('\nPlaylists (%d items):' % searchResp.PlaylistsCount)
    for item in searchResp.Playlists.Items:
        print('- "{name}" ({uri})'.format(name=item.Name, uri=item.Uri))

    print('\nShows (%d items):' % searchResp.ShowsCount)
    for item in searchResp.Shows.Items:
        print('- "{name}" ({uri})'.format(name=item.Name, uri=item.Uri))

    print('\nTracks (%d items):' % searchResp.TracksCount)
    for item in searchResp.Tracks.Items:
        print('- "{name}" ({uri})'.format(name=item.Name, uri=item.Uri))

    print("\nTest Completed")

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
