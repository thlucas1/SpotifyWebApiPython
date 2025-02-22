from spotifywebapipython import *
from spotifywebapipython.models import *

try:

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

    # get Spotify track recommendations for specified criteria.
    print('\nGetting track recommendations - I wanna rock!\n')
    recommendations:TrackRecommendations = spotify.GetTrackRecommendations(seedGenres='rock,hard-rock,rock-n-roll',minLoudness=-9.201,minTimeSignature=4,minEnergy=0.975)

    print(str(recommendations))
    print('')

    seed:RecommendationSeed
    for seed in recommendations.Seeds:
                
        print(str(seed))
        print('')

    print('Recommended Tracks:')
    track:Track
    for track in recommendations.Tracks:
                
        print('- "{name}" ({uri})'.format(name=track.Name, uri=track.Uri))
        #print(str(track))

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
