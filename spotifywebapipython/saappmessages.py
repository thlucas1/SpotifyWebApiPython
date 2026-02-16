# external package imports.
# none

# our package imports.
from .sautils import export


@export
class SAAppMessages:
    """
    A strongly-typed resource class, for looking up localized strings, etc.
    
    Threadsafety:
        This class is fully thread-safe.
    """

    UNHANDLED_EXCEPTION:str = "SAM0001E - An unhandled exception occured while processing method \"{0}\".\n{1}"
    """
    SAM0001E - An unhandled exception occured while processing method \"{0}\".
    {1}
    """

    ARGUMENT_REQUIRED_ERROR:str = "SAM0002E - The \"%s\" method \"%s\" argument is required, and cannot be null or None."
    """
    SAM0002E - The \"%s\" method \"%s\" argument is required, and cannot be null or None.
    """

    ARGUMENT_TYPE_ERROR:str = "SAM0003E - The \"%s\" method \"%s\" argument must be of type \"%s\"; the \"%s\" type is not supported for this argument."
    """
    SAM0003E - The \"%s\" method \"%s\" argument must be of type \"%s\"; the \"%s\" type is not supported for this argument.
    """

    MSG_SPOTIFY_WEB_API_ERROR:str = "SAM1001E - Spotify Web API returned an error status while processing the \"{methodname}\" method.\nStatus: {status} - {httpreason}\nMessage: \"{message}\""
    """
    SAM1001E - Spotify Web API returned an error status while processing the \"{methodname}\" method.\nStatus: {status} - {httpreason}\nMessage: \"{message}\"
    """
    
    MSG_SPOTIFY_WEB_API_AUTH_ERROR:str = "SAM1002E - Spotify Web API returned an authorization error status while processing the \"{methodname}\" method.\nHTTP Status: {httpstatus} - {httpreason}\nError: {error}\nError Description: \"{errordescription}\""
    """
    SAM1002E - Spotify Web API returned an authorization error status while processing the \"{methodname}\" method.\nHTTP Status: {httpstatus} - {httpreason}\nError: {error}\nError Description: \"{errordescription}\"
    """
    
    MSG_SPOTIFY_WEB_API_RETRY_REQUEST_DELAY:str = "Delaying for %s seconds before retry to allow Spotify Gateway to become available"
    """
    Delaying for %s seconds before retry to allow Spotify Gateway to become available
    """

    MSG_SPOTIFY_WEB_API_RETRY_RESPONSE_STATUS:str = "Spotify Web API request returned with a %s status (%s); request will be retried"
    """
    Spotify Web API request returned with a %s status (%s); request will be retried
    """

    MSG_SPOTIFY_WEB_API_RETRY_TIMEOUT:str = "Timed out waiting for Spotify Gateway to become available; gave up after %f seconds from initial request."
    """
    Timed out waiting for Spotify Gateway to become available; gave up after %f seconds from initial request.
    """

    MSG_SPOTIFY_ZEROCONF_API_ERROR:str = "SAM1003E - Spotify ZeroConf API returned an error status while processing the \"{methodname}\" method.\nStatus: {status} - {httpreason}\nMessage: \"{message}\""
    """
    SAM1001E - Spotify ZeroConf API returned an error status while processing the \"{methodname}\" method.\nStatus: {status} - {httpreason}\nMessage: \"{message}\"
    """
    
    MSG_SPOTIFY_ACCOUNT_REQUIRED_FOR_NOWPLAYING:str = "SAM1004E - A Spotify Free or Premium level membership is required to get currently playing item information."
    """
    SAM1004E - A Spotify Premium level membership is required to get currently playing item information.
    """
    
    MSG_SPOTIFY_ACTIVATE_CREDENTIAL_REQUIRED:str = "SAM1005E - The \"%s\" configuration option was not supplied, which is required in order to reactivate a Spotify Connect device."
    """
    SAM1005E - The \"%s\" configuration option was not supplied, which is required in order to reactivate a Spotify Connect device.
    """
       
    MSG_SPOTIFY_DEPRECATED_ENDPOINT_20241127:str = "SAM1010E - The \"%s\" endpoint has been deprecated by Spotify without prior notice as of November 27th 2024, and the supporting functionality is no longer available."
    """
    SAM1010E - The \"%s\" endpoint has been deprecated by Spotify without prior notice as of November 27th 2024, and the supporting functionality is no longer available.
    """

    MSG_SPOTIFY_DEPRECATED_ENDPOINT_20260211:str = "SAM1010E - The \"%s\" endpoint has been deprecated by Spotify without prior notice as of February 11th 2026, and the supporting functionality is no longer available."
    """
    SAM1010E - The \"%s\" endpoint has been deprecated by Spotify without prior notice as of February 11th 2026, and the supporting functionality is no longer available.
    """

    MSG_SPOTIFY_WEB_PLAYER_TOKEN_INUSE:str = "Spotify Web Player authorization access token will be used for accessing Spotify Web API endpoint."
    """
    Spotify Web Player authorization access token will be used for accessing Spotify Web API endpoint.
    """

    MSG_SPOTIFY_WEB_PLAYER_TOKEN_REFRESHED:str = "Converting Spotify Web Player cookie credentials to an access token for loginId \"%s\"."
    """
    Converting Spotify Web Player cookie credentials to an access token for loginId \"%s\".
    """
