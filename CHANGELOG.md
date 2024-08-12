## Change Log

All notable changes to this project are listed here.  

Change are listed in reverse chronological order (newest to oldest).  

<span class="changelog">

###### [ 1.0.78 ] - 2024/08/12

  * Updated `ZeroconfConnect` class constructor to include the `tokenStorageDir` argument that specified the directory path that will contain the `tokens.json` cache file.  This is used for Spotify Connect devices that utilize the `authorization_code` token type.

###### [ 1.0.77 ] - 2024/08/12

  * Updated `AuthClient.AuthorizeWithServer` method to specify a redirect uri with host, port, and path values.  Prior code was only allowing a redirect uri with host and port values.
  * Added `SpotifyClient.SetAuthTokenAuthorizationCode` method argument `redirectUriPath` to allow a redirect_uri path value to be specified for OAuth authorization requests.
  * Added `SpotifyClient.SetAuthTokenAuthorizationCodePKCE` method argument `redirectUriPath` to allow a redirect_uri path value to be specified for OAuth authorization requests.
  * Updated `ZeronconfConnect` class to correctly process Spotify Connect requests for token type `authorization_code` devices.
  * Updated `SpotifyClient.PlayerMediaPlayTrackFavorites` method to add the `limitTotal` argument that limits the number of tracks retrieved from favorites.
  * Added `sortResult` argument to the following `SpotifyClient` methods: `GetAlbumFavorites`, `GetAlbumNewReleases`, `GetArtistAlbums`, `GetArtistsFollowed`, `GetAudiobookFavorites`, `GetBrowseCategorys`, `GetCategoryPlaylists`, `GetEpisodeFavorites`, `GetFeaturedPlaylists`, `GetPlayerDevices`, `GetPlaylistFavorites`, `GetPlaylistsForUser`, `GetShowFavorites`, `GetTrackFavorites`, `GetUsersTopArtists`, `GetUsersTopTracks`.  If True (default), result items are sorted by name prior to returning to the caller; otherwise, results are left in the order that the Spotify Web API returned them.

###### [ 1.0.76 ] - 2024/07/18

  * Updated `ZeroconfConnect` class to remove some test code that was accidentally left in place for tokentype `authorization_code` research.

###### [ 1.0.75 ] - 2024/07/17

  * Updated `PlayerPlayState.ShuffleState` method to return a boolean True or False value to account for changes to underlying Spotify Web API.
  * Updated `PlayerPlayState.SmartShuffle` method to return a boolean True or False value to account for changes to underlying Spotify Web API.
  
###### [ 1.0.74 ] - 2024/07/15

  * Added `SpotifyConnectDevices.GetDeviceById` method to return a `SpotifyConnectDevice` instance if the collection contains the specified device id value; otherwise, None.
  * Added `SpotifyConnectDevices.GetDeviceByName` method to return a `SpotifyConnectDevice` instance if the collection contains the specified device name value; otherwise, None.
  * Updated `ZeroconfConnect` class to use a '2.7.1' version indicator if no version argument was specified on the class contructor.
  * Updated `ZeroconfConnect.Disconnect` to check for an invalid JSON response. It has been found that some devices (Sonos, etc) do not return a proper JSON response for the `resetUsers` action.  If a JSON response was not returned, then it will treat the http status code as the response code; if it's not a 200, then it will raise an exception.
  * Updated `SpotifyClient.PlayerResolveDeviceId` method to not switch the active user context for Sonos devices.  Sonos devices are restricted, and (currently) cannot be controlled by the Spotify Web-Services API player methods.

###### [ 1.0.73 ] - 2024/07/02

  * Updated `SpotifyClient.GetSpotifyConnectDevices` to gracefully handle device unavailable scenarios.  It will try to reach the device by its direct HostIpAddress first; if that fails, then it will try to reach the device by its Server alias; if that fails, then it will log a warning that the device could not be reached and press on.
  * Updated `ZeroconfConnect.Disconnect` to check for an invalid JSON response. It has been found that some devices (Sonos, etc) do not return a proper JSON response for the `resetUsers` action.  If a JSON response was not returned, then it will treat the http status code as the response code; if it's not a 200, then it will raise an exception.
  * Updated `BlobBuilder` methods to add tracing of blob data contents.

