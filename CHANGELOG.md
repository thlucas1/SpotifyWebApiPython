## Change Log

All notable changes to this project are listed here.  

Change are listed in reverse chronological order (newest to oldest).  

<span class="changelog">

###### [ 1.0.25 ] - 2023/02/10

  * Updated urllib3 requirements to "urllib3>=1.21.1,<1.27", to ensure urllib3 version 2.0 is not used.  Home Assistant requires urllib3 version less than 2.  This was causing intermittent issues with calling requests resulting in **kwargs errors when used in Home Assistant!

###### [ 1.0.24 ] - 2023/02/10

  * Updated `SpotifyClient.MakeRequest` method to pass ALL parameters in the various request methods.  Prior to this fix, there were urllib3 request issues with **KWARGS while using the api in a Home Assistant integration.

###### [ 1.0.23 ] - 2023/02/09

  * Updated `SpotifyClient.MakeRequest` method to use json library to create JSON request body, instead of the urllib3 `request(...,json=...)` method.  The urllib3 `request` class seems to have issues processing json data.

###### [ 1.0.22 ] - 2023/02/09

  * Added `SpotifyClient.GetIdFromUri` method to return the Id portion of a Uri value.
  * Added `SpotifyClient.GetTypeFromUri` method to return the Type portion of a Uri value.
  * Updated `SpotifyClient.GetPlayerDevice` method to return a selected device by id or name.
  * Added `SpotifyDiscovery` class that discovers Spotify Connect devices via Zeroconf.
  * Updated `UserProfileSimplified` method to default the `DisplayName` property to the `Id` property value if a display name was not set.

###### [ 1.0.21 ] - 2023/02/08

  * Added `SearchResponse.GetSpotifyOwnedPlaylists` method that gets a list of all playlist items in the underlying search response that have an owner of `spotify:user:spotify`.  These are playlists that are generated for you by the spotify ai engine.
  * Added `additionalTypes` argument to `SpotifyClient.GetPlayerPlaybackState` method.
  * Added `additionalTypes` argument to `SpotifyClient.GetPlayerNowPlaying` method.
  * Updated `SpotifyClient.GetPlayerDevices` method to return the list of devices in sorted order by Name.

###### [ 1.0.20 ] - 2023/02/07

  * Added `PlayHistoryPage.GetTracks` method that gets a list of all tracks contained in the underlying `PlayHistory` list.  This is a convenience method so one does not have to loop through the `PlayHistory` array of `Track` objects to get the list of tracks.

###### [ 1.0.19 ] - 2023/02/07

  * Updated `TrackPageSaved` model to parse a `Track` object instead of a `TrackSimplified` object.  The `Track` object contains the extra `Album`, `ExternalIds` and `Popularity` properties.
  * Updated `TrackRecommendations` model to parse a `Track` object instead of a `TrackSimplified` object.  The `Track` object contains the extra `Album`, `ExternalIds` and `Popularity` properties.
  * Added `AlbumPageSaved.GetAlbums` method that gets a list of all albums contained in the underlying `Items` list.  This is a convenience method so one does not have to loop through the `Items` array of `AlbumSaved` objects to get the list of albums.
  * Added `TrackPageSaved.GetTracks` method that gets a list of all tracks contained in the underlying `Items` list.  This is a convenience method so one does not have to loop through the `Items` array of `TrackSaved` objects to get the list of tracks.
  * Added `EpisodePageSaved.GetEpisodes` method that gets a list of all episodes contained in the underlying `Items` list.  This is a convenience method so one does not have to loop through the `Items` array of `EpisodeSaved` objects to get the list of episodes.
  * Added `ShowPageSaved.GetShows` method that gets a list of all shows contained in the underlying `Items` list.  This is a convenience method so one does not have to loop through the `Items` array of `ShowSaved` objects to get the list of shows.
  * Added an `ImageUrl` property to all models that have an `Images` collection.  The new property returns the first image url in the `Images` list, if images are defined; otherwise, null.  This is a convenience method so one does not have to loop through the `Images` array of `ImageObject` objects to get an image url.

###### [ 1.0.18 ] - 2023/02/05

  * Updated `SpotifyClient` methods to set the request header authorization key directly, rather than assigning a new dictionary to the value.
  * Updated `SpotifyClient.MakeRequest` method to apply token refresh changes to the request authorization header if present.  Prior to this fix, the request was still referencing the expired token value.
  * Added `SpotifyAuthToken.HeaderKey` property for request header access.
  * Added `SpotifyAuthToken.HeaderValue` property for request header access.
  * Removed `SpotifyAuthToken.GetHeaders` method, as it was no longer required.

###### [ 1.0.17 ] - 2023/02/04

  * Updated `SpotifyClient` to correctly support the `tokenUpdater` callable to update a token for an external provider.
  * Updated `AuthClient` to correctly support the `tokenUpdater` callable to update a token for an external provider.

###### [ 1.0.16 ] - 2023/02/02

  * Updated numerous classes with a `ToDictionary` method to allow dictionary representation of data.

###### [ 1.0.15 ] - 2023/02/02

  * Updated `SpotifyClient` methods with better logging information.
  * Updated `AuthClient` methods with better logging information.

###### [ 1.0.14 ] - 2023/02/01

  * Updated `SpotifyClient` methods to add basic validation for required parameter values.

###### [ 1.0.13 ] - 2023/02/01

  * Updated `SpotifyClient._CheckResponseForErrors` method to use json library to parse JSON response, instead of the urllib3 `HTTPResponse.json()` method.  The urllib3 `HTTPResponse` class can return missing attributes and methods when processing redirects.

###### [ 1.0.12 ] - 2023/02/01

  * Updated `SpotifyClient._CheckResponseForErrors` method with better logging information.

###### [ 1.0.11 ] - 2023/02/01

  * Updated `SpotifyClient._CheckResponseForErrors` method with better logging information.

###### [ 1.0.10 ] - 2023/02/01

  * Added `SpotifyClient.SetAuthTokenFromToken` method to allow the authorization token to be used from an existing OAuth2 token.
  * Removed `SpotifyClient.SetAuthTokenFromSession` method in favor of the `SetAuthTokenFromToken` method.
  * Updated scope processing to pass a space-delimited string of scopes instead of an array of strings.  It appears that the Spotify Web API will accept both, but API documentation states that a space-delimited string is preferred.

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