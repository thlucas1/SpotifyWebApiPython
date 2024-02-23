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

    # get a list of new album releases featured in Spotify.
    print('\nGetting list of ALL new album releases featured in Spotify ...\n')
    pageObj:AlbumPageSimplified = spotify.GetAlbumNewReleases(limitTotal=1000)

    # display results.
    print(str(pageObj))
    print('\nAlbums in this page of results (%d items):' % pageObj.ItemsCount)

    # display album details.
    albumSimplified:AlbumSimplified
    for albumSimplified in pageObj.Items:
        print('- "{name}" ({uri})'.format(name=albumSimplified.Name, uri=albumSimplified.Uri))

except Exception as ex:

    print("** Exception: %s" % str(ex))
