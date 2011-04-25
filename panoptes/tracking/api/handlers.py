
from panoptes.core.models import Session
from panoptes.core.utils.api import validate
from panoptes.tracking.forms import CreateSessionForm, EndSessionForm
from panoptes.tracking.models import AccountFilter

from piston.handler import BaseHandler
from piston.utils import rc

class SessionHandler(BaseHandler):
	"""Handler for searching for circulating items."""

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

		mac -    The MAC address of the machine. For the session to be
		         logged, a Workstation instance must exist with this MAC address
		         and have a True `track` attribute.

		apps -   A comma-separated string of applications used, with optional
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
