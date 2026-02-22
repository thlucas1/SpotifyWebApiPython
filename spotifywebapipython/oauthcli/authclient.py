# external package imports.
import base64
import contextlib
import hashlib
import json
import logging
import os.path
import platformdirs
import secrets
import socket
import threading
import webbrowser

from oauthlib.oauth2 import InvalidClientError, InvalidGrantError, Client, WebApplicationClient, TokenExpiredError, AccessDeniedError
from requests_oauthlib import OAuth2Session
from typing import Optional, Union, Callable, Iterable
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler, make_server as WSGIMakeServer
from wsgiref.util import request_uri as WSGIRequestUri

# get smartinspect logger reference; create a new session for this module name.
from smartinspectpython.siauto import SIAuto, SILevel, SISession, SIMethodParmListContext, SIColors
import logging
_logsi:SISession = SIAuto.Si.GetSession(__name__)
if (_logsi == None):
    _logsi = SIAuto.Si.AddSession(__name__, True)
_logsi.SystemLogger = logging.getLogger(__name__)


class AuthClient:
    """
    OAuth2 Authorization client class.
    """

    _DEFAULT_AUTH_CODE_MESSAGE = "Enter the authorization code: "
    """
    Enter the authorization code: 
    """

    _DEFAULT_AUTH_PROMPT_MESSAGE = "Please visit this URL to authorize this application: {url}"
    """
    Please visit this URL to authorize this application: {url}
    """

    _DEFAULT_WEB_SUCCESS_MESSAGE = "The authentication flow has completed; you may close this window (or tab)." #</br>Auth Token:</br>%s"
    """
    The authentication flow has completed; you may close this window (or tab).
    """

    def __init__(self,
                 authorizationType:str,
                 authorizationUrl:str=None,
                 tokenUrl:str=None,
                 scope:str = None,
                 clientId:str=None,
                 clientSecret:str=None,
                 oauth2Client:Client=None,
                 oauth2Session:OAuth2Session=None,
                 tokenProviderId:str=None,
                 tokenProfileId:str=None,
                 tokenStorageDir:str=None,
                 tokenStorageFile:str=None,
                 tokenUpdater:Callable=None,
                 ) -> None:
        """
        Initializes a new instance of the class.
        
        Args:
            authorizationType (str):
                OAuth2 authorization type title (e.g. "Client Credentials", etc).
            authorizationUrl (str):
                URL used to authorize the requested access.  
            tokenUrl (str):
                URL used to request an access token.  
            scope (str | list[str]):
                A space-delimited list of scopes you wish to request access to.  
                If no scopes are specified, authorization will be granted only to access publicly 
                available information.
            clientId (str):
                The unique identifier of the application.
            clientSecret (str):
                The application's secret key, used to authorize your Web API or SDK calls.
            oauth2Client (Client):
                OAuth2 Client instance to use for this request.  
                If null, a new WebApplicationClient will be created with the specified clientId and scope argument values.
            oauth2Session (requests_oauthlib.oauth2_session.OAuth2Session):
                A `OAuth2Session` instance to use for this request.  
                If null, a new 'requests_oauthlib.oauth2_session.OAuth2Session' will be created with the specified 
                clientId and scope argument values.
            tokenProviderId (str):
                Provider identifier used when storing the token to disk.
                A null value will default to `Shared`.  
                Default: `Shared`
            tokenProfileId (str):
                Profile identifier used when storing the token to disk.  
                A null value will default to `Shared`.  
                Default: `Shared`
            tokenStorageDir (str):
                The directory path that will contain the Token Cache file.  
                A null value will default to the platform specific storage location:  
                Example for Windows OS = `C:\\ProgramData\\SpotifyWebApiPython`
            tokenStorageFile (str):
                The filename and extension of the Token Cache file.  
                Default is `tokens.json`.
            tokenUpdater (Callable):
                A method to call when a token needs to be refreshed by an external provider.  
                The defined method is called with no parameters, and should return a token dictionary.  
                Default is null.  
        """
        # if scope is a list then convert it to space-delimited string.
        if isinstance(scope, list):
            scope = ' '.join(scope)

        # verify token storage directory exists.
        if tokenStorageDir is None:
            tokenStorageDir = platformdirs.site_config_dir('SpotifyWebApiPython', ensure_exists=True, appauthor=False)
        os.makedirs(tokenStorageDir, exist_ok=True)  # succeeds even if directory exists.

        # verify token storage filename was specified.
        if tokenStorageFile is None:
            tokenStorageFile = 'tokens.json'

        # if token providerId not set, then default to shared.
        if tokenProviderId is None:
            tokenProviderId = 'Shared'

        # if token profileId not set, then default to shared.
        if tokenProfileId is None:
            tokenProfileId = 'Shared'

        # initialize storage.
        self._AuthorizationType:str = authorizationType
        self._AuthorizationUrl:str = authorizationUrl
        self._ClientId:str = clientId
        self._ClientSecret:str = clientSecret
        self._CodeVerifier:str = None
        self._DefaultLocalHost:str = 'localhost'
        self._Session:OAuth2Session = oauth2Session
        self._TokenProviderId:str = tokenProviderId
        self._TokenStorageDir:str = tokenStorageDir
        self._TokenStorageFile:str = tokenStorageFile
        self._TokenStoragePath:str = os.path.join(tokenStorageDir, tokenStorageFile)
        self._TokenUpdater:Callable = tokenUpdater
        self._TokenUpdater_Lock = threading.Lock()   # non re-entrant lock to sync access to token updates.
        self._TokenUrl:str = tokenUrl
        self._TokenProfileId:str = tokenProfileId
        
        # create OAuth2 Session instance if necessary.
        if self._Session is None:
            
            if oauth2Client is None:
                oauth2Client = WebApplicationClient(client_id=clientId)
            
            # create the OAuth2 session with the specified clientId and scope.
            # note that this will not load the 'token' property!
            self._Session:OAuth2Session = OAuth2Session(clientId, scope=scope, client=oauth2Client)
            
        # load the token from storage, if session does not currently have a token assigned.
        token:dict = self._Session.token
        if self._Session.token is None or len(self._Session.token) == 0:
            token:dict = self._LoadToken()
        
        # was a token loaded?
        if token is not None:
            
            # check for scope change between the existing token and the newly requested session.
            _logsi.LogVerbose('Verifying OAuth2 authorization access scope has not changed')
            hasScopeChanged:bool = self.HasScopeChanged(token, scope)
            if hasScopeChanged == True:
                # if scope change detected, then destroy the token as we need to force an auth refresh.
                _logsi.LogWarning('OAuth2 authorization access scope has changed; token will be destroyed', colorValue=SIColors.Gold)
                self._SaveToken(None)
            else:
                # set session token reference to the loaded token.
                self._Session.token = token


    @property
    def AuthorizationType(self) -> str:
        """
        OAuth2 authorization type title (e.g. "Client Credentials", etc).
        """
        return self._AuthorizationType


    @property
    def AuthorizationUrl(self) -> str:
        """
        Url used to request user authorization permission for an authorization token.
        """
        return self._AuthorizationUrl


    @property
    def ClientId(self) -> str:
        """
        The unique identifier of the application.
        """
        return self._ClientId


    @property
    def CodeVerifier(self) -> str:
        """
        The code verifier string used as part of the token request authorization process.
        
        According to the PKCE standard, a code verifier is a high-entropy cryptographic 
        random string with a length between 43 and 128 characters (the longer the better). 
        It can contain letters, digits, underscores, periods, hyphens, or tildes.
        """
        return self._CodeVerifier


    @property
    def IsAuthorized(self) -> bool:
        """
        Indicates whether this session has an OAuth token 'access_token' value or not. 
        
        If True, you can reasonably expect OAuth-protected requests to the resource to succeed.  
        
        If False, you need the user to go through the OAuth authentication dance before 
        OAuth-protected requests to the resource will succeed.
        """
        # mimic behavior of self._Session.authorized, in case we are using a Home Assistant OAuth2Session
        # instance, which does not have an 'authorized' method.
        result:bool = False
        if self._Session is None:
            return result
        if self._Session.token is None:
            return result
        if self._Session.token.get('access_token') is None:
            return result
        return True


    @property
    def Session(self) -> OAuth2Session:
        """
        OAuth 2 extension to the `requests.Session` class.

        Supports any grant type adhering to :class:`oauthlib.oauth2.Client` spec
        including the four core OAuth 2 grants.

        Can be used to create authorization urls, fetch tokens and access protected
        resources using the `requests.Session` class interface you are used to.
        """
        return self._Session


    @property
    def TokenProfileId(self) -> str:
        """
        Profile identifier used when loading / storing the token from / to disk.
        """
        return self._TokenProfileId

    @TokenProfileId.setter
    def TokenProfileId(self, value:str):
        """ 
        Sets the TokenProfileId property value.
        """
        if (value is None):
            self._TokenProfileId = value
        elif (isinstance(value,str)):
            if value.strip() == '':
                self._TokenProfileId = None
            else:
                self._TokenProfileId = value


    @property
    def TokenUrl(self) -> str:
        """
        Url used to request or renew an authorization token.
        """
        return self._TokenUrl


    def Logout(self):
        """
        Removes a stored token, but does not clear the current session.
        
        Warning: a request with the current session can refresh and save
        the token, making this call ineffective.
        """
        _logsi.LogVerbose('OAuth2 logout called; token will be destroyed', colorValue=SIColors.Gold)
        self._SaveToken(None)


    def process_url(self, api:str) -> str:
        return api


    def request(self, method:str, api:str, **kwargs) -> object:
        return self._Session.request(method, self.process_url(api), **kwargs)


    def get(self, api:str, **kwargs):
        return self._Session.get(self.process_url(api), **kwargs)


    def post(self, api:str, **kwargs):
        return self._Session.post(self.process_url(api), **kwargs)


    def put(self, api:str, **kwargs):
        return self._Session.put(self.process_url(api), **kwargs)


    def patch(self, api:str, **kwargs):
        return self._Session.patch(self.process_url(api), **kwargs)


    def delete(self, api:str, **kwargs):
        return self._Session.delete(self.process_url(api), **kwargs)


    def head(self, api:str, **kwargs):
        return self._Session.head(self.process_url(api), **kwargs)


    def options(self, api:str, **kwargs):
        return self._Session.options(self.process_url(api), **kwargs)


    def _CheckAuthorization(self, force:bool, token_test:Optional[Callable]=None) -> bool:
        """
        Checks if the access token is authorized or not.
        
        Args:
            force (bool):
                True to force the access token to be refreshed regardless of 
                authorized status.
            tokenTest (Callable):
                Function that receives this object for a param, makes a call, and 
                returns the response.  
                Default is null.
                
        Returns:
            True if the access token is authorized; otherwise, False if it is not
            authorized or the force argument is true.
        """
        # force the user to authorize the application access if we do not have an authorized 
        # access token, if the scope has changed, or if the caller requested us to (by force).
        if (not self.IsAuthorized) or (force == True):
            return False
        
        result:bool = True
        if token_test is not None:
            try:
                resp = token_test(self)
                if resp.status_code % 100 == 4:
                    result = False
            except:  # noqa: E722
                result = False
                
        return result


    def _FindOpenPortOnLocalhost(self, portRange:list[int]):
        """
        Find a port to open for the redirect web server.
        
        Args:
            portRange (list[int]):
                A list that contains a starting port number (index 0) and the ending
                port number (index 1) to check.  
                Default port range is 8080 - 8180.
                
        If portRange argument is null, then the default range will be used.
        If only one port number is passed, then only that port will be checked.
        """
        _logsi.LogVerbose('Finding an available local port for the temporary server; port range to check: "%s"' % (str(portRange)))
        
        # default starting and ending ports.
        portStart:int = 8080
        portStop = portStart + 100
        localhostIp:str = '127.0.0.1'

        # validations.
        if portRange is None:
            pass
        elif len(portRange) == 1:
            portStart = int(portRange[0])
            portStop = portStart
        elif len(portRange) == 2:
            portStart = int(portRange[0])
            portStop = int(portRange[1])
            
        # find an available port within the specified range of ports.
        for port in range(portStart, portStop):
            
            with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                try:
                    sock.bind((localhostIp, port))
                    sock.listen(1)
                except socket.error:
                    is_open = False
                else:
                    is_open = True
                
            # if port is open for listening, then use it.
            if is_open:
                return port
            
        # if we could not find a port, then it's a problem!
        raise ConnectionError('Could not find an open port on localhost address "%s", in the range of "%s" to "%s"' % (localhostIp, portStart, portStop))
        

    @staticmethod
    def HasTokenForKey(
        clientId:str=None,
        tokenProviderId:str=None,
        tokenProfileId:str=None,
        tokenStorageDir:str=None,
        tokenStorageFile:str=None,
        ) -> bool:
        """
        Checks if a token exists in the token storage file for the ProviderId / ClientId key.
        
        Args:
            clientId (str):
                The unique identifier of the application.
            tokenProviderId (str):
                Provider identifier used when storing the token to disk.
            tokenProfileId (str):
                Profile identifier used when storing the token to disk.  
            tokenStorageDir (str):
                The directory path that will contain the `tokens.json` file.  
                A null value will default to the platform specific storage location:  
                Example for Windows OS = `C:\\ProgramData\\SpotifyWebApiPython`
            tokenStorageFile (str):
                The filename and extension of the Token Cache file.  
                Default is `tokens.json`.
        
        Returns:
            True if the token was found in the token storage file for the
            specified ProviderId and ClientId key; otherwise, null.
        """
        apiMethodName:str = 'HasTokenForKey'
        apiMethodParms:SIMethodParmListContext = None
        
        try:

            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            _logsi.LogMethodParmList(SILevel.Verbose, "Checking if token exists in token storage file", apiMethodParms)
            
            # verify token storage directory exists.
            if tokenStorageDir is None:
                tokenStorageDir = platformdirs.site_config_dir('SpotifyWebApiPython', ensure_exists=True, appauthor=False)

            # verify token storage filename was specified.
            if tokenStorageFile is None:
                tokenStorageFile = 'tokens.json'

            # if token clientId not set, then default to shared.
            if clientId is None:
                clientId = 'Shared'

            # if token providerId not set, then default to shared.
            if tokenProviderId is None:
                tokenProviderId = 'Shared'

            # if token profileId not set, then default to shared.
            if tokenProfileId is None:
                tokenProfileId = 'Shared'

            # formulate token storage path.
            tokenStoragePath:str = os.path.join(tokenStorageDir, tokenStorageFile)
            
            # formulate token storage key.
            tokenKey:str = f'{tokenProviderId}/{clientId}/{tokenProfileId}'
            _logsi.LogVerbose('Token storage key: "%s"' % (tokenKey))           
            _logsi.LogVerbose('Token storage file path: "%s"' % (tokenStoragePath))
            
            # does the token storage file exist?
            if os.path.exists(tokenStoragePath):

                # open the token storage file, and load it's contents.
                _logsi.LogVerbose('Opening token storage file')
                with open(tokenStoragePath, 'r') as f:
                    
                    tokens = json.load(f)

                    # return if token key exists or not.
                    if tokenKey in tokens:
                        _logsi.LogDictionary(SILevel.Verbose, 'Token was found in token storage file for key: "%s"' % (tokenKey), tokens[tokenKey], prettyPrint=True)
                        return True
        
            # indicate token was not found.
            _logsi.LogVerbose('Token was not found in token storage file for key: "%s"' % (tokenKey))           
            return False
        
        except Exception as ex:
            
            # trace.
            _logsi.LogException('Could not verify OAuth2 Token from token storage file: "%s"' % (tokenStoragePath), ex)
            raise

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def _LoadToken(self) -> dict:
        """
        Loads a token from the token storage file for the ProviderId / ClientId key.
        
        Returns:
            A token dictionary, if one was found in the token storage file for the
            specified ProviderId and ClientId key; otherwise, null.
        """
        apiMethodName:str = '_LoadToken'
        apiMethodParms:SIMethodParmListContext = None
        
        try:

            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            _logsi.LogMethodParmList(SILevel.Verbose, "Loading Token from token storage", apiMethodParms)
                
            # if we don't have a clientId then don't bother.
            if not self._Session.client_id:
                _logsi.LogVerbose('Client ID is not set - nothing to do')
                return
        
            # formulate token storage key.
            tokenKey:str = f'{self._TokenProviderId}/{self._Session.client_id}/{self._TokenProfileId}'
            _logsi.LogVerbose('Token storage key: "%s"' % (tokenKey))           
            _logsi.LogVerbose('Token storage file path: "%s"' % (self._TokenStoragePath))
            
            # does the token storage file exist?
            if os.path.exists(self._TokenStoragePath):

                # open the token storage file, and load it's contents.
                _logsi.LogVerbose('Opening token storage file')
                with open(self._TokenStoragePath, 'r') as f:
                    
                    tokens = json.load(f)

                    # if token key exists then load the token.
                    if tokenKey in tokens:
                        _logsi.LogDictionary(SILevel.Verbose, 'Token was loaded from token storage file for key: "%s"' % (tokenKey), tokens[tokenKey], prettyPrint=True)
                        return tokens[tokenKey]
                    else:
                        _logsi.LogVerbose('Token was not found in token storage file for key: "%s"' % (tokenKey))           
                        
        except Exception as ex:
            
            # trace.
            _logsi.LogException('Could not load OAuth2 Token from token storage file: "%s"' % (self._TokenStoragePath), ex)
            raise

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def SaveToken(self, token:dict=None) -> None:
        """
        Saves a token to the token storage file (e.g. disk) for the ProviderId / ClientId key.
        
        Args:
            token (dict):
                The token dictionary object to save.  
                Specify null to remove the token for the specified ProviderId / ClientId.
                
        Raises:
            IOError:
                If an error occurs saving the tokens file.
        """
        # invoke internal method for backward compatibility.
        self._SaveToken(token)


    def _SaveToken(self, token:dict=None) -> None:
        """
        Saves a token to the token storage file (e.g. disk) for the ProviderId / ClientId key.
        
        Args:
            token (dict):
                The token dictionary object to save.  
                Specify null to remove the token for the specified ProviderId / ClientId.
                
        Raises:
            IOError:
                If an error occurs saving the tokens file.
        """
        apiMethodName:str = '_SaveToken'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("token", token)
            _logsi.LogMethodParmList(SILevel.Verbose, "Saving token to token storage", apiMethodParms)
            _logsi.LogDictionary(SILevel.Verbose, "Token to save (pretty print)", token, prettyPrint=True)
                
            # formulate token storage key.
            tokenKey:str = f'{self._TokenProviderId}/{self._Session.client_id}/{self._TokenProfileId}'
            _logsi.LogVerbose('Token storage key: "%s"' % (tokenKey))
            _logsi.LogVerbose('Token storage file path: "%s"' % (self._TokenStoragePath))
            
            tokens:dict = {}
        
            # does the token storage file exist?
            if os.path.exists(self._TokenStoragePath):
                
                # open the token storage file, and load it's contents.
                _logsi.LogVerbose('Loading token storage file contents')
                with open(self._TokenStoragePath, 'r') as f:
                    tokens = json.load(f)
                    
            if token is None:
                
                # if token not specified, then remove the existing token for the providerId / clientId.
                _logsi.LogVerbose('Removing token from token storage file')
                if tokenKey in tokens:
                    del tokens[tokenKey]
                    
            else:
                
                # store the token for the providerId / clientId.
                _logsi.LogVerbose('Storing token in token storage file')
                tokens[tokenKey] = token

            # save the token storage file changes.
            _logsi.LogVerbose('Saving token storage file updates')
            with open(self._TokenStoragePath, 'w') as f:
                json.dump(tokens, f, indent=4, sort_keys=True)
                
        except Exception as ex:
            
            # trace.
            _logsi.LogException('Could not store Token in the token storage file', ex)
            raise

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def authorization_url(self, **kwargs):
        """
        Constructs the authorization url, complete with all querystring parameters.
        
        Args:
            **kwargs
                Keyword arguments for the authorization type.
        
        Returns:
            The authorization url querystring and a generated state value.
        """
        _logsi.LogVerbose('Creating OAuth2 authorization url')

        # according to the PKCE standard, a code verifier is a high-entropy cryptographic 
        # random string with a length between 43 and 128 characters (the longer the better). 
        # it can contain letters, digits, underscores, periods, hyphens, or tildes.
        codeVerifierLength:int = 128
        codeVerifier:str = secrets.token_urlsafe(codeVerifierLength)[0:codeVerifierLength]
        _logsi.LogText(SILevel.Verbose, 'OAuth2 code verifier (urlsafe, %d bytes): %s' % (codeVerifierLength, codeVerifier), codeVerifier)
        self._CodeVerifier = codeVerifier

        # once the code verifier has been generated, we must transform (hash) it using the SHA256 algorithm. 
        codeHash = hashlib.sha256(codeVerifier.encode('utf-8'))
        _logsi.LogText(SILevel.Verbose, 'OAuth2 code verifier SHA256 hashed bytes: %s' % (codeHash.hexdigest()), codeHash.hexdigest())
        
        # we will then convert the hash value to a base64 encoded string.
        # this is the value that will be sent within the user authorization request.
        codeChallengeBytes = base64.urlsafe_b64encode(codeHash.digest())
        codeChallenge = codeChallengeBytes.decode('utf-8').rstrip('=')  # drop '=' padding characters
        _logsi.LogText(SILevel.Verbose, 'OAuth2 code challenge url-safe BASE64 encoded string: %s' % (codeChallenge), codeChallenge)
        kwargs.setdefault("code_challenge_method", "S256")
        kwargs.setdefault("code_challenge", codeChallenge)

        # state is an opaque value that is used to prevent cross-site request forgery.
        stateLength:int = 16
        state:str = secrets.token_urlsafe(stateLength)[0:stateLength]
        _logsi.LogText(SILevel.Verbose, 'OAuth2 state value (urlsafe, %d bytes): %s' % (stateLength, state), state)

        # create the authorization URL.  
        url, state = self._Session.authorization_url(self._AuthorizationUrl, state, **kwargs)
        
        # trace.
        _logsi.LogText(SILevel.Verbose, 'OAuth2 authorization url: "%s"' % (url), url)
        return url, state


    def FetchToken(self, **kwargs) -> dict:
        """
        Fetch an access token from the token endpoint.
        
        Args:
            **kwargs:
                Additional keyword arguments to add to the 
                
        Returns:
            A token dictionary.
        """
        apiMethodName:str = 'FetchToken'
        apiMethodParms:SIMethodParmListContext = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("self._TokenUrl", self._TokenUrl)
            apiMethodParms.AppendKeyValue("self._ClientId", self._ClientId)
            apiMethodParms.AppendKeyValue("self._ClientSecret", self._ClientSecret)
            apiMethodParms.AppendKeyValue("self._CodeVerifier", self._CodeVerifier)
            apiMethodParms.AppendKeyValue("**kwargs", kwargs)
            _logsi.LogMethodParmList(SILevel.Verbose, 'Fetching access token for authorization type "%s"' % self._AuthorizationType, apiMethodParms)
                
            # if client secret specified then include it.
            includeClientId:bool = False
            if self._ClientId is not None:
                includeClientId = True

            # if code verifier specified then include it so that the code challenge is verified.
            if self._CodeVerifier is not None:
                kwargs.setdefault("code_verifier", self._CodeVerifier)
           
            # fetch the authorization token.
            # this will also automatically set the 'self._Session.token' instance.
            token = self._Session.fetch_token(self._TokenUrl, 
                                              include_client_id=includeClientId, 
                                              client_secret=self._ClientSecret, 
                                              **kwargs)
        
            # trace.
            _logsi.LogDictionary(SILevel.Verbose, 'Access token was successfully fetched', token, prettyPrint=True)

            # save the new token to disk.
            self._SaveToken(token)

            # return new token to the caller.
            return token
        
        except AccessDeniedError as ex:

            _logsi.LogException('AccessDenied Error: normally, this indicates the user cancelled the login request', ex)
            raise
        
        except Exception as ex:
            
            # trace.
            _logsi.LogException('Could not fetch Token', ex)
            raise

        finally:
        
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def HasScopeChanged(self, token:dict, scope:str=None) -> bool:
        """
        Indicates whether the scope has changed between this session and the authorization
        access token scope values.
        
        Args:
            token (dict):
                The authorization access token dictionary to check the scope of.
            scope (str | list[str]):
                A space-delimited list of scope identifiers you wish to request access to.  
        
        If True, you need the user to go through the OAuth authentication dance before 
        OAuth-protected requests to the resource will succeed.
        
        If False, then you can reasonably expect OAuth-protected requests to the resource to succeed.  
        """
        # if token not set then don't bother - indicate scope has changed.
        if token is None:
            return True
        
        arrScopeSession:list[str] = []
        arrScopeToken:list[str] = []

        # get scope values for session and token.
        # we will convert them to array and sort them before comparing for differences.
        if scope is not None:
            arrScopeSession = scope
            if isinstance(arrScopeSession, str):
                arrScopeSession = arrScopeSession.split(' ')
            arrScopeSession.sort()

        if token is not None and isinstance(token, dict):
            arrScopeToken = token.get('scope', None) or []
            if isinstance(arrScopeToken, str):
                arrScopeToken = arrScopeSession.split(' ')
            arrScopeToken.sort()
            
        # get string values for both scope's for comparison.
        strScopeToken = ' '.join(arrScopeToken)
        strScopeSession = ' '.join(arrScopeSession)
        
        # does the token scope match the requested session scope?
        if strScopeToken != strScopeSession:
            
            _logsi.LogWarning('Token scope change detected, forcing authorization access; Token scope="%s", Session scope="%s"' % (strScopeToken, strScopeSession))
            return True
        
        # indicate scope has not changed.
        return False


    def AuthorizeWithConsole(
        self,
        authorization_prompt_message=_DEFAULT_AUTH_PROMPT_MESSAGE,
        open_browser=True,
        code_message=_DEFAULT_AUTH_CODE_MESSAGE,
        token_audience=None,
        force: bool = False,
        token_test: Optional[Callable] = None,
        **kwargs
    ):
        """
        Executes the authorization flow without starting a web server.
        
        Note that you must have 'urn:ietf:wg:oauth:2.0:oob' as a redirect URI value 
        in the provider app settings for this to work.
        
        Args:
            authorization_prompt_message (str | None):  
                The message to display that will inform the user to navigate to the 
                authorization URL. If null, then no message is displayed.
            open_browser (bool):  
                True to open the authorization URL in the user's browser; otherwise, False
                to not open a browser.
            code_message (str):  
                The message to display in the console prompting the user to enter the authorization code.
            token_audience (str):  
                Passed along with the request for an access token.  
                It determines the endpoints with which the token can be used.  
                Default is null.
            force (bool):  
                True to authorize, even if we already have a token;  otherwise, False
                to only authorize if the token is not authorized, has expired, or the
                scope has changed.
            token_test (Callable):  
                Function that receives this object for a param, makes a call, and returns 
                the response.
            kwargs: 
                Additional keyword arguments passed through to `authorization_url`.

        Returns:
            The OAuth 2.0 credentials for the user.
        """
        apiMethodName:str = 'AuthorizeWithServer'
        apiMethodParms:SIMethodParmListContext = None

        wsgiServer:WSGIServer = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("authorization_prompt_message", authorization_prompt_message)
            apiMethodParms.AppendKeyValue("open_browser", open_browser)
            apiMethodParms.AppendKeyValue("code_message", code_message)
            apiMethodParms.AppendKeyValue("token_audience", token_audience)
            apiMethodParms.AppendKeyValue("force", force)
            apiMethodParms.AppendKeyValue("token_test", token_test)
            apiMethodParms.AppendKeyValue("**kwargs", kwargs)
            _logsi.LogMethodParmList(SILevel.Verbose, 'Executing authorization flow using local console for authorization type "%s"' % self._AuthorizationType, apiMethodParms)
                       
            # is the access token authorized?  if so, then we are done.
            if self._CheckAuthorization(force, token_test):
                _logsi.LogVerbose('Token is authorized; nothing else to do')
                return self

            self._Session.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
            auth_url, _ = self.authorization_url(**kwargs)

            if open_browser:
                _logsi.LogVerbose('Opening a browser window (or tab) to the authorization request url')
                webbrowser.open(auth_url, new=2, autoraise=True)

            if authorization_prompt_message:
                message:str = authorization_prompt_message.format(url=auth_url)
                _logsi.LogWarning(message, logToSystemLogger=True)

            # prompt the user (in the console) to enter the authorization code response.
            _logsi.LogVerbose('Waiting for a console response from the user for the authorization request response code')
            while True:
                auth_code = input(code_message).strip()
                if auth_code:
                    break

            # fetch the newly issued authorization token.
            self.FetchToken(code=auth_code, audience=token_audience)
        
            # return to caller.
            return self

        except Exception as ex:
            
            # trace.
            _logsi.LogException('Authorize with console exception', ex)
            raise

        finally:
            
            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def AuthorizeWithServer(
        self,
        host: Optional[str] = None,
        bind_addr: Optional[int] = None,
        port: Union[int, list[int]] = 8080,
        authorization_prompt_message: Optional[str] = _DEFAULT_AUTH_PROMPT_MESSAGE,
        success_message: str = _DEFAULT_WEB_SUCCESS_MESSAGE,
        open_browser: bool = True,
        redirect_uri_path: str = '/',
        timeout_seconds: Optional[int] = 120,
        token_audience: Optional[str] = None,
        force: bool = False,
        token_test: Optional[Callable] = None,
        **kwargs
    ):
        """
        Executes the authorization flow by starting a temporary local web server
        to listen for the authorization response.
        
        Note that you must have 'http://localhost:8080/' as a redirect URI value 
        in the provider app settings for this to work.
        
        The server strategy instructs the user to open the authorization URL in
        their browser and will attempt to automatically open the URL for them.
        It will start a local web server to listen for the authorization
        response. Once authorization is complete the authorization server will
        redirect the user's browser to the local web server. The web server
        will get the authorization code from the response and shutdown. The
        code is then exchanged for a token.

        Args:
            host (str):  
                The hostname for the local redirect server. This will be served 
                over http, not https.
            bind_addr (str):  
                Optionally provide an ip address for the redirect server to listen 
                on when it is not the same as host (e.g. in a container).  
                Default value is None, which means that the redirect server will listen
                on the ip address specified in the host parameter.
            port (int / list[int]):  
                The port for the local redirect server.  
                If a list, it would find the first open port in the range.
            authorization_prompt_message (str | None):  
                The message to display that will inform the user to navigate to the 
                authorization URL. If null, then no message is displayed.
            success_message (str):  
                The message to display in the web browser that the authorization flow 
                is complete.
            open_browser (bool):  
                True to open the authorization URL in the user's browser; otherwise, False
                to not open a browser.
            redirect_uri_path (str):  
                Path value to add when constructing the redirect_uri; otherwise,
                None to not add a path value.  
                Default value is '/'.
            timeout_seconds (int):  
                If set, an error will be raised after the timeout value if the user did not
                respond to the authorization request.  The value is in seconds.  
                When set to None there is no timeout.  
                Default value is 120 (2 minutes).
            token_audience (str):  
                Passed along with the request for an access token.  
                It determines the endpoints with which the token can be used.  
                Default is null.
            force (bool):  
                True to authorize, even if we already have a token;  otherwise, False
                to only authorize if the token is not authorized, has expired, or the
                scope has changed.
            token_test (Callable):  
                Function that receives this object for a param, makes a call, and returns 
                the response.
            kwargs: 
                Additional keyword arguments passed through to `authorization_url`.

        Returns:
            The OAuth 2.0 credentials for the user.
        """
        apiMethodName:str = 'AuthorizeWithServer'
        apiMethodParms:SIMethodParmListContext = None

        wsgiServer:WSGIServer = None
        
        try:
            
            # trace.
            apiMethodParms = _logsi.EnterMethodParmList(SILevel.Debug, apiMethodName)
            apiMethodParms.AppendKeyValue("host", host)
            apiMethodParms.AppendKeyValue("bind_addr", bind_addr)
            apiMethodParms.AppendKeyValue("port", port)
            apiMethodParms.AppendKeyValue("authorization_prompt_message", authorization_prompt_message)
            apiMethodParms.AppendKeyValue("success_message", success_message)
            apiMethodParms.AppendKeyValue("open_browser", open_browser)
            apiMethodParms.AppendKeyValue("redirect_uri_path", redirect_uri_path)
            apiMethodParms.AppendKeyValue("timeout_seconds", timeout_seconds)
            apiMethodParms.AppendKeyValue("token_audience", token_audience)
            apiMethodParms.AppendKeyValue("force", force)
            apiMethodParms.AppendKeyValue("token_test", token_test)
            apiMethodParms.AppendKeyValue("**kwargs", kwargs)
            _logsi.LogMethodParmList(SILevel.Verbose, 'Executing authorization flow using local web server for authorization type "%s"' % self._AuthorizationType, apiMethodParms)
                
            # is the access token authorized?  if so, then we are done.
            if self._CheckAuthorization(force, token_test):
                _logsi.LogVerbose('Token is authorized; nothing else to do')
                return self

            # if a port range was passed, then find an available port in that range.
            if isinstance(port, list):
                port = self._FindOpenPortOnLocalhost(port)

            # default the local redirect server host if one was not specified.
            if not host:
                host = self._DefaultLocalHost

            # initialize and create a local Web Server Gateway Interface (WSGI) server.
            _logsi.LogVerbose('Creating temporary WSGI local web server to handle the OAuth2 authorization request response')
            wsgiApp:_WSGIAppRedirectHandler = _WSGIAppRedirectHandler(success_message)
            WSGIServer.allow_reuse_address = False  # Fail fast if the address is occupied
            wsgiServer:WSGIServer = WSGIMakeServer(bind_addr or host, 
                                                   port, 
                                                   wsgiApp, 
                                                   handler_class=_WSGIRequestHandler
                                                   )
        
            # construct the redirect uri, which is where the user is redirected after 
            # authentication success or failure.
            redirectUri:str = 'http://{}:{}'.format(host, wsgiServer.server_port)
            if redirect_uri_path is not None:
                redirectUri = redirectUri + redirect_uri_path
            self._Session.redirect_uri = redirectUri
        
            # construct the authorization url and state values.
            auth_url, _ = self.authorization_url(**kwargs)

            # open a new tab page using the local default browser.
            if open_browser:
                _logsi.LogVerbose('Opening a browser window (or tab) to the authorization request url')
                webbrowser.open(auth_url, new=2, autoraise=True)

            if authorization_prompt_message:
                message:str = authorization_prompt_message.format(url=auth_url)
                _logsi.LogWarning(message, logToSystemLogger=True)

            # set the timeout value, and handle the user authorization request response.
            # the 'handle_request' call will block until a response is received, or a timeout occurs.
            _logsi.LogVerbose('WSGI server will now wait for a response from the user for the authorization request url (timeout=%s seconds)' % timeout_seconds)
            wsgiServer.timeout = timeout_seconds
            wsgiServer.handle_request()

            # get the user authorization request response value.
            authResponse:str = wsgiApp.LastRequestUri
            if authResponse is None:
                raise AccessDeniedError('An authorization response was not returned, which usually indicates the server timed out waiting for a response from the user to authorize the request')

            # force https in case it needs it, as OAuth 2.0 can only occur over https.
            authResponse = authResponse.replace("http", "https")
            _logsi.LogText(SILevel.Verbose, 'WSGI server intercepted the user authorization response: "%s"' % (authResponse), authResponse)

            # fetch the newly issued authorization token.
            self.FetchToken(authorization_response=authResponse, 
                            audience=token_audience,
                            **kwargs
                           )

            # return to caller.
            return self

        except Exception as ex:
            
            # trace.
            _logsi.LogException('Authorize with server exception', ex)
            raise

        finally:
            
            # ensure wsgi server is shutdown.
            if wsgiServer is not None:
                _logsi.LogVerbose('WSGI server is shutting down and freeing resources.')
                wsgiServer.server_close()
                wsgiServer = None

            # trace.
            _logsi.LeaveMethod(SILevel.Debug, apiMethodName)


    def RefreshToken(self, **kwargs) -> dict:
        """ 
        Refreshes the current session token.
       
        If a TokenUpdater callable was specified, then the token is refreshed externally by the 
        callable function.
        
        Otherwise, the session `refresh_token` method is invoked using the refresh token value.
        
        Args:
            **kwargs: 
                Additional keyword arguments to include in the token request.
                
        Returns:
            A token dictionary.
        """
        token:dict = None
        
        try:

            # trace.
            _logsi.LogVerbose("Refreshing OAuth2 authorization token for the \"%s\" authorization type" % self._AuthorizationType, colorValue=SIColors.Gold)
            
            # was a token updater supplied?
            if self._TokenUpdater is not None:
                    
                # log trace message if we are waiting on another token update to complete!
                _logsi.LogVerbose("Preparing to set the lock for external token refresh", colorValue=SIColors.Gold)
                if self._TokenUpdater_Lock.locked():
                    _logsi.LogVerbose("Waiting on a previous external token refresh to complete", colorValue=SIColors.Red)

                # only allow one thread to update authorization token at a time.
                with self._TokenUpdater_Lock:

                    _logsi.LogVerbose('Calling External Token Updater to refresh the token', colorValue=SIColors.Gold)
                    token = self._TokenUpdater()

                    _logsi.LogDictionary(SILevel.Verbose, 'External Token Updater has refreshed the token', token, colorValue=SIColors.Gold)
                
                    # if nothing returned then it's an error.
                    if token is None:
                        raise TokenExpiredError('External Token Updater did not return a token.')
                    
            else:
            
                # get refresh token from session token.
                refreshToken:str = None
                if self._Session is not None and self._Session.token is not None:
                    _logsi.LogDictionary(SILevel.Verbose, 'OAuth2 Session token', self._Session.token)
                    refreshToken = self._Session.token.get('refresh_token')

                # if refresh token is not present, then it's an error.
                if refreshToken is None:
                    raise TokenExpiredError('Token cannot be refreshed as there is no "refresh_token" key in the session token.')
            
                # add the clientId if the session has been established.
                if self._Session.client_id is not None:
                    kwargs.setdefault("client_id", self._Session.client_id)

                _logsi.LogDictionary(SILevel.Verbose, 'Refreshing the OAuth2 session token via url "%s" - kwargs' % self._TokenUrl, kwargs)
                
                # refresh the authorization token, using it's refresh token value.
                token = self._Session.refresh_token(self._TokenUrl, refreshToken, **kwargs)

                # if nothing returned then it's an error.
                if token is None:
                    raise TokenExpiredError('OAuth Session refresh_token method returned a null token.')
            
                # store the refresh token to the token storage file.
                self._SaveToken(token)
            
            # trace.
            _logsi.LogVerbose('OAuth2 authorization token was successfully refreshed for the "%s" authorization type' % self._AuthorizationType)

            # return the refreshed authorization token to the caller.
            return token
        
        except (InvalidGrantError, InvalidClientError) as ex:

            # trace.
            _logsi.LogException('OAuth2 token refresh error (InvalidGrantError, InvalidClientError): %s' % str(ex), ex, logToSystemLogger=False)

            # if InvalidGrantError / InvalidClientError, then it denotes that it's NOT a temporary 
            # condition and that we need to completely remove the token from the token storage file 
            # since it's no longer valid.  this will force an authorization refresh next time around.
            if ex.description == 'Refresh token revoked':
                if self.AuthorizationType in ['OAuth2Token']:
                    _logsi.LogWarning('Refresh token was revoked for authorization type "%s".  Ensure that you are saving the refreshed token in the host provider session to avoid this problem; see the "tokenUpdater" argument for more details' % self.AuthorizationType)

            # if internal storage provider, then remove the token from the storage file.
            if self._TokenUpdater is None:
                _logsi.LogWarning('Refresh token error detected for internal storage provider; token will be destroyed.  Exception message: %s' % str(ex), colorValue=SIColors.Gold)
                self._SaveToken(None)
                
            # pass exception on thru.
            raise

        except Exception as ex:
            
            # trace.
            _logsi.LogException('OAuth2 token refresh error: %s' % str(ex), ex, logToSystemLogger=False)
            _logsi.LogWarning('An error occured while trying to refresh an "%s" authentication token; this might be a temporary condition, so the token will not be destroyed.  Exception was: %s' % (self.AuthorizationType, str(ex)))

            # if this is NOT an InvalidGrantError / InvalidClientError, then it denotes that it's 
            # PROBABLY a temporary condition (e.g. Spotify auth server unavailable, network issue, etc).
            # in this case, we will NOT remove the token from the token cache file as we want it to
            # try again on the next access.  
            # we will still pass the exception on thru though, as the token could not be refreshed and
            # the operation would fail anyway.

            # pass exception on thru.
            raise


