from spotifywebapipython import *
from spotifywebapipython.zeroconfapi import *
from spotifywebapipython.const import SPOTIFY_DESKTOP_APP_CLIENT_ID

try:

    # more information on how to run Python scripts can be found at:
    # https://www.theknowledgeacademy.com/blog/how-to-run-python-scripts/
    
    # you will need to install the SpotifyWebApiPython requirement in order to run this
    # script.  Use the following PIP command to do so:
    # -> pip install spotifywebapiPython
    
    # set the following user-specific input parameters prior to running this script.
    
    # Parameter: "tokenStorageDir"
    # Contains the fully-qualified directory path to the location of the Home Assistant
    # SpotifyPlus custom component data directory.  This directory is where the Token Cache 
    # file (e.g. "tokens.json") is located.  You can use a temporary local path for this 
    # if you like - you would then need to copy the contents to your Home Assistant server
    # once the script is complete.
    tokenStorageDir:str = '/config/custom_components/spotifyplus/data'

    # Parameter: "tokenProfileId"
    # Contains your Spotify login id, in canonical format.
    # This value can be found by logging into the Spotify Developer web-site, and using the
    # "Get Current Users Profile" page to retrieve the "id" value (via "Try It" button).
    # This value is also the ending portion of your Spotify User URI (e.g. "spotify:user:xxx"
    # Spotify Developer web-site, Get Current Users Profile page:
    # https://developer.spotify.com/documentation/web-api/reference/get-current-users-profile
    tokenProfileId:str = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxx'

    # set token scope(s).
    SPOTIFY_SCOPES:list = \
    [
        'streaming',
    ]
            
    # set token generator parameters.
    tokenProviderId:str = 'SpotifyWebApiAuthCodePkce'
    redirectUriHost:str = '127.0.0.1'
    redirectUriPort:int = 4381
    redirectUriPath:str = '/login'
    forceAuthorize:bool = False

    print('-------------------------------------------------------------------------------')
    print('SpotifyPlus OAuth2 Authorization Token Updater for Spotify - v1.0')
    print('-------------------------------------------------------------------------------')
    print('')
    print('This process will update the OAuth2 authorization token cache file that is used')
    print('by the Home Assistant SpotifyPlus integration.  The integration uses OAuth2')
    print('secure token processing for Spotify Connect devices that utilize the')
    print('"authorization_code" token type (e.g. Sonos devices).')
    print('')
    print('You will be prompted to login to Spotify and authorize the "Allow Spotify to')
    print('connect to: Spotify for Desktop" request.')
    print('This access is used only for activating Spotify Connect devices that utilize the')
    print('"authorization_code" token type.')
    print('')
    print('You will need to repeat this process for each Spotify User account that you')
    print('will be using with the HA SpotifyPlus integration.')
    print('')
    print('** NOTE: Spotify login credentials are not saved as part of this process; only')
    print('** the token information returned by the OAuth2 process is stored in the')
    print('** SpotifyPlus Token Cache file located on your Home Assistant server.')

    print('')
    print('Do you want to proceed?')
    print('Enter "Y" + ENTER to proceed, any other key + ENTER to cancel ...')
    choice = input("> ")
    if (choice != 'y') and (choice != 'Y'):
        exit(4)

    print('-------------------------------------------------------------------------------\n')
    print('Before continuing, please ensure that the following are correct; please refer')
    print('to the script comments for what these variables are:')
    print('- tokenStorageDir => %s' % tokenStorageDir)
    print('- tokenProfileId  => %s' % tokenProfileId)

    print('')
    print('Are the above values correct?')
    print('If not, then cancel the script and modify the incorrect value(s).')
    print('Enter "Y" + ENTER to proceed, any other key + ENTER to cancel ...')
    choice = input("> ")
    if (choice != 'y') and (choice != 'Y'):
        exit(4)

    print('-------------------------------------------------------------------------------\n')
    print('We are now ready to begin the Spotify authorization process.')
    print('')
    print('A link may be displayed following this message asking you to copy and paste the')
    print('link into a new browser window / tab to authorize the request via the Spotify')
    print('Authorization web-site.  You only need to do this if a browser window (or tab)')
    print('does not automatically open, prompting you to authorize the request.')
    print('')
    print('You have 2 minutes to authorize the request before a timeout is reached, and')
    print('the authorization request is cancelled.')

    print('')
    print('Do you want to proceed?')
    print('Enter "Y" + ENTER to proceed, any other key + ENTER to cancel ...')
    choice = input("> ")
    if (choice != 'y') and (choice != 'Y'):
        exit(4)
    
    # create new spotify client instance.
    spotify:SpotifyClient = SpotifyClient(tokenStorageDir=tokenStorageDir)

    # generate a spotify authorization code with PKCE access token.
    spotify.SetAuthTokenAuthorizationCodePKCE(
        SPOTIFY_DESKTOP_APP_CLIENT_ID, 
        SPOTIFY_SCOPES, 
        tokenProfileId=tokenProfileId, 
        redirectUriHost=redirectUriHost, 
        redirectUriPort=redirectUriPort, 
        redirectUriPath=redirectUriPath, 
        forceAuthorize=forceAuthorize)

    # if auth request failed then raise an exception.
    if not spotify._AuthClient.IsAuthorized:
        raise Exception('Spotify Desktop Application access token could not be authorized!')

    print('-------------------------------------------------------------------------------\n')
    print('** Spotify Desktop Application access token is authorized!')
    print('')
    print('If a browser window did appear, and you successfully entered your credentials')
    print('and authorized the requested access, then the access token was refreshed and')
    print('the Token Cache file was updated.')
    print('')
    print('If a browser window did NOT appear, then it denotes an existing authorization')
    print('access token was refreshed and the Token Cache file was updated.')

    print('')
    print('Process completed')
    print('Press ENTER to exit ...')
    choice = input("> ")

except Exception as ex:

    print("** Exception: %s" % str(ex))