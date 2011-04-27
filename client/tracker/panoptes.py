#!/usr/bin/env python

import datetime
import httplib
import optparse
import platform
import re
import signal
import socket
import subprocess
import sys
import time
import urllib
import urlparse
import uuid

try:
	import pywintypes
	import servicemanager
	import win32api
	import win32com.client
	import win32service
	import win32serviceutil
	import _winreg as winreg
except ImportError:
	pass

_platform_name = sys.platform
IS_WINDOWS = _platform_name == "win32"
IS_MAC = _platform_name == "darwin"

class AppList(object):
	"""A list of applications used in a session."""
	
	#  The separator character between an application's info fields
	DATA_SEPARATOR = "#"
	
	#  The separator character between each application info chunk
	RECORD_SEPARATOR = ","
	
	_cfm_app_name_search = re.compile(r'\/LaunchCFMApp\s+.*\/([^\/]+)$')
	_exe_app_name_search = re.compile(r'(.*)\.exe$', re.I)
	_file_extension_search = re.compile(r'\.[a-zA-Z0-9]+$')
	_packaged_app_name_search = re.compile(r'\/([^\/]+)\.app\/')
	
	def __init__(self):
		self._apps = {}
		self._running_apps = []
		
		#  Configure platform-appropriate app name getters
		getters = []
		if IS_MAC:
			getters = [self._find_packaged_app, self._find_cfm_app]
		if IS_WINDOWS:
			getters = [self._find_exe_app]
		self._app_name_getters = getters
		
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
		
	def update_app(self, command, start_dt):
		"""Update the usage record for the possible given application.
		
		If the command appears to be a valid app as defined by this application list,
		its start time is updated in the internal list of used application.
		
		Arguments:
		command -- a string of an executable command
		start_dt -- a datetime instance of when the program started
		
		"""
		
		name = re.sub(self._file_extension_search, '', self._find_app_name(command))
		if name:
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
	
	def _find_app_name(self, command):
		"""Search the given command for a recognizable application name.
		
		Arguments:
		command -- a string of the executable command
		
		Returns: an app name string or an empty string, if no name was found
		
		"""
		name = None
		for getter in self._app_name_getters:
			name = getter(command)
			if name:
				break
		return name
	
	def _find_packaged_app(self, command):
		"""Search for an application name in a Mac .app package."""
			
		#  Used the last occurrence of a .app path as the app's name
		#app_search = self._packaged_app_name_search.search(command)
		app_search = re.findall(self._packaged_app_name_search, command)
		if app_search:
			return app_search[-1]
		return ""
				
	def _find_cfm_app(self, command):
		"""Search for an app name in a Mac CFM app launched by LaunchCFMApp."""
		
		#  Look for apps launched via a call to LaunchCFMApp, which will have the app
		#  name after the call to LaunchCFMApp
		cfm_search = self._cfm_app_name_search.search(command)
		if cfm_search:
			return cfm_search.group(1)
		return ""
	
	def _find_exe_app(self, command):
		"""Find an application name for a Windows .exe file."""
		exe_search = self._exe_app_name_search.search(command)
		if exe_search:
			return exe_search.group(1)
		return ""
							
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
	RUN_INTERVAL_SECONDS = 15
	
	#  Slugs for OS types used by Panoptes
	MAC_OS_SLUG = "mac"
	WINDOWS_OS_SLUG = "windows"
	
	def __init__(self, panoptes_url):
		
		self._apps = AppList()
		self._build_urls(panoptes_url)
		self._session_open = False
		self._closing_session = False

	def start(self):
		"""Report the start of a session to the server."""
		
		self.pre_start()
	
		self._mac_address = self.get_mac_address()
		self._username = self.get_current_user()
		
		connection = self._connect_to_server()
		params = {
			'mac':        self._mac_address,
			'os_type':    self.get_os_slug(),
			'os_version': self.get_os_version(),
			'user':       self._username
		}
		
		#  Notify the tracking API that we're starting a new session, aborting if we
		#  receive a 400 response code, indicating that the current machine should not
		#  or could not be tracked
		response = self._make_api_call(connection, self.START_SESSION_METHOD, params)
		if response:
			if response.status == self.API_ERROR_CODE:
				connection.close()
				self.stop(error="Session creation request refused with error code %d" % response.status)
			else:
				self._session_open = True
		
		#  Run the tracker in the background if we were able to start a session
		if self._session_open:
			self.run()
			
	def is_running(self):
		"""Return True if there is an open session."""
		return self._session_open
		
	def pre_start(self):
		"""Allow a child tracker to initialize itself before starting."""
		pass
		
	def run(self):
		"""Perform an actually on an interval."""
		raise NotImplementedError
	
	def stop(self, error=None):
		"""Quit tracking the session and report back on any apps used."""
		
		if self._closing_session:
			return
		self._closing_session = True
		
		#  Close an open session if one exists, reporting the end of our session and
		#  the list of applications used through the Panoptes REST API
		if self._session_open:
			connection = self._connect_to_server()
			params = {
				'apps': self._apps.format_for_post(),
				'mac': self._mac_address
			}
			response = self._make_api_call(connection, self.END_SESSION_METHOD, params)
			if response:
				if response.status == self.API_ERROR_CODE:
					connection.close()
					error="Session closing request refused with error code: %d" % response.status
				else:
					self._session_open = False
		
		#  Log an error if one occurred
		if error:
			self.log_error(error)
			
		self.post_stop(error)
		
	def post_stop(self, error):
		"""Allow a child tracker to perform actions after it it has stopped.
		
		Arguments:
		error -- the possible text of an error that occured, or None
		
		"""
		pass
		
	def get_os_slug(self):
		"""Return the slug of the OS to be used by Panoptes."""
		if IS_WINDOWS:
			return self.WINDOWS_OS_SLUG
		elif IS_MAC:
			return self.MAC_OS_SLUG
		else:
			return ""
		
	def get_mac_address(self):
		"""Return the current machine's MAC address formatted as AA:BB:CC:DD:EE:FF."""
		mac_hex = "%012X" % uuid.getnode()
		return ":".join([mac_hex[i:i+2] for i in xrange(0, len(mac_hex), 2)])
		
	def get_os_version(self):
		"""Return optional version information for the current OS."""
		raise NotImplementedError
			
	def get_current_user(self):
		"""Return the name of the currently logged in user."""
		raise NotImplementedError
	
	def get_processes(self, user=None):
		"""
		Return a dict of processes, with keys of the path to the executable (with
		args) and values of another dict with the following keys:
		
			start_dt -- a datetime instance of when the process was launched
		    owner -- the username of the owner
		
		"""
		raise NotImplementedError
				
	def update_app_usage(self):
		"""Update the internal app usage tracker."""
		
		apps = self.get_processes(self._username)
		self._apps.start_update()
		for command, info in apps.iteritems():
			self._apps.update_app(command, info['start_dt'])
		self._apps.end_update()
				
	def log_error(self, error):
		"""Log the error contained in the given string."""
		pass
		
	def _build_urls(self, url):
		"""
		Parse the provided Panoptes URL to get the base URL and the path to the
		session tracking API.
		"""
		parts = urlparse.urlparse(url)
		self._server_url = parts.netloc 
		self._api_path = re.sub(r'/{2,}', '/', urlparse.urljoin("%s/" % parts.path, self.API_URL))
		
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
		"""Make a call to the Panoptes tracking REST API.
		
		Arguments:
		connection -- an HTTPConnection instance
		method -- a string of the method used to transfer data
		params -- a dict of params to pass to the API
		
		Returns: an HTTPResponse object on success, otherwise None
		
		"""
		
		log_args = {
			'url': self._api_path,
			'server': self._server_url,
			'method': method,
			'args': params,		
		} 
		log_base = " to %(url)s on %(server)s via %(method)s with args of %(args)s failed for reason: %(error)s"
		
		try:
			connection.request(method, self._api_path, urllib.urlencode(params), self.CONNECTION_HEADERS)
		except socket.error, e:
			connection.close()
			log_args['error'] = e
			self.stop(error="API call" + log_base % log_args)
		else:
			try:
				response = connection.getresponse()
				response.read()
			except httplib.HTTPException, e:
				log_args['error'] = e
				self.stop(error="Reading the response from API call" + log_base % log_args)
				return None
			else:
				return response
	
