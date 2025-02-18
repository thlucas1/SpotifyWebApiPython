from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = ['user-read-email','user-library-read']

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # get a list of the albums saved in the current Spotify user's 'Your Library'.
    print('\nGetting saved albums for current user ...\n')
    pageObj:AlbumPageSaved = spotify.GetAlbumFavorites()

    # handle pagination, as spotify limits us to a set # of items returned per response.
    while True:

        print(str(pageObj))
        print('')
        print('Items in this page of results:')

        # display album details.
        albumSaved:AlbumSaved
        for albumSaved in pageObj.Items:
        
            print('- "{name}" ({uri})'.format(name=albumSaved.Album.Name, uri=albumSaved.Album.Uri))

        # anymore page results?
        if pageObj.Next is None:
            # no - all pages were processed.
            break
        else:
            # yes - retrieve the next page of results.
            print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
            pageObj = spotify.GetAlbumFavorites(offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)
         
except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
