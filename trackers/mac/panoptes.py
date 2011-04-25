#!/usr/bin/env python

import datetime
import httplib
import logging
import optparse
import os
import platform
import re
import signal
import socket
import subprocess
import sys
import time
import urllib
from urlparse import urlparse
import uuid

class AppList(object):
	"""A list of applications used in a session."""
	
	#  The separator character between an application's info fields
	DATA_SEPARATOR = "#"
	
	#  The separator character between each application info chunk
	RECORD_SEPARATOR = ","
	
	def __init__(self):
		self._apps = {}
		self._running_apps = []
		
	def start_update(self):
		"""Signal that we are going to be updating processes."""
		self._running_apps = []
	
	def end_update(self):
		"""Signal that we are done updating processes.
		
		This is called to allow the app list to set an end time for any processes that
		were not updated during the last round, as, given that they no longer are in
		the list of running processes, they can be assumed to have exited.
		"""
		for app_name in self._apps:
			if not self._apps[app_name][-1][1]:
				if app_name not in self._running_apps:
					self._apps[app_name][-1][1] = datetime.datetime.now()
		
	def update_app(self, name, start_dt):
		"""Update the usage record for the app that was launced at `start_dt`."""
		
		if name not in self._apps:
			self._apps[name] = [[start_dt, None]]
		else:
			last_usage = self._apps[name][-1]
			if last_usage[1]:
				self._apps[name].append([start_dt, None])
			else:
				if start_dt < last_usage[0]:
					self._apps[name][-1] = [start_dt, None]
		self._running_apps.append(name)
					
	def format_for_post(self):
		"""Return the list of uses as a string formatted for the Panoptes API."""
		
		records = []
		now = datetime.datetime.now()
		for app, sessions in self._apps.iteritems():
			for session in sessions:
				start = session[0]
				end = session[1] or now
				records.append(self.DATA_SEPARATOR.join((app, start.isoformat(), end.isoformat())))
		return self.RECORD_SEPARATOR.join(records)
							