###### [ 1.0.72 ] - 2024/06/28

  * Updated `ZeroconfConnect.Connect` method to handle the `authorization_code` token type for Zeroconf API `addUser` requests.

###### [ 1.0.71 ] - 2024/06/27

  * Updated `ZeroconfConnect.Connect` method to properly return the response data from the `addUser` request and process the results.

###### [ 1.0.70 ] - 2024/06/27

  * Updated `ZeroconfConnect.Connect` method to properly wait for device to become fully availabile if need be.

###### [ 1.0.69 ] - 2024/06/26

  * Added properties and arguments to support the Zeroconf API `loginId` argument for the `addUser` request.
  * Updated `ZeroconfConnect.Connect` method to include the `deviceName` and `deviceId` keys for the `addUser` request for certain device manufacturer conditions.
  * Updated `ZeroconfConnect.Connect` method to not issue a Disconnect to reset the user context if the public key value is "INVALID", as the logic did not work as expected.

###### [ 1.0.68 ] - 2024/06/26

  * Updated `ZeroconfConnect._CheckResponseForErrors` method to not process the Spotify Zeroconf API response, as each method calling the check response method will process the returned status.

###### [ 1.0.67 ] - 2024/06/25

  * Updated `SpotifyClient.IsDeviceId` class to recognize UUID-formatted device id's (e.g. "48b677ca-ef9b-516f-b702-93bf2e8c67ba").
  * Updated `ZeroconfConnect` class to not default the `version` value to `1.0`, in the event that newer devices may not support that version identifier.
  * Updated `ZeroconfConnect.Connect` method to not pass the `loginId` parameter to the request.
  * Updated `ZeroconfConnect.Connect` method to issue a Disconnect to reset the user context if the public key value is "INVALID".

###### [ 1.0.66 ] - 2024/06/25

  * Updated `ZeroconfResponse` class to convert the `status` and `spotifyError` values to numeric from string.  Some Spotify Connect devices return them as strings, while other return them as numerics.  

###### [ 1.0.65 ] - 2024/06/25

  * Updated `ZeroconfConnect.Connect` method to account for "ERROR-INVALID-PUBLICKEY" statuses returned for some devices.  This will retry the connection request with the PublicKey value returned from the initial request.

###### [ 1.0.64 ] - 2024/06/24

  * Updated `SpotifyClient.GetSpotifyConnectDevices` method to correctly set the currently active device.

###### [ 1.0.63 ] - 2024/06/24

  * Updated `ZeroconfConnect` class to process the Spotify Zeroconf API status code from the JSON response instead of processing the HTTP request status code.  It has been found that some Spotify Connect manufacturers return different HTTP status codes than other manufacturers; but the Spotify Connect `status`, `statusString` and `spotifyError` JSON properties seem to be consistent across the board.
  * Updated `SpotifyClient.GetSpotifyConnectDevices` method to filter out duplicate Spotify Connect Device entries for devices that have been grouped together.  For example, the "Bose-ST10-1" and "Bose-ST10-2" are grouped as a stereo pair; there will be two Zeroconf discovery result entries with different instance names, but their Zeroconf getInfo endpoint url will be the same.  When this happens, it causes the values to show up as duplicates if we process both of them.

###### [ 1.0.62 ] - 2024/06/21

  * Updated `SpotifyDiscovery.DiscoverDevices` method to properly free Zeroconf resources after service discovery, and prevent possible memory leaks and crashes due to running out of resources.

###### [ 1.0.61 ] - 2024/06/21

  * Added `ZeroconfGetInfo.IsInDeviceList` property that returns the status of active device list verification process (Verification not Performed, Verified Active, Verified Inactive).  

