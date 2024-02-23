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

    # get Spotify catalog information about Episodes that match a keyword string.
    criteria:str = 'The LOL Podcast'
    print('\nSearching for Episodes - criteria: "%s" ...\n' % criteria)
    pageObj:SearchResponse = spotify.SearchEpisodes(criteria, limitTotal=75)

    # display paging details.
    print(str(pageObj))
    print(str(pageObj.Episodes))
    print('\nEpisodes in this page of results (%d items):' % pageObj.Episodes.ItemsCount)

    # display episode details.
    episode:EpisodeSimplified
    for episode in pageObj.Episodes.Items:
        print('- "{name}" ({uri})'.format(name=episode.Name, uri=episode.Uri))

except Exception as ex:

    print("** Exception: %s" % str(ex))
