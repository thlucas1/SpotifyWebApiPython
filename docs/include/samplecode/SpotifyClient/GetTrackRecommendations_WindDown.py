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

    # get Spotify track recommendations for specified criteria.
    print('\nGetting track recommendations - Wind Down!\n')
    recommendations:TrackRecommendations = spotify.GetTrackRecommendations(seedArtists='3jdODvx7rIdq0UGU7BOVR3',seedGenres='piano',maxEnergy=0.175)

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