class PanoptesMacTracker(PanoptesTracker):
	"""A tracker for Mac OS X.
	
	This tracker is intended to be run as a local launch agent, and as such is
	managed by launchd.  Once started when a user logs in, it runs in a loop until
	it receives SIGTERM signal, indicating that the user has logged out and launchd
	is requesting that this tracker terminates.
	"""
	
	_space_split = re.compile(r'\s+')
		
	def pre_start(self):
		"""Configure signal listeners to make this tracker work as launch agent."""
		
		#  Listen for a SIGTERM sent from launchd and exit upon its receipt
		signal.signal(signal.SIGTERM, self._catch_sigterm)
		
	def run(self):
		"""Run in a loop in the background."""
		
		#  Take periodic snapshots of the apps being used and update our internal
		#  count of used apps until told to terminate
		while True:
			try:
				self.update_app_usage()
				time.sleep(self.RUN_INTERVAL_SECONDS)
			except (KeyboardInterrupt, SystemExit):
				self.stop()
		
	def post_stop(self, error):
		"""Exit after stopping."""
		sys.exit(1 if error else 0)
		
	def log_error(self, error):
		"""Log errors to stdout."""
		print error
		
	def get_current_user(self):
		"""Return the name of the current user."""
		
		#  Since this is intended to run as an agent owned by root, use the name of
		#  the user that owns the UserEventAgent process as the logged-in user
		username = ""
		for process, info in self.get_processes().iteritems():
			if re.search(r'UserEventAgent', process):
				username = info['user']
		return username		
	
	def get_os_version(self):
		"""Return a string of the Mac OS version as 'major.minor'."""
		parts = platform.mac_ver()
		return ".".join(parts[0].split(".")[:2])
	
	def get_processes(self, user=None):
		"""Return a dict of processes and their info."""
		
		#  Optionally filter processes for the given username
		ps_args = ["ps", "-eo", "ruser,lstart,comm"]
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
	
	def _catch_sigterm(self, signum, frame):
		"""Stop tracking when receiving a SIGTERM."""
		self.stop()

