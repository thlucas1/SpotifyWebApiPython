from spotifywebapipython import *
from spotifywebapipython.models import *

try:

    # this sample requires an authorization token, as it requires security scope to accesses user data.

    CLIENT_ID:str = 'your_client_id'
    SPOTIFY_SCOPES:list = \
    [
        'user-follow-read',
        'user-read-email',
    ]

    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient()

    # generate a spotify authorization code with PKCE access token (with scope, private and public data use).
    spotify.SetAuthTokenAuthorizationCodePKCE(CLIENT_ID, SPOTIFY_SCOPES)
    print('\nAuth Token:\n Type="%s"\n Scope="%s"' % (spotify.AuthToken.AuthorizationType, str(spotify.AuthToken.Scope)))
    print('\nUser:\n DisplayName="%s"\n EMail="%s"' % (spotify.UserProfile.DisplayName, spotify.UserProfile.EMail))

    # check to see if the current user is following one or more artists.
    ids:str = '2CIMQHirSU0MQqyYHq0eOx,1IQ2e1buppatiN1bxUVkrk'
    print('\nChecking if these artists are followed by me:\n- %s\n' % (ids.replace(',','\n- ')))
    result:dict = spotify.CheckArtistsFollowing(ids)
            
    print('Results:')
    for key in result.keys():
        print('- %s = %s' % (key, result[key]))

    # check to see if the current user is following nowplaying artist.
    print('\nChecking if nowplaying artist is followed by me ...')
    result:dict = spotify.CheckArtistsFollowing()
            
    print('Results:')
    for key in result.keys():
        print('- %s = %s' % (key, result[key]))

except Exception as ex:

    print("** Exception: %s" % str(ex))