###### [ 1.0.60 ] - 2024/06/21

  * Updated `ZeroconfConnect` class to process all responses as JSON responses.  It was found that some Spotify Zeroconf API capable devices were not properly setting the `Content-Type` in the returned http response header.
  * Updated `SpotifyDiscovery` class to process the individual Spotify Connect instance names that were discovered via Zeroconf.  Prior logic was adding a device for every IPV4 address that was found for an instance, assuming that each instance only contained one IP address; some services contain multiple IP addressess for the same instance name (specifically, the `SpotifyConnect` add-on, which runs in a docker container).
  * Updated `SpotifyDiscovery` class to rename the `HostIpv4Address` property (and method arguments) to `HostIpAddress`.  The address specified in this argument can be an IP address (e.g. "192.168.1.81") or an alias (e.g. "bose.speaker.kitchen").
  * Updated `ZeroconfConnect` class to rename the `HostIpv4Address` property (and method arguments) to `HostIpAddress`.  The address specified in this argument can be an IP address (e.g. "192.168.1.81") or an alias (e.g. "bose.speaker.kitchen").
  * Updated various `SpotifyClient` methods to utilize the default `HostIpAddress` (or `Server` value if default `HostIpAddress` was not discovered) when connecting to a Spotify Connect capable device.  Methods updated were: `PlayerActivateDevices`, `GetSpotifyConnectDevices`, `PlayerResolveDeviceId`.

###### [ 1.0.59 ] - 2024/06/19

  * Updated `SpotifyClient` methods that call `PlayerResolveDeviceId` with a new parameter that indicates if the device should be resolved (true) or not (False).  This allows multiple methods that call `PlayerResolveDeviceId` to be called from the same method, and only resolve the device one time.  This was sone to ensure that device resolution did not occur more than once, as it's such a time consuming operation.  Methods updated were: `PlayerMediaPlayContext`, `PlayerMediaPlayTrackFavorites`, `PlayerMediaPlayTracks`, `PlayerTransferPlayback`.

###### [ 1.0.58 ] - 2024/06/19

  * Updated `SpotifyClient.PlayerResolveDeviceId` method callers to log a warning message if the specified device value could not be resolved and just return a null value.

###### [ 1.0.57 ] - 2024/06/19

  * Updated `SpotifyClient.PlayerResolveDeviceId` method callers to gracefully handle the `SpotifyApiError` error if the specified device value could not be resolved.

###### [ 1.0.56 ] - 2024/06/19

  * Updated `SpotifyClient.PlayerResolveDeviceId` method to raise a `SpotifyApiError` error if the specified device value could not be resolved.

###### [ 1.0.55 ] - 2024/06/19

  * Updated `SpotifyConnectDevices` model to include a `DateLastRefreshed` property that indicates when the device list was last refreshed.

###### [ 1.0.54 ] - 2024/06/19

  * Updated `SpotifyClient.GetSpotifyConnectDevices` method to store results to the configuration cache.

###### [ 1.0.53 ] - 2024/06/18

  * Updated `ZeroconfConnect.Connect` method to provide a small delay after processing the Spotify Zeroconf API command, which will give the device some time to process the change.
  * Updated `ZeroconfConnect.Disconnect` method to provide a small delay after processing the Spotify Zeroconf API command, which will give the device some time to process the change.

###### [ 1.0.52 ] - 2024/06/18

  * Updated `SpotifyClient.GetSpotifyConnectDevices` method to retrieve dynamic Spotify Connect devices as well as static devices.  Dynamic devices are Spotify Connect devices that are not found in Zeroconf discovery process, but still exist in the player device list.  These are usually Spotify Connect web or mobile players with temporary device id's.

###### [ 1.0.51 ] - 2024/06/18

  * Added `SpotifyClient.GetSpotifyConnectDevices` method that gets information about all available Spotify Connect player devices (not just ones controlled by a user).

