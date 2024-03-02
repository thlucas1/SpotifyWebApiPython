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
