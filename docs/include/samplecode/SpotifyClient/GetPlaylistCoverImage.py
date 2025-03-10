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

    # get the current image details associated with a specific playlist.
    playlistId:str = '4yptcTKnXjCu3V92tVVafS'
    print('\nGetting cover image details for playlist id "%s" ...\n' % playlistId)
    imageObj:ImageObject = spotify.GetPlaylistCoverImage(playlistId)

    # download the cover image to the file system.
    outputPath:str = "./test/testdata/downloads/playlist_%s{dotfileextn}" % (playlistId)
    print('\nGetting cover image file:\n"%s"' % outputPath)
    spotify.GetCoverImageFile(imageObj.Url, outputPath)

    print(str(imageObj))

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
