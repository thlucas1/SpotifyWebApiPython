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

    # get Spotify catalog information about an artist's albums.
    artistId:str = '6APm8EjxOHSYM5B4i3vT3q'
    includeGroups:str = 'album,single,appears_on,compilation'
    print('\nGetting albums for artist id "%s" ...\n' % artistId)
    pageObj:AlbumPageSimplified = spotify.GetArtistAlbums(artistId, includeGroups, limit=50)

    # handle pagination, as spotify limits us to a set # of items returned per response.
    while True:

        # display paging details.
        print(str(pageObj))
        print('')
        print('Albums in this page of results:')

        # display album details.
        albumSimplified:AlbumSimplified
        for albumSimplified in pageObj.Items:
        
            print('- "{name}" ({uri})'.format(name=albumSimplified.Name, uri=albumSimplified.Uri))

        # anymore page results?
        if pageObj.Next is None:
            # no - all pages were processed.
            break
        else:
            # yes - retrieve the next page of results.
            print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
            pageObj = spotify.GetArtistAlbums(artistId, includeGroups, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

except Exception as ex:

    print("** Exception: %s" % str(ex))