class PanoptesWindowsTracker(PanoptesTracker):
	"""A tracker for Windows.
	
	This tracker is intended to be used by the Windows service, which manages the
	logic of it running in the background on an interval.
	"""
	
	_WMI_DATE_FORMAT = "%Y%m%d%H%M%S%f"
	_WMI_DATE_OFFSET = re.compile(r'[+-]\d+$')
	
	def __init__(self, current_user, wmi_client, panoptes_url):
		"""Create the Windows tracker.
		
		Arguments:
		current_user -- the name of the currently logged in user
		wmi_client -- an instance of a WMI client 
		panoptes_url -- the URL for the current Panoptes installation.
		
		"""
		
		super(PanoptesWindowsTracker, self).__init__(panoptes_url)
		self._wmi = wmi_client
		self._current_user = current_user
		
	def get_os_version(self):
		"""Return the major version of Windows installed."""
		parts = platform.win32_ver()
		return parts[0]
		
	def get_current_user(self):
		"""Return the stored user name."""
		return self._current_user
		
	def run(self):
		"""
		Update the app usage and don't run in a loop, as this will always be called by
		the wrapper Windows service.
		"""
		self.update_app_usage()
		
	def get_processes(self, user=None):
		"""Return a dict of processes and their info."""
		
		processes = {}
		now = datetime.datetime.now()
		
		#  Get a process list via WMI
		process_list = self._wmi.ExecQuery("Select Caption, CreationDate from Win32_Process")
		for process in process_list:
			try:
				start_dt = datetime.datetime.strptime(re.sub(self._WMI_DATE_OFFSET, '', process.CreationDate), self._WMI_DATE_FORMAT)
			except (TypeError, ValueError):
				start_dt = now
			try:
				owner_info = process.ExecMethod_("GetOwner")
			except pywintypes.com_error:
				continue
			else:  
				processes[process.Caption] = {
					'start_dt': start_dt,
					'user': owner_info.User
				}
		
		#  Remove any entries not belonging to the given username if filtering
		if user:
			prune_apps = []
			for app, info in processes.iteritems():
				if info['user'] != user:
					prune_apps.append(app)
			for app in prune_apps:
				del processes[app]
		
		return processes
		
	def log_error(self, error):
		"""Log the error to the management console."""
		servicemanager.LogErrorMsg(error)

#  Allow this to run on non-Windows platforms
try:
	ServiceFramework = win32serviceutil.ServiceFramework
except NameError:
	ServiceFramework = object
	