###### [ 1.0.50 ] - 2024/06/18

  * Added `SpotifyClient.ZeroconfClient` property that contains a reference to the Zeroconf client instance used to discover Spotify Connect devices.
  * Added `SpotifyDiscovery.ZeroconfClient` property that contains a reference to the Zeroconf client instance used to discover Spotify Connect devices.

###### [ 1.0.49 ] - 2024/06/18

  * Added `SpotifyClient.PlayerActivateDevices` method that activates all Spotify Connect player devices, and (optionally) switches the active user context to the current user context.  Note that you can still activate individual devices using the `ZeroconfConnect.Connect` method if you wish.
  * Added `SpotifyClient.PlayerResolveDeviceId` method that resolves a Spotify Connect device identifier from a specified device id, name, alias id, or alias name.  This will ensure that the device id can be found on the network, as well as connect to the device (if necessary) with the current user context.  
  * Updated various `SpotifyClient` methods to utilize the new `SpotifyClient.PlayerResolveDeviceId` method so that device id's are automatically activated if they are currently deactivated but available on the local network.  Methods updated were: `PlayerMediaPlayContext`, `PlayerMediaPlayTrackFavorites`, `PlayerMediaPlayTracks`, `PlayerTransferPlayback`.
  * Updated `SpotifyClient` class constructor so that Spotify Connect user context credentials (e.g. username and password) may be supplied for the resolution of device id / name.  Note these credentials are only used for Spotify Connect device resolution, and are not used by method calls that are made to the underlying Spotify Web API.
  * Updated `SpotifyDiscovery` class constructor so that a `Zeroconf` instance can be provided.  This allows Home Assistant integrations to use the HA Zeroconf instance and avoid the log warnings of multiple Zeroconf instances in use.
  * Removed `SpotifyClient` processing from the `SpotifyDiscovery` class, as the processing was moved into the `SpotifyClient` class itself.
  
###### [ 1.0.48 ] - 2024/06/10

  * Forgot to re-build prior to deploying!
  
###### [ 1.0.47 ] - 2024/06/10

  * Moved all Spotify Zeroconf API related classes to a new namespace called `zeroconfapi`.  Classes moved were: `ZeroconfResponse`, `ZeroconfGetInfo`, `ZeroconfGetInfoAlias`, `ZeroconfGetInfoDrmMediaFormat`.
  * Added `ZeroconfConnect` class that contains various methods that support interfacing with the Spotify Zeroconf API.
  * Added `ZeroconfConnect.Connect` method that calls the `addUser` Spotify Zeroconf API endpoint to issue a call to SpConnectionLoginBlob.  If successful, the associated device id is added to the Spotify Connect active device list for the specified user account.
  * Added `ZeroconfConnect.Disconnect` method that calls the `resetUsers` Spotify Zeroconf API endpoint to issue a call to SpConnectionLogout; the currently logged in user (if any) will be logged out of Spotify Connect, and the device id removed from the active Spotify Connect device list.
  * Added `ZeroconfConnect.GetInformation` method that calls the `getInfo` Spotify Zeroconf API endpoint to return information about the device.
  * Removed `SpotifyClient.ZeroconfAddUser` method, and replaced it with method `ZeroconfConnect.Connect`.
  * Removed `SpotifyClient.ZeroconfResetUsers` method, and replaced it with method `ZeroconfConnect.Disconnect`.
  * Removed `SpotifyClient.ZeroconfGetInformation` method, and replaced it with method `ZeroconfConnect.GetInformation`.

###### [ 1.0.46 ] - 2024/06/07

  * Updated the following requirements due to Home Assistant dependency issues: 'oauthlib>=3.2.2', 'platformdirs>=4.1.0', 'requests>=2.31.0', 'requests_oauthlib>=1.3.1', 'zeroconf>=0.132.2'.

