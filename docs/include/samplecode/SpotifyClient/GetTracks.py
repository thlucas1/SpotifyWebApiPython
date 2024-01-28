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

    # get Spotify catalog information for a multiple tracks.
    trackIds:str = '1kWUud3vY5ij5r62zxpTRy,4eoYKv2kDwJS7gRGh5q6SK'
    print('\nGetting details for multiple tracks: \n- %s \n' % trackIds.replace(',','\n- '))
    tracks:list[Track] = spotify.GetTracks(trackIds)

    track:Track
    for track in tracks:
                
        print(str(track))

        print('\nArtist(s):')
        for artist in track.Artists:
            print('- "{name}" ({uri})'.format(name=artist.Name, uri=artist.Uri))

        print('')
        print(str(track.Album))
        print('')

except Exception as ex:

    print("** Exception: %s" % str(ex))