class PanoptesWindowsService(ServiceFramework):
	"""A Windows service that manages the Panoptes Windows tracker."""
	
	_svc_description_  = "Tracks usage for the Panoptes application"
	_svc_display_name_ = "Panoptes Usage Tracker"
	_svc_name_         = "panoptes_tracker"
	
	REGISTRY_KEY = r'Software\Panoptes'
	REGISTRY_URL_SUBKEY = "PanoptesURL"
	
	_USER_NAME_DOMAIN_SEARCH = re.compile(r'.*\\')
	
	def __init__(self, args): 
		"""Start the service and mark it as alive."""
		
		win32serviceutil.ServiceFramework.__init__(self, args)
		self._is_alive = True
		self._tracker = None
		self._current_user = None
		
		self._refresh_wmi_connection()
		self._panoptes_url = self._get_panoptes_url()
		
	def SvcDoRun(self):
		"""Run the Panoptes tracker in a loop."""
		
		#  Take periodic snapshots of the apps being used and update our internal
		#  count of used apps until told to terminate
		while self._is_alive:
			
			username = self._get_current_user()
			
			#  If a user is logging in, defined as a transition from no username to a
			#  valid username, create a new tracker
			if username and not self._current_user:
				self._maybe_stop_tracker()
				self._refresh_wmi_connection()
				self._tracker = PanoptesWindowsTracker(username, self._wmi, self._panoptes_url)
				self._tracker.start()
			
			#  If a user is logging out, defined as a transition from a valid username to
			#  no username, end the tracker's session
			if self._current_user and not username:
				self._maybe_stop_tracker()
			
			#  If a user is logged in, run the tracker
			if username and self._tracker:
				self._tracker.run()
			
			#  Run the service in a loop
			self._current_user = username
			win32api.SleepEx(PanoptesTracker.RUN_INTERVAL_SECONDS * 1000)
	
	def SvcStop(self):
		"""Tell the service to stop."""
		
		#  Try to end the session before stopping
		if self._tracker:
			self._tracker.stop()
		
		self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
		self._is_alive = False
	
	def _maybe_stop_tracker(self):
		"""Stop the tracker only if it exists and is running."""
		if self._tracker and self._tracker.is_running():
			self._tracker.stop()
	
	def _get_panoptes_url(self):
		"""Read the Panoptes URL from the registry and return it.
		
		If the registry key could not be found, shut down the service.
		"""
		
		url = None
		
		try:
			key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.REGISTRY_KEY, 0, winreg.KEY_READ)
		except WindowsError:
			pass
		else:
			try:
				subkey_data = winreg.QueryValueEx(key, self.REGISTRY_URL_SUBKEY)
			except WindowsError:
				pass
			else:
				try:
					url = str(subkey_data[0])
				except (IndexError, TypeError):
					pass
				
		if not url:
			servicemanager.LogErrorMsg("Unable to find the PanoptesURL registry key")
			self.SvcStop()
		return url
			
	def _get_current_user(self):
		"""
		Return the username of the current user or a blank string if no user is logged
		in, indicating that we're at the login prompt.
		"""
		items = self._wmi.ExecQuery("Select UserName from Win32_ComputerSystem")
		for item in items:
			base_name = getattr(item, 'UserName', "")
			if base_name:
				return re.sub(self._USER_NAME_DOMAIN_SEARCH, '', base_name)
		return ""
	
	def _refresh_wmi_connection(self):
		"""Get a connection to WMI for the current machine."""
		wmi_service = win32com.client.Dispatch("WbemScripting.SWbemLocator")
		self._wmi = wmi_service.ConnectServer(".", "root\cimv2")

if __name__ == "__main__":

	#  If on Mac, initialize a tracker that runs as a local launch agent, starting
	#  whenever a user logs in and exiting whenever they log out, and capable of
	#  receiving command line arguments
	if IS_MAC:
		
		parser = optparse.OptionParser()
		parser.add_option("-u", "--url", dest="url", default=None,
			help="the base URL of your Panoptes installation", metavar="URL")
		(options, args) = parser.parse_args()	
		panoptes_url = options.url
		if not panoptes_url:
			parser.error("You must specify a base URL for your Panoptes installation via the -u or --url arguments")
		
		tracker = PanoptesMacTracker(panoptes_url)
		tracker.start()	 
	
	#  If on Windows, initialize the tracker as a background service, filtering out
	#  the command-line URL argument if one is present when installing the service
	if IS_WINDOWS:
		
		#  If installing and specifying a URL for Panoptes, get the URL and remove it
		#  from the args to allow the python service to initialize properly
		try:
			url_arg = sys.argv[-2]
		except IndexError:
			url_arg = None
		if url_arg == "--url":
			try:
				panoptes_url = sys.argv[-2:][1]
			except IndexError:
				panoptes_url = None
			else:
				sys.argv = sys.argv[:-2]
			
			#  If we have a valid URL and are installing, update the registry key
			#  containing the Panpotes URL
			if panoptes_url and sys.argv[-1] == "install":
				try:
					key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, PanoptesWindowsService.REGISTRY_KEY, 0, winreg.KEY_WRITE)
				except WindowsError:
					key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, PanoptesWindowsService.REGISTRY_KEY)
				winreg.SetValueEx(key, PanoptesWindowsService.REGISTRY_URL_SUBKEY, 0, winreg.REG_SZ, panoptes_url)
				winreg.CloseKey(key)
		
		#  Configure and run the tracker service
		def ctrl_handler(ctrl_type):
			return True
		win32api.SetConsoleCtrlHandler(ctrl_handler, True)
		win32serviceutil.HandleCommandLine(PanoptesWindowsService)
		
