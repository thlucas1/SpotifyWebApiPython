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

    # get Spotify catalog information for a multiple shows.
    showIds:str = '6kAsbP8pxwaU2kPibKTuHE,5yX0eiyk7OVq1TpNt8Owkh,6m5al8OnkyVCunFq56qwRE,6E1u3kxII5CbbFR4VObax4'
    print('\nGetting details for multiple shows: \n- %s \n' % showIds.replace(',','\n- '))
    shows:list[ShowSimplified] = spotify.GetShows(showIds)

    show:ShowSimplified
    for show in shows:
                
        print(str(show))
        print('')

except Exception as ex:

    print("** Exception: %s" % str(ex))
