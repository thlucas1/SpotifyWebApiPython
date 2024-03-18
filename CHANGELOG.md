## Change Log

All notable changes to this project are listed here.  

Change are listed in reverse chronological order (newest to oldest).  

<span class="changelog">

###### [ 1.0.34 ] - 2024/03/18

  * Fixed `SpotifyClient.CreatePlaylist` method to properly pass the Public and Collaborative parameters to the Spotify Web API.  Prior to this, any created playlists were being marked with Public=True.

###### [ 1.0.33 ] - 2024/03/02

  * Added `Device.SelectItemNameAndId` property to return a string that can be used in a selection list in the form of "Name (Id)".
  * Added `Device.GetIdFromSelectItem` method to return the Id portion of a `SelectItemNameAndId` property value.
  * Added `Device.GetNameFromSelectItem` method to return the Name portion of a `SelectItemNameAndId` property value.

###### [ 1.0.32 ] - 2024/02/28

  * Updated `PlayerQueueInfo` to correctly return the `Summary` property value when the queue is empty.
  * Removed `SpotifyClient.SearchPlaylists` method argument `spotifyOwnedOnly`, as it can be replaced by other functionality (e.g. `GetCategoryPlaylists`).

###### [ 1.0.31 ] - 2024/02/27

  * Updated all models that used a `root.get('...',[])` syntax to use `root.get('...',None)` instead, as Spotify Web API will sometimes return a `null` instead of an `[]` (empty array) for a key item value.  This was causing methods to fail with `'NoneType' object is not iterable` errors.

###### [ 1.0.30 ] - 2024/02/23

  * Updated `SpotifyClient.SearchPlaylists` method with argument `spotifyOwnedOnly` to filter found items by owner.  This simulates the spotify "content generated for you" functionality provided by the Spotify AI engine.

###### [ 1.0.29 ] - 2024/02/23

  * Added `ContainsId` method to the following classes: `AlbumPageSimplified`, `AudiobookPageSimplified`, `ChapterPageSimplified`, `EpisodePageSimplified`, `PlaylistPageSimplified`, `ShowPageSimplified`, and `TrackPageSimplified`.
  * Updated `SpotifyClient.GetPlayerRecentTracks` method with auto-pagination support to retrieve ALL available items (or up to a limit total).

###### [ 1.0.28 ] - 2024/02/21

  * Added `SpotifyClient.SearchAlbums` method to search Spotify for matching Album criteria.
  * Added `SpotifyClient.SearchArtists` method to search Spotify for matching Artist criteria.
  * Added `SpotifyClient.SearchAudiobooks` method to search Spotify for matching Audiobook criteria.
  * Added `SpotifyClient.SearchEpisodes` method to search Spotify for matching Episode criteria.
  * Added `SpotifyClient.SearchPlaylists` method to search Spotify for matching Playlist criteria.
  * Added `SpotifyClient.SearchShows` method to search Spotify for matching Show criteria.
  * Added `SpotifyClient.SearchTracks` method to search Spotify for matching Track criteria.
  * Updated `SpotifyClient` methods to add auto-pagination to retrieve ALL available items (or up to a limit total).  Methods modified were: `GetAlbumFavorites`, `GetAlbumNewReleases`, `GetArtistAlbums`, `GetArtistsFollowed`, `GetCategoryPlaylists`, `GetFeaturedPlaylists`, `GetPlaylistFavorites`, `GetPlaylistsForUser`, `GetPlaylistItems`, `GetAlbumTracks`, `GetAudiobookChapters`, `GetAudiobookFavorites`, `GetBrowseCategorys`, `GetEpisodeFavorites`, `GetShowEpisodes`, `GetShowFavorites`, `GetTrackFavorites`, `GetUsersTopArtists`, `GetUsersTopTracks`.
  * Renamed `SpotifyClient.GetBrowseCategorys` method to `GetBrowseCategorysList`.
  * Renamed `SpotifyClient.GetBrowseCategorysByPage` method to `GetBrowseCategorys`.
  * Added `Category.Uri` property to simulate a Spotify-like Uri value for a category.  This is a helper property - no value with this name is returned from the Spotify Web API.
  * Updated `PageObject` model with property setters for the `CursorBefore`, `CursorAfter`, `Limit`, `Offset` and `Total` properties.  This allows a user to modify the values when performing custom paging operations.
  * Updated all `SpotifyClient` methods that utilize a `market` argument to ensure that a market value was either supplied or implied (using an authorization access token with a user profile).  The Spotify Web API was returning null results for some methods that did not supply a market value while using a public access token (e.g. no country code default).

