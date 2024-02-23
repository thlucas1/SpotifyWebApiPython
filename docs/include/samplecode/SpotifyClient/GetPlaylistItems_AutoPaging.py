from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = ['user-read-email','user-library-read']

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # get full details of the items of a playlist owned by a Spotify user.
    playlistId:str = '5v5ETK9WFXAnGQ3MRubKuE'
    print('\nGetting ALL item details for playlist "%s" ...\n' % playlistId)
    pageObj:PlaylistPage = spotify.GetPlaylistItems(playlistId, limitTotal=1000)

    # display paging details.
    print(str(pageObj))
    print('\nTrack Item results: (%d items)' % pageObj.ItemsCount)

    # display track details.
    playlistTrack:PlaylistTrack
    for playlistTrack in pageObj.Items:
        print('- "{name}" ({uri}), added on {added} '.format(name=playlistTrack.Track.Name, uri=playlistTrack.Track.Uri, added=playlistTrack.AddedAt))

except Exception as ex:

    print("** Exception: %s" % str(ex))
