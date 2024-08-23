from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = ['user-read-email','user-library-read','user-read-currently-playing']

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # get Spotify catalog information for the nowplaying audiobook.
    print('\nGetting details for nowplaying audiobook ...\n')
    audiobook:Audiobook = spotify.GetAudiobook()

    print(str(audiobook))
    print('')
            
    # prepare to retrieve all chapters.
    pageObj:ChapterPageSimplified = audiobook.Chapters
            
    # handle pagination, as spotify limits us to a set # of items returned per response.
    while True:

        # display paging details.
        print(str(pageObj))
        print('')
        print('Chapters in this page of results:')

        # display chapter details.
        chapterSimplified:ChapterSimplified
        for chapterSimplified in pageObj.Items:
        
            print('- "{name}" ({uri})'.format(name=chapterSimplified.Name, uri=chapterSimplified.Uri))

        # anymore page results?
        if pageObj.Next is None:
            # no - all pages were processed.
            break
        else:
            # yes - retrieve the next page of results.
            print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
            pageObj = spotify.GetAudiobookChapters(audiobook.Id, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

except Exception as ex:

    print("** Exception: %s" % str(ex))