###### [ 1.0.27 ] - 2024/02/20

  * Updated `SpotifyClient.GetPlayerRecentTracks` method to retrieve the last 24 hours of play history if neither `after` or `before` arguments were specified.

###### [ 1.0.26 ] - 2024/02/15

  * Added `SpotifyClient.ToString` method to display a string representation of the class.
  * Added `SpotifyClient.ConfigurationCache` property to store static configuration objects.
  * Added `SpotifyClient.ClearConfigurationCache` method to clear the configuration cache.
  * Updated `SpotifyClient` methods to add returned results to the `ConfigurationCache` for faster access: `GetBrowseCategory`, `GetBrowseCategorys`, `GetGenres`, `GetMarkets`, `GetPlayerDevice`, `GetPlayerDevices`, `GetUsersCurrentProfile`.  This increases performance when accessing Spotify information that rarely changes.

###### [ 1.0.25 ] - 2024/02/10

  * Updated urllib3 requirements to "urllib3>=1.21.1,<1.27", to ensure urllib3 version 2.0 is not used.  Home Assistant requires urllib3 version less than 2.  This was causing intermittent issues with calling requests resulting in **kwargs errors when used in Home Assistant!

###### [ 1.0.24 ] - 2024/02/10

  * Updated `SpotifyClient.MakeRequest` method to pass ALL parameters in the various request methods.  Prior to this fix, there were urllib3 request issues with **KWARGS while using the api in a Home Assistant integration.

###### [ 1.0.23 ] - 2024/02/09

  * Updated `SpotifyClient.MakeRequest` method to use json library to create JSON request body, instead of the urllib3 `request(...,json=...)` method.  The urllib3 `request` class seems to have issues processing json data.

###### [ 1.0.22 ] - 2024/02/09

  * Added `SpotifyClient.GetIdFromUri` method to return the Id portion of a Uri value.
  * Added `SpotifyClient.GetTypeFromUri` method to return the Type portion of a Uri value.
  * Updated `SpotifyClient.GetPlayerDevice` method to return a selected device by id or name.
  * Added `SpotifyDiscovery` class that discovers Spotify Connect devices via Zeroconf.
  * Updated `UserProfileSimplified` method to default the `DisplayName` property to the `Id` property value if a display name was not set.

###### [ 1.0.21 ] - 2024/02/08

  * Added `SearchResponse.GetSpotifyOwnedPlaylists` method that gets a list of all playlist items in the underlying search response that have an owner of `spotify:user:spotify`.  These are playlists that are generated for you by the spotify ai engine.
  * Added `additionalTypes` argument to `SpotifyClient.GetPlayerPlaybackState` method.
  * Added `additionalTypes` argument to `SpotifyClient.GetPlayerNowPlaying` method.
  * Updated `SpotifyClient.GetPlayerDevices` method to return the list of devices in sorted order by Name.

###### [ 1.0.20 ] - 2024/02/07

  * Added `PlayHistoryPage.GetTracks` method that gets a list of all tracks contained in the underlying `PlayHistory` list.  This is a convenience method so one does not have to loop through the `PlayHistory` array of `Track` objects to get the list of tracks.

###### [ 1.0.19 ] - 2024/02/07

  * Updated `TrackPageSaved` model to parse a `Track` object instead of a `TrackSimplified` object.  The `Track` object contains the extra `Album`, `ExternalIds` and `Popularity` properties.
  * Updated `TrackRecommendations` model to parse a `Track` object instead of a `TrackSimplified` object.  The `Track` object contains the extra `Album`, `ExternalIds` and `Popularity` properties.
  * Added `AlbumPageSaved.GetAlbums` method that gets a list of all albums contained in the underlying `Items` list.  This is a convenience method so one does not have to loop through the `Items` array of `AlbumSaved` objects to get the list of albums.
  * Added `TrackPageSaved.GetTracks` method that gets a list of all tracks contained in the underlying `Items` list.  This is a convenience method so one does not have to loop through the `Items` array of `TrackSaved` objects to get the list of tracks.
  * Added `EpisodePageSaved.GetEpisodes` method that gets a list of all episodes contained in the underlying `Items` list.  This is a convenience method so one does not have to loop through the `Items` array of `EpisodeSaved` objects to get the list of episodes.
  * Added `ShowPageSaved.GetShows` method that gets a list of all shows contained in the underlying `Items` list.  This is a convenience method so one does not have to loop through the `Items` array of `ShowSaved` objects to get the list of shows.
  * Added an `ImageUrl` property to all models that have an `Images` collection.  The new property returns the first image url in the `Images` list, if images are defined; otherwise, null.  This is a convenience method so one does not have to loop through the `Images` array of `ImageObject` objects to get an image url.

