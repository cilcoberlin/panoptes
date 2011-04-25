#!/usr/bin/env bash

app_plist='com.panoptes.tracker.plist'
app_dir=/Library/Application\ Support/Panoptes
logs_dir=/Library/Logs/Panoptes
la_dir=/Library/LaunchAgents

#  Get the panoptes URL from the user
echo
echo "Enter the base URL for your Panoptes installation, followed by [ENTER]: "
read panoptes_url
echo

#  Copy over application files
echo "Copying files..."

[ ! -d "${app_dir}" ] && mkdir "${app_dir}"
cp -f panoptes.py "${app_dir}/"
chmod 755 "${app_dir}/panoptes.py"

[ ! -d "$logs_dir" ] && mkdir $logs_dir
touch $logs_dir/panoptes.log
touch $logs_dir/stdout.log
touch $logs_dir/stderr.log

echo "  All files have been copied"
echo 

#  Update the launch agent to pass Panoptes the URL provided to this installer
echo "Configuring launch agent..."
launchctl unload $app_plist > /dev/null 2>&1
cp -f $app_plist $la_dir
cd $la_dir
sed -i '' -e 's#{{URL}}#'"$panoptes_url"'#' $app_plist
echo "  Launch agent configured"
echo

#  Run Panoptes
echo "Loading Panoptes..."
launchctl load $app_plist > /dev/null 2>&1
echo "  Panoptes loaded"
echo