class _WSGIRequestHandler(WSGIRequestHandler):
    """
    WSGI Request Handler.

    Uses a named logger instead of printing to stderr.
    """

    def log_message(self, format, *args) -> None:
        # pylint: disable=redefined-builtin
        # (format is the argument name defined in the superclass.)

        # trace.
        _logsi.LogVerbose(format, *args, logToSystemLogger=False)


class _WSGIAppRedirectHandler(object):
    """
    WSGI App that will handle the authorization redirect.

    Stores the request URI and displays the given success message.
    """

    def __init__(self, successMessage) -> None:
        """
        Args:
            successMessage (str): 
                The message to display in the web browser that the authorization flow is complete.
        """
        self._LastRequestUri:str = None
        self._SuccessMessage = successMessage


    def __call__(self, environ, start_response) -> Iterable[bytes]:
        """
        WSGI Callable.

        Args:
            environ (Mapping[str, Any]): 
                The WSGI environment.
            start_response (Callable[str, list]): 
                The WSGI start_response callable.

        Returns:
            The response body.
        """
        # respond to the authorization server with response code 200 (ok) message,
        # which indicates that we received their response.
        start_response("200 OK", [("Content-type", "text/plain; charset=utf-8")])
        
        # store the full request URI (including the query string) so that it can
        # be accessed by the caller.
        self._LastRequestUri = WSGIRequestUri(environ)
        
        # return authorization flow was completed successfully message.
        return [self._SuccessMessage.encode("utf-8")]


    @property
    def LastRequestUri(self) -> str:
        """
        The full request URI, optionally including the query string.
        """
        return self._LastRequestUri


    @property
    def SuccessMessage(self) -> str:
        """
        The message to display in the web browser that the authorization flow is complete.
        """
        return self._SuccessMessage
