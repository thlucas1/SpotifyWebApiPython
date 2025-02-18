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

    # get Spotify catalog information for a single show.
    showId:str = '6E1u3kxII5CbbFR4VObax4'
    print('\nGetting details for show id "%s" ...\n' % showId)
    show:Show = spotify.GetShow(showId)

    print(str(show))
    print('')
            
    # prepare to retrieve all episodes.
    pageObj:EpisodePageSimplified = show.Episodes
            
    # handle pagination, as spotify limits us to a set # of items returned per response.
    while True:

        # display paging details.
        print(str(pageObj))
        print('')
        print('Episodes in this page of results:')

        # display episode details.
        episodeSimplified:EpisodeSimplified
        for episodeSimplified in pageObj.Items:
        
            print('- "{name}" ({uri})'.format(name=episodeSimplified.Name, uri=episodeSimplified.Uri))

        # anymore page results?
        if pageObj.Next is None:
            # no - all pages were processed.
            break
        else:
            # yes - retrieve the next page of results.
            print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
            pageObj = spotify.GetShowEpisodes(show.Id, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
