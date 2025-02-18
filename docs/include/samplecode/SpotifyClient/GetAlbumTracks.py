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
    print('\nGetting list of tracks for album id "%s" ...\n' % albumId)
    trackPage:TrackPageSimplified = spotify.GetAlbumTracks(albumId) 

    # handle pagination, as spotify limits us to a set # of items returned per response.
    while True:

        # display paging details.
        print(str(trackPage))
        print('')
        print('Tracks in this page of results:')

        # display track details.
        trackSimplified:TrackPageSimplified
        for trackSimplified in trackPage.Items:
        
            print('- "{name}" ({uri})'.format(name=trackSimplified.Name, uri=trackSimplified.Uri))
                    
            # or dump the entire object:
            #print(str(trackSimplified))
            #print('')

        # anymore page results?
        if trackPage.Next is None:
            # no - all pages were processed.
            break
        else:
            # yes - retrieve the next page of results.
            print('\nGetting next page of %d items ...\n' % (trackPage.Limit))
            trackPage = spotify.GetAlbumTracks(albumId, offset=trackPage.Offset + trackPage.Limit, limit=trackPage.Limit)

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
