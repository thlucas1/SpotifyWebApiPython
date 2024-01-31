## Change Log

All notable changes to this project are listed here.  

Change are listed in reverse chronological order (newest to oldest).  

<span class="changelog">

###### [ 1.0.9 ] - 2023/01/31

  * Updated `SpotifyClient.SetAuthTokenFromSession` method to correct a bug related to Home Assistant OAuth2Session object.

###### [ 1.0.8 ] - 2023/01/31

  * Added `SpotifyClient.SetAuthTokenFromSession` method to allow the authorization token to be used from an existing OAuth2Session.

###### [ 1.0.7 ] - 2023/01/29

  * Allow customization of the redirect uri host and port values in the token authorization process.

###### [ 1.0.6 ] - 2023/01/29

  * Changed urllib3 requirements to a non-specific version so it could run with Home Assistant addons.

###### [ 1.0.5 ] - 2023/01/29

  * Changed Development Status to 5 - Production / Stable.

###### [ 1.0.4 ] - 2023/01/29

  * Removed invalid requirement from setup.py.

###### [ 1.0.3 ] - 2023/01/29

  * Added `SpotifyAuthToken.ProfileId` property that indicates the token profile that was loaded.

###### [ 1.0.2 ] - 2023/01/29

  * Corrected the `SpotifyClient.GetTrackRecommendations` method to process the `market`, `maxSpeechiness`, and `targetSpeechiness` arguments correctly.
  * Updated `SpotifyClient.SetAuthTokenAuthorizationCode` method to use a 120 second timeout value while waiting for an authorize response from the user.
  * Updated `SpotifyClient.SetAuthTokenAuthorizationCodePkce` method to use a 120 second timeout value while waiting for an authorize response from the user.

###### [ 1.0.1 ] - 2023/01/17

  * Version 1 initial release.

</span>