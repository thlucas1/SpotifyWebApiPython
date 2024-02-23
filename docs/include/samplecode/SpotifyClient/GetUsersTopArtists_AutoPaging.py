from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = \
    [
        'user-read-email',
        'user-top-read',
    ]

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # get current user's top artists based on calculated affinity.
    affinity:str = 'long_term'
    print('\nGetting ALL current user top artists for "%s" affinity ...\n' % affinity)
    pageObj:ArtistPage = spotify.GetUsersTopArtists(affinity, limitTotal=1000)

    # display paging details.
    print(str(pageObj))
    print('\nArtists in this page of results (%d items):' % pageObj.ItemsCount)

    # display artist details.
    artist:Artist
    for artist in pageObj.Items:
        print('- "{name}" ({uri})'.format(name=artist.Name, uri=artist.Uri))

except Exception as ex:

    print("** Exception: %s" % str(ex))