###### [ 1.0.45 ] - 2024/06/07

  * Updated `zeroconf` requirements to "zeroconf>=0.132.2".  This was causing installation issues with other components that utilize zeroconf.

###### [ 1.0.44 ] - 2024/06/07

  * Added `SpotifyDiscovery.DiscoveredResults` class property that will contain an array of `ZeroconfDiscoveryResult` items that contain discovery details for each service that was discovered.
  * Added model `ZeroconfDiscoveryResult` class that contains detailed Zeroconf ServiceInfo details that were discovered via Zeroconf.
  * Added model `ZeroconfProperty` class that contains Zeroconf ServiceInfo property details that were discovered via Zeroconf.
  * Added model `ZeroconfResponse` class that contains Zeroconf basic response variables.
  * Added model `ZeroconfGetInfo` class that contains Zeroconf action=getInfo response variables.
  * Added model `ZeroconfGetInfoAlias` class that contains Zeroconf action=getInfo Alias response variables.
  * Added model `ZeroconfGetInfoDrmMediaFormat` class that contains Zeroconf action=getInfo DRM Media format response variables.
  * Added logic to handle `503 Server Error` responses from the Spotify Web API.
  * Added support for Spotify DJ playlist retrieval.  As the Spotify Web API does not support retrieving the DJ playlist (`spotify:playlist:37i9dQZF1EYkqdzj48dyYq`), it simply returns a manually built representation of the playlist.  Note that playlist tracks cannot be retrieved either for the DJ playlist, as the Spotify Web API does not support it.

###### [ 1.0.43 ] - 2024/04/21

  * Added device name support to the following player methods that take a `deviceId` argument for player functions.  You can now specify either a device id or device name in the `deviceId` argument to target a specific Spotify Connect Player device.  `SpotifyClient` methods updated were: `AddPlayerQueueItem`, `PlayerMediaPause`, `PlayerMediaPlayContext`, `PlayerMediaPlayTrackFavorites`, `PlayerMediaPlayTracks`, `PlayerMediaResume`, `PlayerMediaSeek`, `PlayerMediaSkipNext`, `PlayerMediaSkipPrevious`, `PlayerSetRepeatMode`, `PlayerSetShuffleMode`, `PlayerSetVolume`, `PlayerTransferPlayback`.
  * Added `SpotifyClient.PlayerConvertDeviceNameToId` method that converts a Spotify Connect player device name to it's equivalent id value if the value is a device name.  If the value is a device id, then the value is returned as-is.

###### [ 1.0.42 ] - 2024/04/05

  * Added `Device.IsMuted` property to indicate if volume is zero (muted) or not (unmuted).
  * Added `PlayerPlayState.IsMuted` property to indicate if player device volume is zero (muted) or not (unmuted).
  * Updated `SpotifyClient.PlayerMediaPlayTrackFavorites` method to set the shuffle mode prior to starting play of the track list.  Prior to this change, the first track would always play first regardless of the shuffle setting; now it is part of the shuffle.

###### [ 1.0.41 ] - 2024/04/02

  * Added `ArtistInfo` model that contains artist bio information.
  * Added `ArtistInfoTourEvent` model that contains artist on tour event information.
  * Added `SpotifyClient.GetArtistInfo` method to retrieve artist bio information for a specified Artist id.
  * Added `SpotifyClient.PlayerMediaPlayTrackFavorites` method to play all tracks contained in the current users track favorites.
  * Added `SpotifyClient.RemovePlaylist` method to remove a playlist by calling the `UnfollowPlaylist` method.

