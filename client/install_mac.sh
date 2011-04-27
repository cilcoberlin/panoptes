#!/usr/bin/env bash

APP_PLIST='com.panoptes.tracker.plist'
APP_DIR=/Library/Application\ Support/Panoptes
DATA_DIR=mac_data
LA_DIR=/Library/LaunchAgents
TRACKER_DIR=tracker

#  Get the panoptes URL from the user
echo
echo "Enter the base URL for your Panoptes installation, followed by [ENTER]: "
read panoptes_url
echo

#  Copy over application files
echo "Copying files..."
[ ! -d "${APP_DIR}" ] && mkdir "${APP_DIR}"
cp -f $TRACKER_DIR/panoptes.py "${APP_DIR}/"
echo "  All files have been copied"
echo 

#  Update the launch agent to pass Panoptes the URL provided to this installer
echo "Configuring launch agent..."
launchctl unload $APP_PLIST > /dev/null 2>&1
cp -f $DATA_DIR/$APP_PLIST $LA_DIR
cd $LA_DIR
chmod 644 $APP_PLIST
sed -i '' -e 's#{{URL}}#'"$panoptes_url"'#' $APP_PLIST
echo "  Launch agent configured"
echo

#  Run Panoptes
echo "Loading Panoptes..."
launchctl load $APP_PLIST > /dev/null 2>&1
echo "  Panoptes loaded"
echo
