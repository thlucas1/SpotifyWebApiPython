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

    # get Spotify catalog information about an album's tracks.
    albumId:str = '6vc9OTcyd3hyzabCmsdnwE'
    print('\nGetting list of ALL tracks for album id "%s" ...\n' % albumId)
    pageObj:TrackPageSimplified = spotify.GetAlbumTracks(albumId, limitTotal=1000) 

    # display paging details.
    print(str(pageObj))
    print('\nTracks in this page of results (%d items):' % pageObj.ItemsCount)

    # display track details.
    trackSimplified:TrackPageSimplified
    for trackSimplified in pageObj.Items:
        print('- "{name}" ({uri})'.format(name=trackSimplified.Name, uri=trackSimplified.Uri))

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
