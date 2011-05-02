@echo off

set INSTALL_PATH_QUOTELESS=C:\Program Files\Panoptes\
set INSTALL_PATH="%INSTALL_PATH_QUOTELESS%"
set TRACKER_NAME=panoptes.py

rem Get the Panoptes URL from the user or a command-line argument
if "%1"=="" goto from_user
set panoptes_url=%1
goto end_url
:from_user
set /P panoptes_url="Please enter the full URL to your Panoptes installation: "
:end_url

rem Create the Panoptes file structure
if exist %INSTALL_PATH% rmdir /S /Q %INSTALL_PATH%
mkdir %INSTALL_PATH%
copy tracker\%TRACKER_NAME% %INSTALL_PATH%
echo All files have been copied!

rem Install the tracker service with the user-provided URL
set tracker=python "%INSTALL_PATH_QUOTELESS%%TRACKER_NAME%"
%tracker% --wait 60 stop
%tracker% remove
%tracker% --startup auto install --url %panoptes_url%
%tracker% --wait 60 start
echo The Panoptes tracker was successfully configured and loaded!
