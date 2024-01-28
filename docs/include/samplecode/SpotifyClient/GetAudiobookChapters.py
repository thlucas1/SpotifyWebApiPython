from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

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

    # get Spotify catalog information about a audiobook's chapters.
    audiobookId:str = '7iHfbu1YPACw6oZPAFJtqe'  # <- Dune - Author=Frank Herbert
    print('\nGetting list of chapters for audiobook id "%s" ...\n' % audiobookId)
    pageObj:ChapterPageSimplified = spotify.GetAudiobookChapters(audiobookId) 

    # handle pagination, as spotify limits us to a set # of items returned per response.
    while True:

        # display paging details.
        print(str(pageObj))
        print('')
        print('Chapters in this page of results:')

        # display chapter details.
        chapterSimplified:ChapterPageSimplified
        for chapterSimplified in pageObj.Items:
        
            print('- "{name}" ({uri})'.format(name=chapterSimplified.Name, uri=chapterSimplified.Uri))
                    
            # or dump the entire object:
            #print(str(chapterSimplified))
            #print('')

        # anymore page results?
        if pageObj.Next is None:
            # no - all pages were processed.
            break
        else:
            # yes - retrieve the next page of results.
            print('\nGetting next page of %d items ...\n' % (pageObj.Limit))
            pageObj = spotify.GetAudiobookChapters(audiobookId, offset=pageObj.Offset + pageObj.Limit, limit=pageObj.Limit)

except Exception as ex:

    print("** Exception: %s" % str(ex))
