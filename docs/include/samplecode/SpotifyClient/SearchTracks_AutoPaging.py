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

    # get Spotify catalog information about Tracks that match a keyword string.
    criteria:str = 'Parliament Funkadelic'
    print('\nSearching for Tracks - criteria: "%s" ...\n' % criteria)
    pageObj:SearchResponse = spotify.SearchTracks(criteria, limitTotal=75)

    # display paging details.
    print(str(pageObj))
    print(str(pageObj.Tracks))
    print('\nTracks in this page of results (%d items):' % pageObj.Tracks.ItemsCount)

    # display track details.
    track:Track
    for track in pageObj.Tracks.Items:
        print('- "{name}" ({uri})'.format(name=track.Name, uri=track.Uri))

except Exception as ex:

    print("** Exception: %s" % str(ex))
