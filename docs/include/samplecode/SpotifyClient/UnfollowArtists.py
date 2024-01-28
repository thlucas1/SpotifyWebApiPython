from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = \
    [
        'user-follow-modify',
        'user-read-email',
    ]

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # remove the current user as a follower of one or more artists.
    ids:str = '2CIMQHirSU0MQqyYHq0eOx,1IQ2e1buppatiN1bxUVkrk'
    print('\nStop following these artists:\n- %s\n' % (ids.replace(',','\n- ')))
    spotify.UnfollowArtists(ids)
            
    print('Success - artists are now unfollowed')

except Exception as ex:

    print("** Exception: %s" % str(ex))
