from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = \
    [
        'playlist-modify-private',
        'playlist-modify-public',
        'ugc-image-upload',
        'user-library-modify',
        'user-library-read',
        'user-read-email',
        'user-read-playback-position',
    ]

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # get a list of Spotify playlists tagged with a particular category.
    categoryId:str = 'toplists'
    print('\nGetting playlists for category "%s" ...\n' % categoryId)
    pageObj:PlaylistPageSimplified
    pageObj, message = spotify.GetCategoryPlaylists(categoryId)

    # handle pagination, as spotify limits us to a set # of items returned per response.
    while True:

        # display paging details.
        print('Playlist Results Type: "%s"\n' % str(message))
        print(str(pageObj))
        print('')
        print('Playlists in this page of results:')

        # display playlist details.
        playlist:PlaylistSimplified
        for playlist in pageObj.Items:
        
            print('- "{name}" ({uri})'.format(name=playlist.Name, uri=playlist.Uri))
                    
            # use the following to display all object properties.
            #print(str(playlist))
            #print('')
         
        # anymore page results?
        if pageObj.Next is None:
            # no - all pages were processed.
            break
        else:
            # yes - retrieve the next page of results.
            print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
            pageObj, message = spotify.GetCategoryPlaylists(categoryId, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
