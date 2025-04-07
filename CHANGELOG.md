## Change Log

All notable changes to this project are listed here.  

Change are listed in reverse chronological order (newest to oldest).  

<span class="changelog">

###### [ 1.0.197 ] - 2025/04/06

  * Removed version 1.0.196, as the `vibrant-python` namespace has a dependency that was not compatible with current version of Home Assistant: "pillow>=10.1.0,<11.0.0".
  * Added namespace `vibrant` to library to support vibrant color extraction.

###### [ 1.0.196 ] - 2025/04/06

  * Added `ImageVibrantColors` model that contains vibrant colors extracted from a processed image.
  * Added `SpotifyClient.GetImageVibrantColors` method that extracts vibrant color palette RGB values from the specified image url.

###### [ 1.0.195 ] - 2025/04/03

  * Changed transfer playback behavior to resume playback of the last playing track instead of defaulting to playing of track favorites if no active device was found and Spotify Web Player cookie credentials are in use.  Note that track favorites will be used if no active device was found and Spotify Web Player cookie credentials are NOT in use.

###### [ 1.0.194 ] - 2025/03/29

  * Added support for re-awakening Amazon devices from sleep mode.

###### [ 1.0.193 ] - 2025/03/27

  * Updated underlying `smartinspectpython` package requirement to version 3.0.37.

###### [ 1.0.192 ] - 2025/03/26

  * Updated underlying `smartinspectpython` package requirement to version 3.0.36.

###### [ 1.0.191 ] - 2025/03/19

  * Added Time-based One Time Password processing. 
  * Added `pyotp` package requirement version >=2.9.0.

###### [ 1.0.190 ] - 2025/03/14

  * Fixed a bug that was causing `'ZeroconfGetInfoAlias' object has no attribute 'lower'` exceptions when Aliases were returned in Spotify Connect `GetInfo` requests. 

###### [ 1.0.189 ] - 2025/03/13

  * Fixed a bug that was causing the device name to be blank when Aliases were returned in Spotify Connect `GetInfo` requests. The first alias name will be used as the device name when aliases are returned for a device.
  * Defaulted Chromecast Zeroconf GetInformation BrandDisplayName value to "ChromeCast" if a manufacturer name was not supplied.

###### [ 1.0.188 ] - 2025/03/09

  * Added more device `cast_type` values to check for supported Chromecast devices: `null`; if `cast_type` is null, then assume it supports audio.  It appears that some manufacturers are not correctly setting this attribute (e.g. LG SN Series ThinQ Soundbar, JBL Authentics 200, etc).

###### [ 1.0.187 ] - 2025/03/08

  * Cleaned up some error / trace messages related to Spotify Web Player credentials processing.

###### [ 1.0.186 ] - 2025/03/08

  * Fixed a bug in Spotify Web Player credentials processing.

###### [ 1.0.185 ] - 2025/03/08

  * Fixed a bug in device name processing to properly display the Spotify Connect RemoteName value.  Prior code was causing the Zeroconf DeviceName to be displayed, which is sometimes not a user-friendly name.
  * Added Spotify Web Player credentials to `SpotifyClient` class constructor.  If the `spotifyWebPlayerCookieSpdc` and `spotifyWebPlayerCookieSpkey` argument values are specified, then an "elevated" access token (created from the argument values) will be used for all player-control related methods.

###### [ 1.0.184 ] - 2025/03/02

  * Updated underlying `smartinspectpython` package requirement to version 3.0.35.

###### [ 1.0.183 ] - 2025/03/02

  * Updated PDoc Documentation package name to lower-case, to match the PyPi.org package name.  This was to adhere to PyPI.org requirements for uploaded binary distribution filenames to comply with the binary distribution format.

###### [ 1.0.182 ] - 2025/03/02

  * Updated `setup.py` to adhere to PyPI.org requirements for uploaded binary distribution filenames to comply with the binary distribution format.  This changes the wheel filename that is generated from `spotifywebapiPython-1.0.182-py3-none-any.whl` to `spotifywebapipython-1.0.182-py3-none-any.whl` (same filename, just lower-case project name).

###### [ 1.0.181 ] - 2025/03/01

  * Updated logic to start / restart the Spotify Connect Directory task only if the authorization token setup was successful.  Prior logic was causing a misleading exception to be returned to the caller, and the original offending exception was only visible in the SmartInspect trace.

###### [ 1.0.180 ] - 2025/02/25

  * Updated Spotify Web API request logic to retry request failures with status code 504 (Gateway Timeout); request will be tried 5 times with a slight delay in between before giving up.
  * Updated Spotify Web Player token refresh request logic to retry request failures with status code 504 (Gateway Timeout); request will be tried 5 times with a slight delay in between before giving up.

###### [ 1.0.179 ] - 2025/02/25

  * Updated `SpotifyClient.GetDevicePlaybackState` method to get the current Spotify playback state, with device fallback if nothing is reported from Spotify.
  * Updated `SpotifyClient.PlayerTransferPlayback` method to ignore exceptions if trying to pause play on the device being transferred from.

###### [ 1.0.178 ] - 2025/02/24

  * Updated `mediaPositionHMS_toSeconds` method to account for a null position value.

###### [ 1.0.177 ] - 2025/02/24

  * Added retry logic to token exchange method for handling Spotify Web Player token refresh "504 - Gateway Timeout" errors.
  * Added exception handling logic to process TokenError exceptions more gradefully and without adding extra system log errors messages.

