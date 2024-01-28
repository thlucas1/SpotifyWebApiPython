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

    # get Spotify catalog information for a single chapter.
    chapterId:str = '0D5wENdkdwbqlrHoaJ9g29'
    print('\nGetting details for chapter id "%s" ...\n' % chapterId)
    chapter:Chapter = spotify.GetChapter(chapterId)

    print(str(chapter))
    print('')

    print(str(chapter.Audiobook))

except Exception as ex:

    print("** Exception: %s" % str(ex))
