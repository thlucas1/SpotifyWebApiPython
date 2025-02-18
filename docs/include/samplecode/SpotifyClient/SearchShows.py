from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = \
    [
        'user-read-email',
        'user-library-read',
        'user-library-modify',
        'playlist-modify-private',
        'playlist-modify-public'
    ]

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # get Spotify catalog information about Shows that match a keyword string.
    # note - use an Authorization type of token or the `market` argument for this
    # method, otherwise the item result are all null.
    criteria:str = 'Joe Rogan'
    print('\nSearching for Shows - criteria: "%s" ...\n' % criteria)
    searchResponse:SearchResponse = spotify.SearchShows(criteria, limit=25)

    # display search response details.
    print(str(searchResponse))
    print('')

    # save initial search response total, as search next page response total 
    # will change with each page retrieved.  this is odd behavior, as it seems
    # that the spotify web api is returning a new result set each time rather 
    # than working off of a cached result set.
    pageObjInitialTotal:int = searchResponse.Shows.Total

    # handle pagination, as spotify limits us to a set # of items returned per response.
    while True:
                
        # only display show results for this example.
        pageObj:ShowPageSimplified = searchResponse.Shows

        # display paging details.
        print(str(pageObj))
        print('\nShows in this page of results:')

        # display show details.
        show:ShowSimplified
        for show in pageObj.Items:
            print('- "{name}" ({uri})'.format(name=show.Name, uri=show.Uri))
         
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
            searchResponse = spotify.SearchShows(criteria, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
