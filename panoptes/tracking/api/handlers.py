
from panoptes.core.models import Location, Session
from panoptes.core.utils.api import validate
from panoptes.tracking.forms import CreateSessionForm, EndSessionForm
from panoptes.tracking.models import AccountFilter

from dateutil.parser import parser as dateutil_parser
from piston.handler import BaseHandler
from piston.utils import rc

class LocationInfoHandler(BaseHandler):
	"""Handler for locations."""

	allowed_methods = ('GET',)

	def read(self, request, location_slug=None):
		"""Return basic information about a location.

		This information is available in the JSON response via the following keys:

		    name               - The full display name of the location

			open_workstations  - The number of workstations currently available

			total_workstations - The total number of workstations at the location

		If the location slug provided does not map to a valid location, an HTTP
		400 bad request response is returned.

		:param location_slug: a slug identifying a location

		"""
		try:
			location = Location.objects.get(slug=location_slug)
		except Location.DoesNotExist:
			return rc.BAD_REQUEST
		return {
			'name': location.name,
			'open_workstations': location.open_workstation_count,
			'total_workstations': location.total_workstation_count
		}

class LocationActivityHandler(BaseHandler):
	"""Handler for location user information."""

	allowed_methods = ('GET',)

	def read(self, request, location_slug=None, start_dt=None, end_dt=None):
		"""Return information about the activity at a location.

		This activity is available to the caller by accessing the following keys
		of the generated JSON response:

		    total_users  - The total number of users that logged a session

		This method can be passed two optional parameters to specify datetimes
		after or before which sessions were logged, being the :param:start_dt
		and :param:end_dt arguments.  Each of these must be a datetime string
		formatted according to RFC 3339 (i.e., 1937-01-01T12:00:27.87+00:20).
		These parameters can be used to specify a date window during which all
		counted sessions must have occurred.

		If the location slug provided does not map to a valid location, or if
		either of the optional datetimes given is not properly formatted, an HTTP
		400 bad request response is returned.

		:param location_slug: a slug identifying a location
		:key start_dt: an RFC 3339 datetime after which any counted session must be logged
		:key end_dt: an RFC 3339 datetime before which any counted session must be logged

		"""

		# Build the required location and optional datetime filters
		try:
			location = Location.objects.get(slug=location_slug)
		except Location.DoesNotExist:
			return rc.BAD_REQUEST
		else:
			filter_args = {'location': location}

		parser = dateutil_parser()
		if start_dt:
			try:
				filter_args['start_date'] = parser.parse(start_dt)
			except ValueError:
				return rc.BAD_REQUEST
		if end_dt:
			try:
				filter_args['end_date'] = parser.parse(end_dt)
			except ValueError:
				return rc.BAD_REQUEST

		# Return counts for the given sessions
		sessions = Session.objects.filter_sessions(**filter_args)
		return {
			'total_users': sessions.count(),
		}

class SessionHandler(BaseHandler):
	"""Handler for sessions."""

	allowed_methods = ('POST','PUT')

	@validate(CreateSessionForm, 'POST')
	def create(self, request):
		"""
		Create a new session using the given POST data, whose possible keys and
		their function are explained below.

		mac        - The MAC address of the machine. For the session to be
		             logged, a Workstation instance must exist with this MAC
		             address and have a True `track` attribute.

		os_type    - A string describing the base OS type used for the session.

		os_version - An optional string describing the OS version.

		user       - The optional name of the local workstation account
		             reporting usage, or an arbitrary value. This value is used
		             to control whether or not the session is tracked.
		"""
		data = request.form.cleaned_data
		if AccountFilter.objects.is_user_loggable(data['user'], data['workstation']):
			session = Session.objects.start_session(data['workstation'], data['os'])
			return rc.CREATED if session else rc.BAD_REQUEST
		else:
			return rc.BAD_REQUEST

	@validate(EndSessionForm, 'PUT')
	def update(self, request):
		"""
		End an existing session using the given raw POST data, whose keys and
		their function are explained below.

		mac    - The MAC address of the machine. For the session to be
		         logged, a Workstation instance must exist with this MAC address
		         and have a True `track` attribute.

		apps   - A comma-separated string of applications used, with optional
		         start and end dates of usage reported as ISO 8601 timestamps,
		         all separated with a "#" character. If no time data is
		         available, a 0 should be provided instead. Each grouping of
		         data is thus expressed as
		         "appname#2010-01-01T10:15:36#2010-01-01T11:15:48". Only
		         applications who have a ReportedApplication instance matching
		         the application's reported name will be tracked.

		offset - A positive or negative integer representing the number of
		         seconds that should be added to the session's reported end time.
		"""
		data = request.form.cleaned_data
		session = Session.objects.end_session(data['workstation'], data['apps'], data['offset'])
		return rc.ALL_OK if session else rc.BAD_REQUEST
