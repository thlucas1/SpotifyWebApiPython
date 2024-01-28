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

    # get Spotify catalog information for a multiple audiobooks.
    audiobookIds:str = '74aydHJKgYz3AIq3jjBSv1,4nfQ1hBJWjD0Jq9sK3YRW8'
    print('\nGetting details for multiple audiobooks: \n- %s \n' % audiobookIds.replace(',','\n- '))
    audiobooks:list[AudiobookSimplified] = spotify.GetAudiobooks(audiobookIds)

    audiobook:AudiobookSimplified
    for audiobook in audiobooks:
                
        print(str(audiobook))
        print('')

except Exception as ex:

    print("** Exception: %s" % str(ex))
