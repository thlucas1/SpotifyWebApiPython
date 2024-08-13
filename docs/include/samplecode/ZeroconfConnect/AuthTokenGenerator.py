from spotifywebapipython import *
from spotifywebapipython.zeroconfapi import *
from spotifywebapipython.const import SPOTIFY_DESKTOP_APP_CLIENT_ID

try:

    # set required token scope(s).
    SPOTIFY_SCOPES:list = \
    [
        'streaming',
    ]
            
    # set token profile parameters.
    tokenStorageDir:str = './test/testdata/haconfig'
    tokenProviderId:str = 'SpotifyWebApiAuthCodePkce'
    tokenProfileId:str = 'SpotifyDesktopApp_Scopes_Streaming'
    redirectUriHost:str = '127.0.0.1'
    redirectUriPort:int = 4381
    redirectUriPath:str = '/login'
    forceAuthorize:bool = False

    print('')
    print('A link may be displayed following this message asking you to copy and')
    print('paste the link into a new browser window / tab to authorize the request.')
    print('via the Spotify Authorization web-site.  You only need to do this if a')
    print('browser window / tab did not automatically open, prompting you to authorize')
    print('the request.')
    print('')
    print('You have 2 minutes to authorize the request before a timeout is reached,')
    print('and the authorization request is cancelled.')
    print('')
    
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

    print('')
    print('** Spotify Desktop Application access token is authorized!')
    print('')
    print('If a browser window did not appear, then it denotes an existing authorization')
    print('access token was refreshed and the Token Cache file was updated.')

    # log token storage info.
    print('')
    print('A Token Cache file was saved to the following location:\n%s/tokens.json' % tokenStorageDir)
    print('')
    print('Copy the above Token Cache file to the following Home Assistant Config folder location:')
    print('-> /config/custom_components/spotifyplus/data/tokens.json')

except Exception as ex:

    print("** Exception: %s" % str(ex))
