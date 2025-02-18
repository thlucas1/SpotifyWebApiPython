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

    # get Spotify catalog information about a show's episodes.
    showId:str = '6E1u3kxII5CbbFR4VObax4'
    print('\nGetting list of ALL episodes for show id "%s" ...\n' % showId)
    pageObj:EpisodePageSimplified = spotify.GetShowEpisodes(showId, limitTotal=1000) 

    # display paging details.
    print(str(pageObj))
    print('\nEpisodes in this page of results (%d items):' % pageObj.ItemsCount)

    # display episode details.
    episodeSimplified:EpisodePageSimplified
    for episodeSimplified in pageObj.Items:
        print('- "{name}" ({uri})'.format(name=episodeSimplified.Name, uri=episodeSimplified.Uri))

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
