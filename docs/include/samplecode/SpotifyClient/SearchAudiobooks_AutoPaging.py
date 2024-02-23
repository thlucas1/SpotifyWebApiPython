from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = \
    [
        'user-read-email',
        'user-library-read',
        'user-library-modify',
        'playlist-modify-private',
        'playlist-modify-public'
    ]

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # get Spotify catalog information about Audiobooks that match a keyword string.
    criteria:str = 'Terry Brooks'
    print('\nSearching for Audiobooks - criteria: "%s" ...\n' % criteria)
    pageObj:SearchResponse = spotify.SearchAudiobooks(criteria, limitTotal=75)

    # display paging details.
    print(str(pageObj))
    print(str(pageObj.Audiobooks))
    print('\nAudiobooks in this page of results (%d items):' % pageObj.Audiobooks.ItemsCount)

    # display audiobook details.
    audiobook:Audiobook
    for audiobook in pageObj.Audiobooks.Items:
        print('- "{name}" ({uri})'.format(name=audiobook.Name, uri=audiobook.Uri))

except Exception as ex:

    print("** Exception: %s" % str(ex))
