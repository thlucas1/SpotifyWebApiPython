@echo off
echo Build PDoc Documentation Script starting.


echo Changing working directory to docspdoc folder.
cd C:\Users\thluc\source\repos\SpotifyWebApiPythonProject\docspdoc


echo Activating python virtual environment.
call "..\env\scripts\activate.bat"


echo Setting build environment variables manually ...
SET PYTHONWARNINGS=always


echo Setting build environment variables via buildEnv.py ...
FOR /F "delims=|" %%G IN ('"python.exe .\buildEnv.py"') DO SET "%%G"
echo.
echo Build Environment variables ...
echo - BUILDENV_PACKAGENAME = %BUILDENV_PACKAGENAME%
echo - BUILDENV_PACKAGEVERSION = %BUILDENV_PACKAGEVERSION%
echo - BUILDENV_PDOC_BRAND_ICON_URL = %BUILDENV_PDOC_BRAND_ICON_URL%
echo - BUILDENV_PDOC_BRAND_ICON_URL_SRC = %BUILDENV_PDOC_BRAND_ICON_URL_SRC%
echo - BUILDENV_PDOC_BRAND_ICON_URL_TITLE = %BUILDENV_PDOC_BRAND_ICON_URL_TITLE%


echo Cleaning up the PDoc Documentation output folder.
del /S /Q .\build\spotifywebapipython\*.*
del /S /Q .\build\*.*


echo Copying include files to PDoc output folder.
mkdir .\build\spotifywebapipython
copy .\include\*.js .\build
copy .\include\*.ico .\build


echo Changing working directory to package source folder.
cd C:\Users\thluc\source\repos\SpotifyWebApiPythonProject\spotifywebapipython


echo Building PDoc Documentation ...
rem can also add custom footer text with this option:  --footer-text "This is some footer text" 
echo.
pdoc -o ..\docspdoc\build -d google --no-show-source --no-math --no-mermaid --search -t ..\docspdoc\templates\darkmode __init__ models/album.py models/albumpagesaved.py models/albumpagesimplified.py models/albumsaved.py models/albumsimplified.py models/artist.py models/artistpage.py models/artistsimplified.py models/audiobook.py models/audiobookpagesimplified.py models/audiobooksimplified.py models/audiofeatures.py models/author.py models/category.py models/categorypage.py models/chapter.py models/chapterpagesimplified.py models/chaptersimplified.py models/context.py models/copyright.py models/device.py models/episode.py models/episodepagesaved.py models/episodepagesimplified.py models/episodesaved.py models/episodesimplified.py models/explicitcontent.py models/externalids.py models/externalurls.py models/followers.py models/imageobject.py models/imagevibrantcolors.py models/narrator.py models/owner.py models/pageobject.py models/playeractions.py models/playerplaystate.py models/playerqueueinfo.py models/playhistory.py models/playhistorypage.py models/playlist.py models/playlistpage.py models/playlistpagesimplified.py models/playlistsimplified.py models/playlisttrack.py models/playlisttracksummary.py models/recommendationseed.py models/restrictions.py models/resumepoint.py models/searchresponse.py models/searchresultbase.py models/show.py models/showpagesaved.py models/showpagesimplified.py models/showsaved.py models/showsimplified.py models/spotifyconnectdevice.py models/spotifyconnectdevices.py models/track.py models/trackpage.py models/trackpagesaved.py models/trackpagesimplified.py models/trackrecommendations.py models/tracksaved.py models/tracksimplified.py models/userprofile.py models/userprofilesimplified.py models/zeroconfdiscoveryresult.py models/zeroconfproperty.py oauthcli/authclient.py spotifyconnect/spotifyconnectdeviceeventargs.py, spotifyconnect/spotifyconnectdirectorytask.py, spotifyconnect/spotifyconnectzeroconfcastapptask.py, spotifyconnect/spotifyconnectzeroconfcastcontroller.py, spotifyconnect/spotifyconnectzeroconfcastlistener.py, spotifyconnect/spotifyconnectzeroconfexceptions.py, spotifyconnect/spotifyconnectzeroconflistener.py, zeroconfapi/spotifyzeroconfapierror.py zeroconfapi/zeroconfconnect.py zeroconfapi/zeroconfgetinfo.py zeroconfapi/zeroconfgetinfoalias.py zeroconfapi/zeroconfgetinfodrmmediaformat.py zeroconfapi/zeroconfresponse.py const.py saappmessages.py sautils.py spotifyapierror.py spotifyapimessage.py spotifyauthtoken.py spotifyclient.py spotifydiscovery.py spotifymediatypes.py spotifywebapiauthenticationerror.py spotifywebapierror.py spotifywebplayertoken.py


echo Deactivating python virtual environment.
call "..\env\scripts\deactivate.bat"


echo.
echo Changing working directory to package project folder.
cd C:\Users\thluc\source\repos\SpotifyWebApiPythonProject


echo Build PDoc Documentation Script completed.