###### [ 1.0.176 ] - 2025/02/24

  * Added Spotify Player transport control for Spotify FREE accounts.  Note that the [Spotify Web Player Authentication Setup](https://github.com/thlucas1/homeassistantcomponent_spotifyplus/wiki/Device-Configuration-Options#spotify-web-player-authentication-setup) must be configured to use this functionality; if not configured, then the Spotify Web API will return a `Premium required` exception for all transport control methods.

###### [ 1.0.175 ] - 2025/02/23

  * Updated `SpotifyClient` methods to utilize the Spotify Web Player elevated access token (if configured) if a Spotify Player method is accessed.  This should prevent issues with Sonos devices.  Note that the [Spotify Web Player Authentication Setup](https://github.com/thlucas1/homeassistantcomponent_spotifyplus/wiki/Device-Configuration-Options#spotify-web-player-authentication-setup) must be configured to use this functionality; if not configured, then the Sonos Controller (e.g. SoCo) API is used to control the Sonos device.  The following methods were updated: `PlayerMediaPause`, `PlayerMediaResume`, `PlayerMediaSeek`, `PlayerMediaSkipNext`, `PlayerMediaSkipPrevious`, `PlayerSetRepeatMode`, `PlayerSetShuffleMode`, `PlayerSetVolume`, `PlayerTransferPlayback`, `AddPlayerQueueItems`.

###### [ 1.0.174 ] - 2025/02/22

  * Updated `SpotifyClient` methods to restore functions that were previously deprecated by the Spotify development team.  Note that the [Spotify Web Player Authentication Setup](https://github.com/thlucas1/homeassistantcomponent_spotifyplus/wiki/Device-Configuration-Options#spotify-web-player-authentication-setup) must be enabled to use these specific functions; if not enabled, the functions will still work but won't return Spotify owned items and data.  The following methods have functionality restored: `GetPlaylistItems`.

###### [ 1.0.173 ] - 2025/02/22

  * Updated `SpotifyClient` methods to restore functions that were previously deprecated by the Spotify development team.  Note that the [Spotify Web Player Authentication Setup](https://github.com/thlucas1/homeassistantcomponent_spotifyplus/wiki/Device-Configuration-Options#spotify-web-player-authentication-setup) must be enabled to use these specific functions; if not enabled, the functions will still work but won't return Spotify owned items and data.  The following methods have functionality restored: `GetPlaylist`,  `GetPlaylistFavorites`.

###### [ 1.0.172 ] - 2025/02/22

  * Updated `SpotifyClient` methods to restore functions that were previously deprecated by the Spotify development team.  Note that the [Spotify Web Player Authentication Setup](https://github.com/thlucas1/homeassistantcomponent_spotifyplus/wiki/Device-Configuration-Options#spotify-web-player-authentication-setup) must be enabled to use these specific functions; if not enabled, the functions will raise a `deprecated` exception.  The following methods were restored: `GetArtistRelatedArtists`, `GetTrackRecommendations`, `GetTracksAudioFeatures`, `GetFeaturedPlaylists`, `GetCategoryPlaylists`, `GetGenres`.

###### [ 1.0.171 ] - 2025/02/21

  * Updated `SpotifyConnectDirectoryTask.GetSonosPlayer` method to trace the SoCo instance that is used to control Sonos devices.
  
###### [ 1.0.170 ] - 2025/02/20

  * Updated `SpotifyConnectDevices.GetDeviceByName` method to match on alias name, remote name, and zeroconf device name when resolving a device name value.
  * Updated `SpotifyConnectDirectoryTask.OnServiceInfoAddedUpdatedSpotifyConnect` method to use the ZeroConf DeviceName value for the user-friendly device name by default.  The getInfo RemoteName value will be used for the user-friendly device name for some manufacturers (Sonos, etc).
  
###### [ 1.0.169 ] - 2025/02/20

  * Updated `SpotifyConnectDirectoryTask.GetSonosPlayer` method to optionally return the Sonos Group Coordinator when retrieving the Sonos Controller instance for a device.  This should prevent any `"play" can only be called/used on the coordinator in a group` errors.
  
###### [ 1.0.168 ] - 2025/02/18

  * Cleaned up some old trace messages and code comments.
  
###### [ 1.0.167 ] - 2025/02/18

  * Updated `SpotifyConnectDirectoryTask.GetDevices` method to not lock the collection when making a copy of the collection.
  
###### [ 1.0.166 ] - 2025/02/18

  * Updated `AuthClient.RefreshToken` logic to prevent calling external token updaters from more than 1 thread at a time.
  
###### [ 1.0.165 ] - 2025/02/17

  * Updated `SpotifyClient.PlayerMediaPlayContext` and `PlayerMediaPlayTracks` to utilize Spotify Web Player authorization token when starting play for Sonos and restricted devices.  This will cause play to start under Spotify Connect control, rather than using the Sonos Local Queue.  Refer to the [Spotify Web Player Authentication Setup](https://github.com/thlucas1/homeassistantcomponent_spotifyplus/wiki/Device-Configuration-Options#spotify-web-player-authentication-setup) wiki page for more information on how to configure it.
  
###### [ 1.0.164 ] - 2025/02/05

  * Added `SpotifyClient.Dispose` method to properly dispose of resources and unwire events when the instance is destroyed.friendly.
  
###### [ 1.0.163 ] - 2025/01/30

  * Adjusted `no active device` error message to be more user-friendly.
  * Updated service method arguments to indicate DEPRECATED parameters (e.g. parameters no longer used).
  
###### [ 1.0.162 ] - 2025/01/28

  * Added device `cast_type` value to `ZeroconfDiscoveryResult.Properties` for easier detection of Chromecast device types.
  * Updated `SpotifyClient.PlayerMediaPlayContext` method to correct shuffled track behavior; Prior behavior did not honor the current shuffle setting of the player, and would always start with the first track.
  
###### [ 1.0.161 ] - 2025/01/26

  * Added more device `cast_type` values to check for supported Chromecast devices: `cast`, `group`.
  
###### [ 1.0.160 ] - 2025/01/26

  * Removed check for `(castInfo.cast_type != "audio")` to determine if the Chromecast device is allowed in the device list or not.  This was never released to PROD.
  
###### [ 1.0.159 ] - 2025/01/25

  * Replaced `threading.Lock` references with `threading.RLock` (reentrant) references.  This should avoid any potential deadlock situations for recursive calls to methods on the same thread.

###### [ 1.0.158 ] - 2025/01/23

  * Updated Chromecast logic to support more user-friendly error messages when configuration / initialization errors occur.

###### [ 1.0.157 ] - 2025/01/23

  * Updated Chromecast logic to support more user-friendly error messages when configuration / initialization errors occur.

###### [ 1.0.156 ] - 2025/01/23

  * Updated `SpotifyClient` methods that require a `deviceId` argument to check for a "Device Not Found" condition, and return a more user-friendly message than the "Device Not Found" message from the Spotify Web API.

###### [ 1.0.155 ] - 2025/01/22

  * Updated `SpotifyClient.AddPlayerQueueItems` to support adding items to the Sonos device local queue.
  * Added `additionalTypes='episode'` parameter to all `GetPlayerPlaybackState()` calls so that context and item information is returned in the player playstate data.

###### [ 1.0.154 ] - 2025/01/22

  * Updated function `SpotifyClient.PlayerMediaPlayTracks` to handle playing tracks on the Sonos local queue.  Sonos devices can only initiate play (of tracks or context) on their local queue, as they are considered restricted devices by the Spotify Web API.
  * Updated function `SpotifyClient.PlayerMediaPlayContext` to handle playing context on the Sonos local queue.  Sonos devices can only initiate play (of tracks or context) on their local queue, as they are considered restricted devices by the Spotify Web API.

###### [ 1.0.153 ] - 2025/01/22

  * Updated function `SpotifyClient.PlayerTransferPlayback` to return a `SpotifyConnectDevice` object for the device where playback was transferred to.

###### [ 1.0.152 ] - 2025/01/22

  * Added more support for Sonos Player functions via the SoCo Sonos API.

###### [ 1.0.151 ] - 2025/01/21

  * Added support for limited Sonos Player functions via the SoCo Sonos API.
  * Added `soco` package requirement, >= 0.30.6.

###### [ 1.0.150 ] - 2025/01/20

  * Updated `SpotifyConnectDirectoryTask` to reset Zeroconf response data after Chromecast device activation; new requests were still referring to the stale information.

###### [ 1.0.149 ] - 2025/01/20

  * Added support for Google Chromecast Spotify Connect devices.
  * Added namespace `spotifyconnect` that contains support for Spotify Connect device discovery.
  * Removed function `SpotifyClient.AddPlayerQueueItem` - use `AddPlayerQueueItems` instead.
  * Removed function `SpotifyClient.PlayerActivateDevices` - playback is auto-transferred to some devices when they are activated (Sonos, Chromecast, etc).  This method is no longer needed, as devices are automatically resolved / activated now.
  * Removed function `SpotifyClient.PlayerVerifyDeviceDefault` - devices are automatically resolved / verified now.
  * Removed function `SpotifyClient.VerifyPlayerActiveDeviceId` - devices are automatically resolved / verified now.
  * Added `PyChromecast` package requirement, >= 14.0.5.
  * Updated underlying `smartinspectPython` package requirement to version 3.0.34.
  * Updated Python from v3.9 to v3.11.
  * Updated minimum python version requirement from v3.5.1+ to v3.11.0+
  
###### [ 1.0.148 ] - 2025/01/13

  * Updated trace message to better reflect logic flow.

###### [ 1.0.147 ] - 2025/01/13

  * Added `SpotifyConnectDevices.UpdateActiveDevice` method to update the currently active device based on playerState.
  * Added `ZeroconfDiscoveryResult.Description` property that returns a basic description of the device, and how source info was obtained. This is a helper property, and not part of the Zeroconf ServiceInfo result.

###### [ 1.0.146 ] - 2025/01/12

  * Added `SpotifyConnectDevices.RemoveDevice` method to remove existing device entry(s) from the `Items` collection by device id value.

###### [ 1.0.145 ] - 2025/01/12

  * Added `SpotifyConnectDevices.GetActiveDevice` method to return a Spotify Connect device if one is currently marked as the active device; otherwise, null if there is no active device.
  * Updated `SpotifyConnectDevices.UpdatePlayerDevices` method to return the currently active Spotify Player device instance as determined by the Spotify Player PlayState if one was supplied; otherwise, null if not active device.

###### [ 1.0.144 ] - 2025/01/10

  * Added `SpotifyConnectDevices.UpdatePlayerDevices` method to add a list of dynamic player device entries to the `Items` collection, remove any existing dynamic devices from the collection that are not in the `playerDevices` list, and update the currently active device based on playerState.

###### [ 1.0.143 ] - 2025/01/10

  * Added `SpotifyConnectDevices.GetDeviceIndexByDiscoveryName` method to return the index of the `Items` collection entry that contains the specified device Zeroconf discovery results name value, or -1 if not found.

###### [ 1.0.142 ] - 2025/01/10

  * Added `ZeroconfDiscoveryResult.Equals` method to compare object argument values to determine equality.
  * Added `ZeroconfGetInfo.Equals` method to compare object argument values to determine equality.
  * Added `SpotifyConnectDevice.Equals` method to compare object argument values to determine equality.

###### [ 1.0.141 ] - 2025/01/09

  * Added `SpotifyConnectDevices.GetDeviceByDiscoveryKey` method to return the device of the `Items` collection entry that contains the specified device Zeroconf discovery results key value, or null if not found.

###### [ 1.0.140 ] - 2025/01/09

  * Added `SpotifyConnectDevices.GetDeviceIndexByDiscoveryKey` method to return the index of the `Items` collection entry that contains the specified device Zeroconf discovery results key value, or -1 if not found.

###### [ 1.0.139 ] - 2025/01/07

  * Updated `SpotifyDiscovery._OnServiceStateChange` method to correctly update the Zeroconf DiscoveryResults instance.  The serviceinfo `Key` value must be used to update the device entry (not its `Id` value).

###### [ 1.0.138 ] - 2025/01/06

  * Updated `SpotifyDiscovery._OnServiceStateChange` method to correctly update the Zeroconf DiscoveryResults instance.

###### [ 1.0.137 ] - 2025/01/06

  * Added `PlayerPlayState.IsEmpty` property setter.

###### [ 1.0.136 ] - 2025/01/05

  * Updated `SpotifyClient.PlayerTransferPlayback` method to check player state before trying to transfer playback.  If nothing is playing, then issue a call to `PlayTrackFavorites` instead.  This will avoid the `Restriction violated` error which results from a transfer playback to the player when nothing is currently playing.

###### [ 1.0.135 ] - 2025/01/05

  * Updated `SpotifyClient` class to include properties for `SpotifyConnectLoginId` and `SpotifyConnectUsername`.

###### [ 1.0.134 ] - 2025/01/04

  * Updated `SpotifyClient` methods `PlayerActivateDevices` and `GetSpotifyConnectDevice` to re-create the ZeroconfConnect connection instance if the device IP address or port changed after Zeroconf rediscovery on a Disconnect call sequence.

###### [ 1.0.133 ] - 2025/01/04

  * Modified `SpotifyDiscovery._OnServiceStateChange` method to process Zeroconf Update and Remove notifications.

###### [ 1.0.132 ] - 2025/01/02

  * Modified `ZeroconfConnect.GetInformation` method logic to automatically retry the connection (after 250ms, 2s max) to the Spotify Connect Zeroconf device service if a "connection refused" was returned while trying to get device information.  This was originally set to 10 seconds, which is far too long to wait for a device to become available.
  * Updated `SpotifyClient` methods `PlayerActivateDevices` and `GetSpotifyConnectDevice` to rediscover the Spotify Connect Zeroconf device after a Disconnect call is issued.  It has been found that some device manufacturers (e.g. Denon) stop and restart the Zeroconf server on the device after a `resetUsers` (e.g. disconnect) call is made, which changes the IP Port number that the device listens on for incoming connections.
  * Removed the deprecated function `SpotifyConnect.PlayerResolveDeviceId` (since 2024/08/15); use the `GetSpotifyConnectDevice` method instead.

###### [ 1.0.131 ] - 2025/01/01

  * Modified `ZeroconfConnect.GetInformation` method logic to automatically retry the connection (after 250ms, 10s max) to the Spotify Connect Zeroconf device service if a "connection refused" was returned while trying to get device information.  The previous logic used a simple delay prior to the call and did not retry the connection, which resulted in the "connection refused" exceptions while trying to awaken devices.  Some Spotify Connect devices take a little bit longer to start accepting connections again after a change.
  * Added `lxml` package requirement to `setup.py`.

###### [ 1.0.130 ] - 2024/12/27

  * Added `PlayerPlayState.IsEmpty` property; returns True if Spotify playstate returned an empty response; otherwise, false.  This is a helper property, and is not part of the Spotify Web API specification.

###### [ 1.0.129 ] - 2024/12/21

  * Added `SpotifyClient.GetCoverImageFile` that gets the contents of an image url and transfers the contents to the local file system.  This method should only be used to download images for playlists that contain public domain images.
  * Added `ImageObject.GetImageHighestResolutionWidth` that returns the highest resolution order image width from a list of `ImageObject` items.

###### [ 1.0.128 ] - 2024/12/20

  * Updated `PlayerActions` model to load the correct action values for `TogglingRepeatTrack` and `TogglingShuffle`.  These were switched, which was causing shuffle and repeat actions to be misinterpreted.

###### [ 1.0.127 ] - 2024/12/19

  * Updated `SpotifyClient.PlayerMediaPlayTrackFavorites` to default and validate limitTotal argument.  It has been found that approximately 750 items can be retrieved and played successfully (anything more generates request size errors).

###### [ 1.0.126 ] - 2024/12/18

  * Updated `SpotifyClient.PlayerMediaPlayTrackFavorites` to retrieve unsorted track favorites, so that the most recently added favorites are played instead of the first alphabetical favorites.

###### [ 1.0.125 ] - 2024/12/09

  * Added `PlaylistSimplified` property setters for the the following properties: `Description`, `Id`, `Name`, `Type`, `Uri`.

###### [ 1.0.124 ] - 2024/12/07

  * Updated various `SpotifyClient` methods to discard favorites that do not contain a valid URI value.  Sometimes the Spotify Web API returns favorite items with no information!  The following methods were updated: `GetAlbumFavorites`, `GetEpisodeFavorites`, `GetShowFavorites`, `GetTrackFavorites`.

###### [ 1.0.123 ] - 2024/12/06

  * Updated various methods to validate boolean arguments - if value was not passed (e.g. None), then set to documented value (True or False).
  * Fixed a bug in `SpotifyClient.PlayerTransferPlayback` method that was causing play not to resume if `Play=True` and `forceActivateDevice=True`.  If forceActivateDevice=True, then we need to resume play manually if play=True was specified; this is due to the device losing its current status since it was being forcefully activated (e.g. disconnected and reconnected).

###### [ 1.0.122 ] - 2024/12/02

  * Updated `SpotifyClient` methods to return an exception due to the functions being deprecated by the Spotify development team.  More information can be found on the [Spotify Developer Forum Blog post](https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api) that was conveyed on November 27, 2024.  The following methods will now raise a `SpotifyApiError` exception due to the Spotify development team changes: `GetArtistRelatedArtists`, `GetTrackRecommendations`, `GetTracksAudioFeatures`, `GetFeaturedPlaylists`, `GetCategoryPlaylists`, `GetGenres`.  The following properties were also marked as deprecated for the same reason: `TrackSimplified.PreviewUrl`.
  * Due to the above changes made by Spotify, any Algorithmic and Spotify-owned editorial playlists are no longer accessible or have more limited functionality.  This means that you can no longer obtain details via the `SpotifyClient.GetPlaylist` and `SpotifyClient.GetPlaylistItems` methods for Spotify-owned / generated content (e.g. "Made For You", etc).  A `404 - Not Found` error will be returned when trying to retrieve information for these playlist types.

###### [ 1.0.121 ] - 2024/11/20

  * Updated `AuthTokenGenerator.py` sample code to correctly reference the token cache file.

###### [ 1.0.120 ] - 2024/11/18

  * Updated `SpotifyClient.ReorderPlaylistItems` to validate required input parameters were supplied.
  * Updated `SpotifyClient.ReplacePlaylistItems` to check for no uris argument; this can occur if you want to clear the playlist.
  * Updated `SpotifyClient.GetPlaylistCoverImage` method to make the `playlistId` argument optional; if not supplied, the currently playing playlist id value is used instead.
  * Added `SpotifyClient.Version` property.

###### [ 1.0.119 ] - 2024/11/15

  * Updated `TrackRecommendations` model to return empty arrays (instead of None) if seeds or tracks items were not found.

###### [ 1.0.118 ] - 2024/11/07

  * Updated `SpotifyClient.GetArtistInfo` method to handle the `see more` suffix in the `BioHtml` property.
  * Updated `SpotifyClient.GetArtistInfo` method to correctly parse tour event dates.

###### [ 1.0.117 ] - 2024/11/07

  * Updated `SpotifyClient.GetArtistInfo` method to force all links in the `BioHtml` property to open in a new browser window / tab (e.g. added `target="_blank"`).

###### [ 1.0.116 ] - 2024/11/07

  * Updated `ArtistInfoTourEvent` model to include the concert link.
  * Fixed `SpotifyClient.GetArtistInfo` method to correctly parse Spotify artist info and tour events.

###### [ 1.0.115 ] - 2024/11/04

  * Updated `PlayerQueueInfo` model to include the `DateLastRefreshed` property, which contains the date and time items were was last refreshed in unix epoch format (e.g. 1669123919.331225).  A value of zero indicates the date was unknown.  Note that this attribute does not exist in the Spotify Web API; it was added here for convenience.
  * Updated `Category` model to include the `Type` property, which contains a simulated data type.  This is a helper property - no value with this name is returned from the Spotify Web API.
  * Updated `Category` model to add the `uri` and `type` values to data returned by the `ToDictionary` method.

###### [ 1.0.114 ] - 2024/11/03

  * Added `sortResult` argument to the following `SpotifyClient` methods: `GetArtistRelatedArtists`, `GetArtistTopTracks`.  If True (default), result items are sorted by name prior to returning to the caller; otherwise, results are left in the order that the Spotify Web API returned them.

###### [ 1.0.113 ] - 2024/10/30

  * Updated `PlayerQueueInfo` model to remove repeated items when retrieving player queue information.  For some reason, the Spotify Web API will return up to 10 duplicate items with the same information.  For example: if there is only 1 item in the queue, then 10 duplicate items are returned by the Spotify Web API; if there are 5 items in the queue, then 5 duplicate items are returned by the Spotify Web API.  We will check for this scenario, and only return non-duplicate items if so.
  * Updated `PageObject` model to include the `DateLastRefreshed` property, which contains the date and time items were was last refreshed in unix epoch format (e.g. 1669123919.331225).  A value of zero indicates the date was unknown.  Note that this attribute does not exist in the Spotify Web API; it was added here for convenience.
  * Added `SpotifyClient.AddPlayerQueueItems` method that will add one or more items to the end of the user's current playback queue. 
  * Marked `SpotifyClient.AddPlayerQueueItem` method as deprecated; use the new `AddPlayerQueueItems` method instead.

###### [ 1.0.112 ] - 2024/10/19

  * Updated `SpotifyClient.GetSpotifyConnectDevice` method to issue a slight delay after disconnecting the device.  This should prevent `Getinformation` exceptions for devices that require a little bit of extra time after a Disconnect (e.g. zeroconf `resetUsers`) request in order to be ready for a Connect (e.g. zeroconf `addUser`) request.

###### [ 1.0.111 ] - 2024/10/14

  * Updated `SpotifyClient.GetChapter` method to make the `chapterId` argument optional; if not supplied, the currently playing chapter id value is used instead.

###### [ 1.0.110 ] - 2024/10/10

  * Updated `ImageObject.GetImageHighestResolution` method to account for null width values.

###### [ 1.0.109 ] - 2024/10/10

  * Correctly Updated various methods that return an ImageUrl property to return the highest resolution image from the Images collection instead of the first image.  For some reason, the Spotify Web API sets the first Images collection image to the lowest resolution (e.g. 64x64); for all other Images, the highest resolution image is listed first (e.g. 640x640).

###### [ 1.0.108 ] - 2024/10/10

  * Updated various methods that return an ImageUrl property to return the highest resolution image from the Images collection instead of the first image.  For some reason, the Spotify Web API sets the first Images collection image to the lowest resolution (e.g. 64x64); for all other Images, the highest resolution image is listed first (e.g. 640x640).

###### [ 1.0.107 ] - 2024/10/09

  * Updated `SpotifyClient.RemoveShowFavorites` method to account for Spotify Web API changes to remove show favorites.
  * Updated `SpotifyClient.SaveShowFavorites` method to account for Spotify Web API changes to save show favorites.
  * Updated `SpotifyClient.CheckPlaylistFollowers` method to account for Spotify Web API changes to `userIds` argument, which is now deprecated.  A single item list containing current user's Spotify Username must now be used.

###### [ 1.0.106 ] - 2024/10/04

  * Fixed various python `SyntaxWarning: invalid escape sequence '\ '` warnings that were being generated when code was executed.  Something changed with Home Assistant recently that turned these "used to be ignored" warnings into actual warnings that wind up in the HA System Log!  This is due to invalid escaped characters in various string comments that are used for documentation purposes (e.g. """ this is a code comment """).

###### [ 1.0.105 ] - 2024/10/04

  * Updated Spotify Connect device processing to only require the userid and password parameters when authenticating to devices that require user and password values.  Some devices only require a loginid value (e.g. spotifyd, Spotify Connect AddOn, librespot, Sonos, etc).  The user should not have to specify userid and password values if they are not required!
  * Cleaned up some documentation, as well as some of the code examples.

###### [ 1.0.104 ] - 2024/10/03

  * Updated `SpotifyClient.PlayerMediaSeek` method to change the `progressMS` check to `<= 0` when invoking relative positioning.

###### [ 1.0.103 ] - 2024/10/03

  * Updated `SpotifyClient.PlayerMediaSeek` method to add relative positioning capability.  This allows you to seek ahead / behind by a specified `relativePositionMS` positioning amount.  The `positionMS` argument must be zero to enable this functionality.  Note that the relative position functionality is not defined by the Spotify Web API.  The functionality was added to this API to support "skip" seeking.

###### [ 1.0.102 ] - 2024/09/29

  * Updated `SpotifyClient.GetShowFavorites` method to only return podcast show items by default.  Prior to this fix, it was returning both audiobook and podcast shows.  The new `excludeAudiobooks` argument allows you to return both audiobook and podcast shows (default returned by Spotify Web API).

###### [ 1.0.101 ] - 2024/09/28

  * Updated `ZeroconfConnect.Connect` method to load authorization credentials for the Spotify Connect `addUser` blob from a `credentials.json` file for devices that utilize librespot / spotifyd.  Spotify no longer supports uername / password authentication via librespot (always returns "Bad Credentials" exceptions.  This allows the librespot `credentials.json` file to be copied to the spotifywebapiPython storage folder, and used for calls to the librespot `addUser` zeroconf endpoint.
  * Updated `SpotifyClient.GetSpotifyConnectDevice` and `PlayerActivateDevices` methods to bypass the call to Spotify Connect Zeroconf Disconnect for devices that utilize librespot / spotifyd.  librespot does not implement the Spotify Connect Zeroconf `resetUsers` endpoint, so the request always fails with a 404.

###### [ 1.0.100 ] - 2024/09/26

  * Updated `SpotifyClient.GetSpotifyConnectDevice` method to force a Spotify Connect Disconnect call to the device if `activateDevice` argument is `True`.  The `verifyUserContext` argument is deprecated as well.  This was necessary, as Spotify Connect device manufacturers do not use the Spotify Connect Zeroconf Information `ActiveUser` property consistently.
  * Added `PlayerTransferPlayback.forceActivateDevice` argument that allows you to force activate the Spotify Connect device as part of the transfer of playback.

###### [ 1.0.99 ] - 2024/09/24

  * Added `PlayerPlayState.ItemType` property that denotes the type of episode being played: `podcast` or `audiobook`.  This property is only loaded when the `SpotifyClient` `GetPlayerNowPlaying` or `GetPlayerPlaybackState` method is called with `additionalTypes='episode'`.

###### [ 1.0.98 ] - 2024/09/24

  * Added `SpotifyClient.IsAudiobookEpisode` method that returns true if the specified episode id is an audiobook chapter; otherwise, false.  This allows you to programatically determine the difference between a podcast / show episode, and an audiobook episode.

###### [ 1.0.97 ] - 2024/09/20

  * Updated `ZeroconfGetInfoAlias` to fix a bug related to Spotify Connect devices that define aliases (introduced with v1.0.93).  This was causing `TypeError: unsupported operand type(s) for &: 'str' and 'tuple'` exceptions if a device had aliases defined.

###### [ 1.0.96 ] - 2024/09/19

  * Added defensive code in various parsers to account for the Spotify Web API returning an invalid / incomplete object.  This was noticed with the `GetAlbumFavorites` method, but also applied to other models that inherited from PageObject.

###### [ 1.0.95 ] - 2024/09/12

  * Added `image_url` attribute value to all models that support a `ToDictionary()` method (some that were previously missed in 1.0.94 release).

###### [ 1.0.94 ] - 2024/09/12

  * Added `image_url` attribute value to all models that support a `ToDictionary()` method.
  * Miscellaneous documentation updates.

###### [ 1.0.93 ] - 2024/09/10

  * Updated `SpotifyClient.GetAlbumFavorites` method to correctly sort results based upon the `sortResult` argument setting; true to sort by name ascending, false to sort by AddedAt descending.
  * Updated `SpotifyClient.GetEpisodeFavorites` method to correctly sort results based upon the `sortResult` argument setting; true to sort by name ascending, false to sort by AddedAt descending.
  * Updated `SpotifyClient.GetShowFavorites` method to correctly sort results based upon the `sortResult` argument setting; true to sort by name ascending, false to sort by AddedAt descending.
  * Updated `SpotifyClient.GetTrackFavorites` method to correctly sort results based upon the `sortResult` argument setting; true to sort by name ascending, false to sort by AddedAt descending.

###### [ 1.0.92 ] - 2024/08/23

  * Updated `SpotifyClient.FollowPlaylist` method to make the `playlistId` argument optional; if not supplied, the currently playing playlist id value is used instead.
  * Updated `SpotifyClient.GetAlbum` method to make the `albumId` argument optional; if not supplied, the currently playing album id value is used instead.
  * Updated `SpotifyClient.GetAlbumTracks` method to make the `albumId` argument optional; if not supplied, the currently playing album id value is used instead.
  * Updated `SpotifyClient.GetArtist` method to make the `artistId` argument optional; if not supplied, the currently playing artist id value is used instead.
  * Updated `SpotifyClient.GetArtistAlbums` method to make the `artistId` argument optional; if not supplied, the currently playing artist id value is used instead.
  * Updated `SpotifyClient.GetArtistInfo` method to make the `artistId` argument optional; if not supplied, the currently playing artist id value is used instead.
  * Updated `SpotifyClient.GetArtistRelatedArtists` method to make the `artistId` argument optional; if not supplied, the currently playing artist id value is used instead.
  * Updated `SpotifyClient.GetArtistTopTracks` method to make the `artistId` argument optional; if not supplied, the currently playing artist id value is used instead.
  * Updated `SpotifyClient.GetAudiobook` method to make the `audiobookId` argument optional; if not supplied, the currently playing audiobook id value is used instead.
  * Updated `SpotifyClient.GetAudiobookChapters` method to make the `audiobookId` argument optional; if not supplied, the currently playing audiobook id value is used instead.
  * Updated `SpotifyClient.GetEpisode` method to make the `episodeId` argument optional; if not supplied, the currently playing episode id value is used instead.
  * Updated `SpotifyClient.GetPlaylist` method to make the `playlistId` argument optional; if not supplied, the currently playing playlist id value is used instead.
  * Updated `SpotifyClient.GetPlaylistItems` method to make the `playlistId` argument optional; if not supplied, the currently playing playlist id value is used instead.
  * Updated `SpotifyClient.GetShow` method to make the `showId` argument optional; if not supplied, the currently playing show id value is used instead.
  * Updated `SpotifyClient.GetShowEpisodes` method to make the `showId` argument optional; if not supplied, the currently playing show id value is used instead.
  * Updated `SpotifyClient.GetTrack` method to make the `trackId` argument optional; if not supplied, the currently playing track id value is used instead.
  * Updated `SpotifyClient.GetTracksAudioFeatures` method to make the `trackId` argument optional; if not supplied, the currently playing track id value is used instead.
  * Updated `SpotifyClient.UnfollowPlaylist` method to make the `playlistId` argument optional; if not supplied, the currently playing playlist id value is used instead.

###### [ 1.0.91 ] - 2024/08/22

  * Updated `CheckTrackFavorites`, `RemoveTrackFavorites`, and `SaveTrackFavorites` methods to ensure that nowplaying item was a track and not an episode item.

###### [ 1.0.90 ] - 2024/08/22

  * Updated various methods to not log handled exception data as unhandled exceptions.

###### [ 1.0.89 ] - 2024/08/22

  * Updated `SpotifyClient.CheckAlbumFavorites` method to make the `ids` argument optional; if not supplied, the currently playing album id value is used instead.
  * Updated `SpotifyClient.CheckArtistsFollowing` method to make the `ids` argument optional; if not supplied, the currently playing artist id value is used instead.
  * Updated `SpotifyClient.CheckAudiobookFavorites` method to make the `ids` argument optional; if not supplied, the currently playing audiobook id value is used instead.
  * Updated `SpotifyClient.CheckEpisodeFavorites` method to make the `ids` argument optional; if not supplied, the currently playing episode id value is used instead.
  * Updated `SpotifyClient.CheckShowFavorites` method to make the `ids` argument optional; if not supplied, the currently playing show id value is used instead.
  * Updated `SpotifyClient.CheckTrackFavorites` method to make the `ids` argument optional; if not supplied, the currently playing track id value is used instead.

###### [ 1.0.88 ] - 2024/08/20

  * Updated `SpotifyClient.DefaultDeviceId` property to setter to account for empty string values.

###### [ 1.0.87 ] - 2024/08/20

  * Added `SpotifyClient.DefaultDeviceId` property to get / set the default device id (or name) to use for player transport methods (e.g. play, pause, skip, etc) that do not specify a device id and there is no active Spotify player detected (e.g. "Office", "5d4931f9d0684b625d702eaa24137b2c1d99539c", etc).  This should avoid the `No Active Device` exceptions returned from the Spotify Web API when playback transport methods are called after long pauses of inactivity.

###### [ 1.0.86 ] - 2024/08/19

  * Updated `SpotifyClient`, `ZeroconfConnect`, and `AuthClient` class constructors to include the `tokenStorageFile` argument that specifies the filename and extension of the authorization Token Cache file.  This is used for Spotify Connect devices that utilize the `authorization_code` token type.

###### [ 1.0.85 ] - 2024/08/19

  * Updated `SpotifyClient.RemoveAudiobookFavorites` method to make the `ids` argument optional; if not supplied, the currently playing audiobook id value is used instead.
  * Updated `SpotifyClient.RemoveEpisodeFavorites` method to make the `ids` argument optional; if not supplied, the currently playing episode id value is used instead.
  * Updated `SpotifyClient.RemoveShowFavorites` method to make the `ids` argument optional; if not supplied, the currently playing show id value is used instead.
  * Updated `SpotifyClient.SaveAudiobookFavorites` method to make the `ids` argument optional; if not supplied, the currently playing audiobook id value is used instead.
  * Updated `SpotifyClient.SaveEpisodeFavorites` method to make the `ids` argument optional; if not supplied, the currently playing episode id value is used instead.
  * Updated `SpotifyClient.SaveShowFavorites` method to make the `ids` argument optional; if not supplied, the currently playing show id value is used instead.

###### [ 1.0.84 ] - 2024/08/18

  * Updated `SpotifyClient.PlayerTransferPlayback` method to default the `refreshDeviceList` argument to True so that the Spotify Connect device list is refreshed by default before transferring playback.
  * Updated `ZeroconfConnect` methods to use `connection:close` headers for requests to the Spotify Connect Zeroconf API endpoints.

###### [ 1.0.83 ] - 2024/08/15

  * Updated `SpotifyClient.GetSpotifyConnectDevice` method to check if a Spotify Desktop Client Application OAuth2 token exists when a PlayerTransfer targets a Sonos device.  If not found, then control will be transferred to the Sonos device using it's local queue; if found, then Spotify Connect will reconnect to the device and control will be transferred to the Sonos device using Spotify Connect.

###### [ 1.0.82 ] - 2024/08/15

  * Updated `SpotifyClient.GetSpotifyConnectDevice` method to get real-time information for some portions of the device info for devices detected by zeroconf discovery (non-dynamic), even when using the cache.  Prior to this fix, transfer of playback failed for dynamic devices (web player, mobile app player, etc).

###### [ 1.0.81 ] - 2024/08/15

  * Updated `SpotifyClient.GetSpotifyConnectDevice` method to get real-time information for some portions of the device info, even when using the cache.  Prior to this, stale information was being used that had been updated since the last cache update.

###### [ 1.0.80 ] - 2024/08/15

  * Added `SpotifyClient.GetSpotifyConnectDevice` method that will get information about a specific Spotify Connect player device, and (optionally) activate the device if it requires it.
  * Marked the `SpotifyClient.PlayerResolveDeviceId` method as deprecated, and it will be removed in a future release; use the `GetSpotifyConnectDevice` instead.
  * Removed `SpotifyClient.PlayerTransferPlayback` method argument `resolveDeviceId` as it is no longer used.
  * Added `SpotifyClient.PlayerTransferPlayback` method argument `refreshDeviceList` to refresh the Spotify Connect device list (True) or use the Spotify Connect device list cache (False) when resolving a Spotify Connect device value.

###### [ 1.0.79 ] - 2024/08/13

  * Updated `ZeroconfConnect._GetSpotifyConnectAuthorizationCodeToken` method to raise an exception if the Spotify Client Application authorization access token could not be found.  Prior logic was causing the process to wait for a user response to a token authorization request, which would never happen since the process was running on a server.

###### [ 1.0.78 ] - 2024/08/12

  * Updated `ZeroconfConnect` class constructor to include the `tokenStorageDir` argument that specified the directory path that will contain the `tokens.json` cache file.  This is used for Spotify Connect devices that utilize the `authorization_code` token type.

###### [ 1.0.77 ] - 2024/08/12

  * Updated `AuthClient.AuthorizeWithServer` method to specify a redirect uri with host, port, and path values.  Prior code was only allowing a redirect uri with host and port values.
  * Added `SpotifyClient.SetAuthTokenAuthorizationCode` method argument `redirectUriPath` to allow a redirect_uri path value to be specified for OAuth authorization requests.
  * Added `SpotifyClient.SetAuthTokenAuthorizationCodePKCE` method argument `redirectUriPath` to allow a redirect_uri path value to be specified for OAuth authorization requests.
  * Updated `ZeronconfConnect` class to correctly process Spotify Connect requests for token type `authorization_code` devices.
  * Updated `SpotifyClient.PlayerMediaPlayTrackFavorites` method to add the `limitTotal` argument that limits the number of tracks retrieved from favorites.
  * Added `sortResult` argument to the following `SpotifyClient` methods: `GetAlbumFavorites`, `GetAlbumNewReleases`, `GetArtistAlbums`, `GetArtistsFollowed`, `GetAudiobookFavorites`, `GetBrowseCategorys`, `GetCategoryPlaylists`, `GetEpisodeFavorites`, `GetFeaturedPlaylists`, `GetPlayerDevices`, `GetPlaylistFavorites`, `GetPlaylistsForUser`, `GetShowFavorites`, `GetSpotifyConnectDevices`, `GetTrackFavorites`, `GetUsersTopArtists`, `GetUsersTopTracks`.  If True (default), result items are sorted by name prior to returning to the caller; otherwise, results are left in the order that the Spotify Web API returned them.

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