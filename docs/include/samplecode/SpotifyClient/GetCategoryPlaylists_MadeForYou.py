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
    categoryId:str = '0JQ5DAt0tbjZptfcdMSKl3' # special hidden category id "Made For You"
    print('\nGetting ALL playlists for category "%s" ...\n' % categoryId)
    pageObj:PlaylistPageSimplified
    pageObj, message = spotify.GetCategoryPlaylists(categoryId, limitTotal=1000)

    # display results.
    print('Playlist Results Type: "%s"\n' % str(message))
    print(str(pageObj))
    print('\nPlaylists in this page of results (%d items):' % pageObj.ItemsCount)

    # display playlist details.
    playlist:PlaylistSimplified
    for playlist in pageObj.Items:
        print('- "{name}" ({uri})'.format(name=playlist.Name, uri=playlist.Uri))

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
