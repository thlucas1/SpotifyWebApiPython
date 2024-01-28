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

    # get Spotify catalog information for a single audiobook.
    audiobookId:str = '7iHfbu1YPACw6oZPAFJtqe'
    print('\nGetting details for audiobook id "%s" ...\n' % audiobookId)
    audiobook:Audiobook = spotify.GetAudiobook(audiobookId)

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
