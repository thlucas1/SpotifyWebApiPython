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

    # get Spotify catalog information about Albums that match a keyword string.
    criteria:str = 'Welcome to the New'
    print('\nSearching for Albums - criteria: "%s" ...\n' % criteria)
    searchResponse:SearchResponse = spotify.SearchAlbums(criteria, limit=25)

    # display search response details.
    print(str(searchResponse))
    print('')

    # save initial search response total, as search next page response total 
    # will change with each page retrieved.  this is odd behavior, as it seems
    # that the spotify web api is returning a new result set each time rather 
    # than working off of a cached result set.
    pageObjInitialTotal:int = searchResponse.Albums.Total

    # handle pagination, as spotify limits us to a set # of items returned per response.
    while True:
                
        # only display album results for this example.
        pageObj:AlbumPageSimplified = searchResponse.Albums

        # display paging details.
        print(str(pageObj))
        print('')
        print('Albums in this page of results:')

        # display album details.
        album:AlbumSimplified
        for album in pageObj.Items:
            print('- "{name}" ({uri})'.format(name=album.Name, uri=album.Uri))
         
        # for testing - don't return 1000 results!  
        # comment the following 3 lines of code if you want ALL results.
        if pageObj.Offset + pageObj.Limit >= 75:
            print('\n*** Stopping paging loop after 75 entries for testing.')
            break

        # anymore page results?
        if (pageObj.Next is None) or ((pageObj.Offset + pageObj.Limit) > pageObjInitialTotal):
            # no - all pages were processed.
            break
        else:
            # yes - retrieve the next page of results.
            print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
            searchResponse = spotify.SearchAlbums(criteria, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

except Exception as ex:

    print("** Exception: %s" % str(ex))
