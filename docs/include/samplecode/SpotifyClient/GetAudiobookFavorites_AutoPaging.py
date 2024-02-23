from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = ['user-read-email','user-library-read']

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # get a list of the audiobooks saved in the current Spotify user's 'Your Library'.
    print('\nGetting ALL saved audiobooks for current user ...\n')
    pageObj:AudiobookPageSimplified = spotify.GetAudiobookFavorites(limitTotal=1000)

    # display paging details.
    print(str(pageObj))
    print('\nAudiobooks in this page of results (%d items):' % pageObj.ItemsCount)

    # display audiobook details.
    audiobook:AudiobookSimplified
    for audiobook in pageObj.Items:
        print('- "{name}" ({uri})'.format(name=audiobook.Name, uri=audiobook.Uri))

except Exception as ex:

    print("** Exception: %s" % str(ex))
