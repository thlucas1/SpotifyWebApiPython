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

    # get a list of the episodes saved in the current Spotify user's 'Your Library'.
    print('\nGetting ALL saved episodes for current user ...\n')
    pageObj:EpisodePageSaved = spotify.GetEpisodeFavorites(limitTotal=1000)

    # display paging details.
    print(str(pageObj))
    print('\nEpisodes in this page of results (%d items):' % pageObj.ItemsCount)

    # display episode details.
    episodeSaved:EpisodeSaved
    for episodeSaved in pageObj.Items:
        print('- "{name}" ({uri})'.format(name=episodeSaved.Episode.Name, uri=episodeSaved.Episode.Uri))

except Exception as ex:

    print("** Exception: %s" % str(ex))
