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

    # get audio features for multiple tracks based on their Spotify IDs.
    trackIds:str = '1kWUud3vY5ij5r62zxpTRy,4eoYKv2kDwJS7gRGh5q6SK'
    print('\nGetting audio features for multiple tracks: \n- %s \n' % trackIds.replace(',','\n- '))
    items:list[AudioFeatures] = spotify.GetTracksAudioFeatures(trackIds)

    audioFeatures:AudioFeatures
    for audioFeatures in items:
                
        print(str(audioFeatures))
        print('')

except Exception as ex:

    print("** Exception: %s" % str(ex))

finally:

    # shut down zeroconf directory browser and dispose of all resources.
    if (spotify is not None):
        spotify.Dispose()
