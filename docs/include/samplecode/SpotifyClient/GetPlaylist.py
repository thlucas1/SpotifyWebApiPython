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

    # get a playlist owned by a Spotify user.
    playlistId:str = '5v5ETK9WFXAnGQ3MRubKuE'
    print('\nGetting details for playlist "%s" ...\n' % playlistId)
    playlist:Playlist = spotify.GetPlaylist(playlistId)

    print(str(playlist))
    print('')

    print(str(playlist.Tracks))

    print('\nTracks:')
    playlistTrack:PlaylistTrack
    for playlistTrack in playlist.Tracks.Items:
        print('- "{name}" ({uri})'.format(name=playlistTrack.Track.Name, uri=playlistTrack.Track.Uri))

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
