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

    # get Spotify catalog information for a multiple chapters.
    chapterIds:str = '0D5wENdkdwbqlrHoaJ9g29,0PMQAsGZ8f9tSTd9moghJs'
    print('\nGetting details for multiple chapters: \n- %s \n' % chapterIds.replace(',','\n- '))
    chapters:list[ChapterSimplified] = spotify.GetChapters(chapterIds)

    chapter:ChapterSimplified
    for chapter in chapters:
                
        print(str(chapter))
        print('')

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
