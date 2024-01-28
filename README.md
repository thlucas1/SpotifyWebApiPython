<h1 class="modulename">
Spotify Web API Python3 Library
</h1>

## Overview
This API provides Python programmers the ability to retrieve information from the Spotify Web API from any program written in Python 3.

More information about the Spotify Web API can be found on the <a href="https://developer.spotify.com/documentation/web-api" target="_blank">Spotify Developer Portal page</a>.

*IMPORTANT*
This API assumes you will adhere to all of the terms set forth in the <a href="https://developer.spotify.com/terms" target="_blank">Spotify Developer Terms of Use</a>.  The developers of this API are not responsible for misuse of the underlying Spotify Web API.

## Features

This API supports all of the features of the Spotify Web API including access to all end points, and support for user authorization with scope(s).  Check out the [Spotify Web API documentation](https://developer.spotify.com/documentation/web-api) page for more details.

The following features are supported by this API.
- Authorization: Token generation (Authorization Code, Authorization Code PKCE, Client Credentials) with Scope(s), auto token storage and renewal.
- Albums: Get Album(s), Get Album Tracks, User Favorites (Get,Add,Remove,Check), Get New Releases.
- Artists: Get Artist(s), Get Artist's Albums, Get Artist's Top Tracks, Get Related Artists.
- Audiobooks: Get Audiobook(s), Get Audiobook Chapters, User Favorites (Get,Add,Remove,Check).
- Categories: Get Several Browse Categories, Get Single Browse Category.
- Chapters: Get a Chapter, Get Several Chapters.
- Episodes: Get Episode(s), User Favorites (Get,Add,Remove,Check).
- Genres: Get Available Genre Seeds.
- Markets: Get Available Markets.
- Player: Get Playback State, Transfer Playback, Get Available Devices, Get Currently Playing Track, Start/Resume/Pause/Skip/Seek/Repeat/Shuffle/Volume Playback, Get Recently Played Tracks, Get the User's Queue, Add Item to Playback Queue.
- Playlists: Get Playlist(s), Change Playlist Details, Get/Update/Add/Remove Playlist Items, Get Favorites, Get User's Playlists, Create Playlist, Get Featured Playlists, Get Category's Playlists, Get Playlist Cover Image, Add Custom Playlist Cover Image
- Search: Search for Albums/Artists/Audiobooks/Episodes/Playlists/Shows/Tracks.
- Shows: Get Show(s), Get Show Episodes, User Favorites (Get,Add,Remove,Check).
- Tracks: Get Track(s), User Favorites (Get,Add,Remove,Check), Get Track(s) Audio Features, Recommendations, Analysis.
- Users: Get Current/Another User's Profile, Get Top Items, Favorites (Follow,Unfollow,Check) Artists/Playlist/Users.
- ... and more

## Requirements and Dependencies
The following requirements must be met in order to utilize this API:

* You must have a Spotify account (free or premium).
* If designing an application for general use, you might consider creating a Spotify Application Client ID.  More information about creating an application can be found on the Spotify [Getting started with Web API](https://developer.spotify.com/documentation/web-api/tutorials/getting-started) page.

The following Python-related requirements must be met in order to utilize this API:

* Python 3.4 or greater (Python 2 not supported).
* oauthlib (==3.2.2) - for OAuth support.
* platformdirs (==4.1.0) - for platform dependent directory support.
* smartinspectPython (==3.0.30) - for diagnostics and logging support.
* requests (==2.31.0) - for web service request support.
* requests_oauthlib (==1.3.1) - for OAuth support.
* urllib3 (==2.1.0) - for web service request support.

## Documentation
Documentation is located in the package library under the 'docs' folder; use the index.html as your starting point. 
You can also view the latest docs on the <a href="https://spotifywebapipython.readthedocs.io/en/latest/__init__.html" target="_blank">readthedocs web-site</a>.

## Installation

This module can be easily installed via pip:
``` bash
$ python3 -m pip install spotifywebapipython
```

## Quick-Start Sample Code

Almost every method is documented with sample code; just click on the "Sample Code" links under the method, and use the "Copy to Clipboard" functionality to copy / paste.

Check out the following classes to get you started:
- `spotifywebapipython.spotifyclient.SpotifyClient` - main client class.

## Licensing
This project is licensed and distributed under the terms of the MIT End-User License Agreement (EULA) license.

## Logging / Tracing Support

The SmartInspectPython package (installed with this package) can be used to easily debug your applications that utilize this API.

The following topics and code samples will get you started on how to enable logging support.  
Note that logging support can be turned on and off without changing code or restarting the application.  
Click on the topics below to expand the section and reveal more information.  

<details>
  <summary>Configure Logging Support Settings File</summary>
  <br/>
  Add the following lines to a new file (e.g. "smartinspect.cfg") in your application startup / test directory.  
  Note the file name can be whatever you like, just specify it on the call to `SiAuto.Si.LoadConfiguration()` when initializing the logger.

``` ini
; smartinspect.cfg

; SmartInspect Logging Configuration General settings.
; - "Enabled" parameter to turn logging on (True) or off (False).
; - "Level" parameter to control the logging level (Debug|Verbose|Message|Warning|Error).
; - "AppName" parameter to control the application name.
Enabled = False 
Level = Verbose
DefaultLevel = Debug
AppName = My Application Name

; SmartInspect Logging Configuration Output settings.
; - Log to SmartInspect Console Viewer running on the specified network address.
Connections = tcp(host=192.168.1.1,port=4228,timeout=5000,reconnect=true,reconnect.interval=10s,async.enabled=true)
; - Log to a file, keeping 14 days worth of logs.
;Connections = "file(filename=\"./tests/logfiles/logfile.log\", rotate=daily, maxparts=14, append=true)"
; - Log to an encrypted file, keeping 14 days worth of logs.
;Connections = "file(filename=\"./tests/logfiles/logfileEncrypted.sil\", encrypt=true, key=""1234567890123456"", rotate=daily, maxparts=14, append=true)"
        
; set defaults for new sessions
; note that session defaults do not apply to the SiAuto.Main session, since
; this session was already added before a configuration file can be loaded. 
; session defaults only apply to newly added sessions and do not affect existing sessions.
SessionDefaults.Active = True
SessionDefaults.Level = Message
SessionDefaults.ColorBG = 0xFFFFFF

; configure some individual session properties.
; note that this does not add the session to the sessionmanager; it simply
; sets the property values IF the session name already exists.
Session.Main.Active = True
Session.Main.ColorBG = 0xFFFFFF
```

</details>

<details>
  <summary>Initialize Logging Support, MAIN module</summary>
  <br/>
  Add the following lines to your program startup module.  
  This will import the necessary package modules, and initialize logging support.  
  NOTE - This code should only be executed one time!  

``` python
# load SmartInspect settings from a configuration settings file.
from smartinspectpython.siauto import *
siConfigPath:str = "./tests/smartinspect.cfg"
SIAuto.Si.LoadConfiguration(siConfigPath)

# start monitoring the configuration file for changes, and reload it when it changes.
# this will check the file for changes every 60 seconds.
siConfig:SIConfigurationTimer = SIConfigurationTimer(SIAuto.Si, siConfigPath)

# get smartinspect logger reference.
_logsi:SISession = SIAuto.Main

# log system environment and application startup parameters.
_logsi.LogSeparator(SILevel.Fatal)
_logsi.LogAppDomain(SILevel.Verbose)
_logsi.LogSystem(SILevel.Verbose)
```

</details>

<details>
  <summary>Initialize Logging Support, CLASS or sub-modules</summary>
  <br/>
  Add the following lines to your program supporting modules.  
  This will import the necessary package modules, and initialize the shared logging session.  

``` python
# get smartinspect logger reference.
from smartinspectpython.siauto import *
_logsi:SISession = SIAuto.Main
```

</details>

<details>
  <summary>More Information on SmartInspect</summary>
  <br/>
  You can use SmartInspectPython by itself to create log files for your own applications.  
  Use the following PIP command to install the SmartInspectPython package from PyPi.org:  

  ``` bash
  $ python3 -m pip install smartinspectpython
  ```

  The SmarrtInspect Redistributable Console Viewer (free) is required to view SmartInspect Log (.sil) formatted log files, as well capture packets via the TcpProtocol or PipeProtocol connections.  The Redistributable Console Viewer can be downloaded from the <a href="https://code-partners.com/offerings/smartinspect/releases/" target="_blank">Code-Partners Software Downloads Page</a>. Note that the "Redistributable Console Viewer" is a free product, while the "SmartInspect Full Setup" is the Professional level viewer that adds a few more bells and whistles for a fee.  Also note that a Console Viewer is NOT required to view plain text (non .sil) formatted log files.
</details>

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1. Fork the Project
2. Create your Feature Branch  `git checkout -b feature/AmazingFeature`
3. Commit your Changes  `git commit -m 'Add some AmazingFeature'`
4. Push to the Branch  `git push origin feature/AmazingFeature`
5. Open a Pull Request
