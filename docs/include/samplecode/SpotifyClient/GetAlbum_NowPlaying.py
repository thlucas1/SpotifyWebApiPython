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

    # get Spotify catalog information for nowplaying album.
    print('\nGetting details for nowplaying Album ...\n')
    album:Album = spotify.GetAlbum()
            
    print(str(album))

    print('\nArtists:')
    artist:ArtistSimplified
    for artist in album.Artists:
        print('- "{name}" ({uri})'.format(name=artist.Name, uri=artist.Uri))

    print('\nTracks:')
    track:TrackSaved
    for track in album.Tracks.Items:
        print('- "{name}" ({uri})'.format(name=track.Name, uri=track.Uri))

except Exception as ex:

    print("** Exception: %s" % str(ex))