###### [ 1.0.40 ] - 2024/03/26

  * Updated `SpotifyClient.PlayerVerifyDeviceDefault` method to check for a null `Device.Id` value when determining if an active device was set.
  * Added `delay` argument to various `SpotifyClient` player command-related methods, which allows the Spotify Web API a little bit of time to process the change before returning from the method.  Methods updated: `PlayerMediaPause`, `PlayerMediaPlayContext`, `PlayerMediaPlayTracks`, `PlayerMediaResume`, `PlayerMediaSeek`, `PlayerMediaSkipNext`, `PlayerMediaSkipPrevious`, `PlayerSetRepeatMode`, `PlayerSetShuffleMode`, `PlayerSetVolume`, `PlayerTransferPlayback`, `PlayerVerifyDeviceDefault`.  Default delay is 250 milliseconds, but you can adjust accordingly (including removing the delay if you wish).

###### [ 1.0.39 ] - 2024/03/26

  * Updated `PlayerPlayState.__init__` model to properly parse the Actions property.

###### [ 1.0.38 ] - 2024/03/26

  * Updated `Device.__init__` model to validate the following properties were initialized from Spotify Web API results, and to set defaults if not: IsActive = False, IsPrivateSession = False, IsRestricted = False, SupportsVolume = False, VolumePercent = 0.
  * Updated `PlayerPlayState.__init__` model to validate the following properties were initialized from Spotify Web API results, and to set defaults if not: Actions = PlayerActions(), Device = Device(), CurrentlyPlayingType = 'unknown', IsPlaying = False, ProgressMS = 0, RepeatState = 'off', ShuffleState = 'off', SmartShuffle = 'off', Timestamp = 0.
  * Updated `PlayerActions.__init__` model to validate the following properties were initialized from Spotify Web API results, and to set defaults if not: InterruptingPlayback = False, Pausing = False, Resuming = False, Seeking = False, SkippingNext = False, SkippingPrev = False, TogglingRepeatContext = False, TogglingRepeatTrack = False,  TogglingShuffle = False, TransferringPlayback = False.

###### [ 1.0.37 ] - 2024/03/19

  * Updated `SpotifyClient.FollowArtists` method to make the `ids` argument optional; if not supplied, the currently playing track artist id value is used instead.
  * Updated `SpotifyClient.UnfollowArtists` method to make the `ids` argument optional; if not supplied, the currently playing track artist id value is used instead.
  * Updated `SpotifyClient.SaveAlbumFavorites` method to make the `ids` argument optional; if not supplied, the currently playing track album id value is used instead.
  * Updated `SpotifyClient.RemoveAlbumFavorites` method to make the `ids` argument optional; if not supplied, the currently playing track album id value is used instead.
  * Updated `SpotifyClient.CreatePlaylist` method to add the `imagePath` argument, which assigns an image to the created playlist.
  * Updated `SpotifyClient.ChangePlaylistDetails` method to add the `imagePath` argument, which assigns an image to the updated playlist details.

###### [ 1.0.36 ] - 2024/03/19

  * Fixed `SpotifyClient.SaveTrackFavorites` method for a bug introduced with v1.0.35 update causeing 'object of type 'bool' has no len()' exceptions.
  * Fixed `SpotifyClient.RemoveTrackFavorites` method for a bug introduced with v1.0.35 update causeing 'object of type 'bool' has no len()' exceptions.
  * Fixed `SpotifyClient.AddPlaylistItems` method for a bug introduced with v1.0.35 update causeing 'object of type 'bool' has no len()' exceptions.
  * Fixed `SpotifyClient.RemovePlaylistItems` method for a bug introduced with v1.0.35 update causeing 'object of type 'bool' has no len()' exceptions.

###### [ 1.0.35 ] - 2024/03/18

  * Updated `SpotifyClient.SaveTrackFavorites` method to make the `ids` argument optional; if not supplied, the currently playing id value is used instead.
  * Updated `SpotifyClient.RemoveTrackFavorites` method to make the `ids` argument optional; if not supplied, the currently playing id value is used instead.
  * Updated `SpotifyClient.AddPlaylistItems` method to make the `uris` argument optional; if not supplied, the currently playing uri value is used instead.
  * Updated `SpotifyClient.RemovePlaylistItems` method to make the `uris` argument optional; if not supplied, the currently playing uri value is used instead.

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