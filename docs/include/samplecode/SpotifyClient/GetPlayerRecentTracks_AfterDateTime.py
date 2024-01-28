from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = \
    [
        'user-read-recently-played',
        'user-read-email',
    ]

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # get all tracks played after UTC date 2024-01-25T21:34:16.821Z (1706218456821)
    afterMS:int = 1706218456821

    # get tracks from current user's recently played tracks.
    print('\nGetting recently played tracks for current user ...\n')
    pageObj:PlayHistoryPage = spotify.GetPlayerRecentTracks(after=afterMS)

    # handle pagination, as spotify limits us to a set # of items returned per response.
    while True:

        # display paging details.
        print(str(pageObj))
        print('')
        print('Tracks in this page of results:')
                
        # display history details.
        history:PlayHistory
        for history in pageObj.Items:
        
            print('- {played_at} {played_atMS}: "{name}" ({uri})'.format(played_at=history.PlayedAt, played_atMS=history.PlayedAtMS, name=history.Track.Name, uri=history.Track.Uri))

        # anymore page results?
        if pageObj.Next is None:
            # no - all pages were processed.
            break
        else:
            # yes - retrieve the next page of results.
            print('\nGetting next page of items ...\n')
            pageObj = spotify.GetPlayerRecentTracks(after=pageObj.CursorAfter, limit=pageObj.Limit)

except Exception as ex:

    print("** Exception: %s" % str(ex))
