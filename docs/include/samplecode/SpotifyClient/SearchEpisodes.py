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

    # get Spotify catalog information about episodes that match a keyword string.
    criteria:str = 'The LOL Podcast'
    criteriaType:str = 'episode'
    print('\nSearching for episodes - criteria: "%s" ...\n' % criteria)
    searchResponse:SearchResponse = spotify.Search(criteria, criteriaType, limit=50)

    # display search response details.
    print(str(searchResponse))
    print('')

    # save initial search response total, as search next page response total 
    # will change with each page retrieved.  this is odd behavior, as it seems
    # that the spotify web api is returning a new result set each time rather 
    # than working off of a cached result set.
    pageObjInitialTotal:int = searchResponse.Episodes.Total

    # handle pagination, as spotify limits us to a set # of items returned per response.
    while True:

        # only display episode results for this example.
        pageObj:EpisodePageSimplified = searchResponse.Episodes

        # display paging details.
        print(str(pageObj))
        print('')
        print('Episodes in this page of results:')

        # display episode details.
        episode:EpisodeSimplified
        for episode in pageObj.Items:
        
            print('- "{name}" ({uri})'.format(name=episode.Name, uri=episode.Uri))
         
        # anymore page results?
        if (pageObj.Next is None) or ((pageObj.Offset + pageObj.Limit) > pageObjInitialTotal):
            # no - all pages were processed.
            break
        else:
            # yes - retrieve the next page of results.
            print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
            searchResponse = spotify.Search(criteria, criteriaType, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

except Exception as ex:

    print("** Exception: %s" % str(ex))
