# our package imports.
# none.

# constants are placed in this file if they are used across multiple files.
# the only exception to this is for the VERSION constant, which is placed here for convenience.

VERSION:str = "1.0.97"
""" 
Current version of the Spotify Client Python3 Library. 
"""

PACKAGENAME:str = "spotifywebapiPython"
"""
Name of our package (used by PDoc Documentation build).
"""

# properties used in PDOC documentation build.

PDOC_BRAND_ICON_URL:str = "https://developer.spotify.com/documentation/web-api"
"""
PDoc Documentation brand icon link url that is displayed in the help document TOC.  
"""

PDOC_BRAND_ICON_URL_SRC:str = "spotifywebapipython.ico"
"""
PDoc Documentation brand icon link url that is displayed in the help document TOC.  
"""

PDOC_BRAND_ICON_URL_TITLE:str = "A Spotify Web Api Client"
"""
PDoc Documentation brand icon link title that is displayed in the help document TOC.  
"""

# miscellaneous constants.
SPOTIFY_API_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
""" Url used to request user authorization permission for an authorization token. """
    
SPOTIFY_API_TOKEN_URL = "https://accounts.spotify.com/api/token"
""" Url used to request or renew a Spotify authorization token. """
    
SPOTIFY_WEBAPI_URL_BASE = "https://api.spotify.com/v1"
""" Url base name used to access tthe Spotify Web API. """

SPOTIFY_DEFAULT_MARKET:str = "US"
""" 
Default country code to use if a country code was not supplied on a request and the 
UserProfile.Country value is not set (e.g. public access token in effect. 

Default value is "US".
"""

SPOTIFY_DESKTOP_APP_CLIENT_ID:str = '65b708073fc0480ea92a077233ca87bd'
"""
Spotify Desktop Application client id.
"""

SPOTIFYWEBAPIPYTHON_TOKEN_CACHE_FILE:str = 'SpotifyWebApiPython_tokens.json'
"""
Filename and extension of the authorization Token Cache file (`SpotifyWebApiPython_tokens.json`).
"""

TRACE_METHOD_RESULT = "%s result"
""" 
%s result
"""

TRACE_METHOD_RESULT_TYPE = "%s result - %s object "
""" 
%s result - %s object
"""

TRACE_METHOD_RESULT_TYPE_CACHED = "%s result - %s object (%s)"
""" 
%s result - %s object (%s)
"""

TRACE_METHOD_RESULT_TYPE_PAGE = "%s page result - %s object "
""" 
%s page result - %s object
"""

TRACE_MSG_AUTHTOKEN_CREATE = "Creating a \"%s\" authorization access token"
""" 
Creating a \"%s\" authorization access token
"""

TRACE_MSG_DELAY_DEVICE:str = "Delaying for %s seconds to allow Spotify API to process the change"
"""
Delaying for %s seconds to allow Spotify API to process the change
"""

TRACE_MSG_USERPROFILE = 'User Profile Object: DisplayName="%s", EMail="%s"'
""" 
User Profile Object: DisplayName="%s", EMail="%s"
"""

TRACE_MSG_AUTOPAGING_NEXT = "Requesting next page of items %s"
""" 
Requesting next page of items %s
"""

TRACE_WARN_SPOTIFY_SEARCH_NO_MARKET:str = "Warning - Market value (aka country code) was not specified for '%s' search request, and user profile did not have a country code set.  This may cause Spotify Web API to return some weird results, or even cause an exception!"
"""
Warning - Market value (aka country code) was not specified for '%s' search request, and user profile did not have a country code set.  This may cause Spotify Web API to return some weird results, or even cause an exception!
"""
    