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

    # get Spotify catalog information about Playlists that match a keyword string.
    criteria:str = 'Daily Mix'
    print('\nSearching for Playlists - criteria: "%s" ...\n' % criteria)
    pageObj:SearchResponse = spotify.SearchPlaylists(criteria, limitTotal=200)

    # get playlists owned by spotify (e.g. content generated for you).
    spotifyOwnedPlaylists:list[PlaylistSimplified] = pageObj.GetSpotifyOwnedPlaylists()

    # sort them by name.
    if len(spotifyOwnedPlaylists) > 0:
        spotifyOwnedPlaylists.sort(key=lambda x: (x.Name or "").lower(), reverse=False)
                
    # display playlist details.
    print('\nPlaylists generated for you by Spotify (%d items):' % len(spotifyOwnedPlaylists))
    playlist:PlaylistSimplified
    for playlist in spotifyOwnedPlaylists:
        print('- "{name}" ({uri})'.format(name=playlist.Name, uri=playlist.Uri))

except Exception as ex:

    print("** Exception: %s" % str(ex))