class PanoptesTracker(object):
	"""A usage tracker for Mac sessions."""
	
	#  The path to the Panoptes session tracking API
	API_URL = "api/versions/1/tracking/sessions/"
	
	#  The HTTP status code returned when an API request is unsuccessful
	API_ERROR_CODE = 400
	
	#  Headers to send to any connection to Panoptes
	CONNECTION_HEADERS = {
		"Accept": "text/plain",
		"Content-type": "application/x-www-form-urlencoded"
	}

	#  The HTTP methods used to transfer data when starting and ending sessions
	END_SESSION_METHOD = "PUT"
	START_SESSION_METHOD = "POST"
	
	#  How often to run the background process
	RUN_INTERVAL_SECONDS = 30
		
	#  The slug used to report Mac OS to Panoptes
	MAC_OS_SLUG = "mac"
	
	#  Logging information
	LOG_FILE = "/Library/Application Support/Logs/Panoptes/panoptes.log"
	LOG_FORMAT = "%(asctime)s %(message)s"
	
	_space_split = re.compile(r'\s+')
	_event_agent_process = re.compile(r'UserEventAgent', re.I)
	_app_name = re.compile(r'\/([^\/]+)\.app\/')
	
	def __init__(self, panoptes_url):
		
		self._apps = AppList()
		self._build_urls(panoptes_url)
		self._configure_logger()
		self._session_open = False

	def start(self):
		"""Report the start of a session to the server."""
		
		self._mac_address = self._get_mac_address()
		self._username = self._get_current_user()
		
		connection = self._connect_to_server()
		params = {
			'mac':        self._mac_address,
			'os_type':    self.MAC_OS_SLUG,
			'os_version': self._get_os_version(),
			'user':       self._username
		}
		
		#  Notify the tracking API that we're starting a new session, aborting if we
		#  receive a 400 response code, indicating that the current machine should not
		#  or could not be tracked
		response = self._make_api_call(connection, self.START_SESSION_METHOD, params)
		if response.status == self.API_ERROR_CODE:
			connection.close()
			self.stop(error="Session creation request refused with error code %d" % response.status)
		self._session_open = True
		
		#  Run the tracker in the background if we were able to start a session
		self.run()
		
	def run(self):
		"""Run in a loop in the background."""
		
		#  Take periodic snapshots of the apps being used and update our internal
		#  count of used apps until told to terminate
		while True:
			try:
				self._update_app_usage()
				time.sleep(self.RUN_INTERVAL_SECONDS)
			except (KeyboardInterrupt, SystemExit):
				self.stop()
	
	def stop(self, error=None):
		"""Quit tracking the session and report back on any apps used."""
		
		#  Close an open session if one exists, reporting the end of our session and
		#  the list of applications used through the Panoptes REST API
		if self._session_open:
			connection = self._connect_to_server()
			params = {
				'apps': self._apps.format_for_post(),
				'mac': self._mac_address
			}
			response = self._make_api_call(connection, self.END_SESSION_METHOD, params)
			if response.status == self.API_ERROR_CODE:
				connection.close()
				self.stop(error="Session closing request refused with error code: %d" % response.status)
			self._session_open = False
		
		#  Exit, possibly logging an error
		if error:
			self._logger.error(error)
		sys.exit(1 if error else 0)
		
	def _configure_logger(self):
		"""Configure the logger."""
		self._logger = logging.getLogger("panoptes.py")
		file_logger = logging.FileHandler(self.LOG_FILE)
		log_format = logging.Formatter(self.LOG_FORMAT)
		file_logger.setFormatter(log_format)
		self._logger.addHandler(file_logger)
		
	def _get_current_user(self):
		"""Return the name of the currently logged in user."""
		
		#  Since this is intended to run as a daemon owned by root, use the name of
		#  the user that owns the UserEventAgent process
		username = ""
		for process, info in self._get_processes().iteritems():
			if self._event_agent_process.search(process):
				username = info['user']
		return username

	def _connect_to_server(self):
		"""Return an HTTPConnection instance or error out."""
		
		#  Note that we set the session open flag to False, to prevent an infinite
		#  loop of trying to close a session when the server is not responding
		try:
			connection = httplib.HTTPConnection(self._server_url)
		except httplib.HTTPException, e:
			self._session_open = False
			self.stop(error="Connection to server %(server)s failed for reason: %(error)s" % {
				'server': self._server_url,
				'error': e})
		else:
			if not connection:
				self._session_open = False
				self.stop(error="Unable to connect to %s" % self._server_url)
			return connection
			
	def _make_api_call(self, connection, method, params):
		"""
		Make a call to the tracking REST API, returning an HTTPResponse instance or
		erroring out if the call fails.
		"""
		try:
			connection.request(method, self._api_path, urllib.urlencode(params), self.CONNECTION_HEADERS)
		except socket.error, e:
			connection.close()
			self.stop(error="API call to %(url)s on %(server)s via %(method)s and args of %(args)s failed for reason: %(error)s" % {
				'url': self._api_path,
				'server': self._server_url,
				'method': method,
				'args': params,
				'error': e})
		else:
			response = connection.getresponse()
			response.read()
			return response
	
	def _get_mac_address(self):
		"""Return the current machine's MAC address formatted as AA:BB:CC:DD:EE:FF."""
		mac_hex = "%012X" % uuid.getnode()
		return ":".join([mac_hex[i:i+2] for i in xrange(0, len(mac_hex), 2)])
	
	def _get_os_version(self):
		"""Return a string of the OS version as 'major.minor'."""
		parts = platform.mac_ver()
		return ".".join(parts[0].split(".")[:2])
	
	def _build_urls(self, url):
		"""
		Parse the provided Panoptes URL to get the base URL and the path to the
		session tracking API.
		"""
		parts = urlparse(url)
		self._server_url = parts.netloc 
		self._api_path = os.path.join(parts.path, self.API_URL)
		
	def _get_processes(self, user=None):
		"""
		Return a dict of processes, with keys of the path to the executable (with
		args) and values of another dict with the following keys:
		
			start -- a datetime instance of when the process was launched
		    owner -- the username of the owner
		
		"""
		
		#  Optionally filter processes for the given username
		ps_args = ["ps", "-eo", "ruser,lstart,command"]
		if user:
			ps_args.extend(["-u", user])
		
		#  Break each process from ps into a meaningful dict entry
		processes = {}
		ps = subprocess.Popen(ps_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		output, unused = ps.communicate()
		for line in output.splitlines()[1:]:
			parts = re.split(self._space_split, line)
			user = parts[0]
			start_dt = datetime.datetime.strptime(" ".join(parts[1:6]), "%c")
			command = " ".join(parts[6:])
			processes[command] = {
				'start_dt': start_dt,
				'user':     user,
			}
		return processes
	
	def _update_app_usage(self):
		"""Update the internal app usage tracker."""
		
		#  Extract any app bundle name from the process names and use that to update
		#  our internal repository of start times.  If an app has multiple instances,
		#  use the oldest instance's start time, as it is likely an app that creates
		#  multiple processes for internal tabs or windows.  
		apps = self._get_processes(self._username)
		self._apps.start_update()
		for command, info in apps.iteritems():
			app_search = self._app_name.search(command)
			if app_search:
				app_name = app_search.group(1)
				self._apps.update_app(app_name, info['start_dt'])
		self._apps.end_update()
	
if __name__ == "__main__":
		
	#  Get the URL for Panoptes from the command-line arguments
	parser = optparse.OptionParser()
	parser.add_option("-u", "--url", dest="url", default=None,
		help="the base URL of your Panoptes installation", metavar="URL")
	(options, args) = parser.parse_args()	
	panoptes_url = options.url
	if not panoptes_url:
		parser.error("You must specify a base URL for your Panoptes installation via the -u or --url arguments")

	#  Create a new tracker for the current user's session
	tracker = PanoptesTracker(panoptes_url)
	tracker.start()
	
	#  Stop the tracker when receiving a SIGTERM signal, which will be sent by
	#  launchd when the user is logging out
	def stop_tracker(signum, frame):
		if tracker:
			tracker.stop()
	signal.signal(signal.SIGTERM, stop_tracker)