###### [ 1.0.18 ] - 2024/02/05

  * Updated `SpotifyClient` methods to set the request header authorization key directly, rather than assigning a new dictionary to the value.
  * Updated `SpotifyClient.MakeRequest` method to apply token refresh changes to the request authorization header if present.  Prior to this fix, the request was still referencing the expired token value.
  * Added `SpotifyAuthToken.HeaderKey` property for request header access.
  * Added `SpotifyAuthToken.HeaderValue` property for request header access.
  * Removed `SpotifyAuthToken.GetHeaders` method, as it was no longer required.

###### [ 1.0.17 ] - 2024/02/04

  * Updated `SpotifyClient` to correctly support the `tokenUpdater` callable to update a token for an external provider.
  * Updated `AuthClient` to correctly support the `tokenUpdater` callable to update a token for an external provider.

###### [ 1.0.16 ] - 2024/02/02

  * Updated numerous classes with a `ToDictionary` method to allow dictionary representation of data.

###### [ 1.0.15 ] - 2024/02/02

  * Updated `SpotifyClient` methods with better logging information.
  * Updated `AuthClient` methods with better logging information.

###### [ 1.0.14 ] - 2024/02/01

  * Updated `SpotifyClient` methods to add basic validation for required parameter values.

###### [ 1.0.13 ] - 2024/02/01

  * Updated `SpotifyClient._CheckResponseForErrors` method to use json library to parse JSON response, instead of the urllib3 `HTTPResponse.json()` method.  The urllib3 `HTTPResponse` class can return missing attributes and methods when processing redirects.

###### [ 1.0.12 ] - 2024/02/01

  * Updated `SpotifyClient._CheckResponseForErrors` method with better logging information.

###### [ 1.0.11 ] - 2024/02/01

  * Updated `SpotifyClient._CheckResponseForErrors` method with better logging information.

###### [ 1.0.10 ] - 2024/02/01

  * Added `SpotifyClient.SetAuthTokenFromToken` method to allow the authorization token to be used from an existing OAuth2 token.
  * Removed `SpotifyClient.SetAuthTokenFromSession` method in favor of the `SetAuthTokenFromToken` method.
  * Updated scope processing to pass a space-delimited string of scopes instead of an array of strings.  It appears that the Spotify Web API will accept both, but API documentation states that a space-delimited string is preferred.

###### [ 1.0.9 ] - 2024/01/31

  * Updated `SpotifyClient.SetAuthTokenFromSession` method to correct a bug related to Home Assistant OAuth2Session object.

###### [ 1.0.8 ] - 2024/01/31

  * Added `SpotifyClient.SetAuthTokenFromSession` method to allow the authorization token to be used from an existing OAuth2Session.

###### [ 1.0.7 ] - 2024/01/29

  * Allow customization of the redirect uri host and port values in the token authorization process.

###### [ 1.0.6 ] - 2024/01/29

  * Changed urllib3 requirements to a non-specific version so it could run with Home Assistant addons.

###### [ 1.0.5 ] - 2024/01/29

  * Changed Development Status to 5 - Production / Stable.

###### [ 1.0.4 ] - 2024/01/29

  * Removed invalid requirement from setup.py.

###### [ 1.0.3 ] - 2024/01/29

  * Added `SpotifyAuthToken.ProfileId` property that indicates the token profile that was loaded.

###### [ 1.0.2 ] - 2024/01/29

  * Corrected the `SpotifyClient.GetTrackRecommendations` method to process the `market`, `maxSpeechiness`, and `targetSpeechiness` arguments correctly.
  * Updated `SpotifyClient.SetAuthTokenAuthorizationCode` method to use a 120 second timeout value while waiting for an authorize response from the user.
  * Updated `SpotifyClient.SetAuthTokenAuthorizationCodePkce` method to use a 120 second timeout value while waiting for an authorize response from the user.

###### [ 1.0.1 ] - 2024/01/17

  * Version 1 initial release.

</span>