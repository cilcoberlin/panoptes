
from django.utils.translation import ugettext_lazy as _

from panoptes.analysis.axes.x import XAxis
from panoptes.core.models import Application

class Axis(XAxis):
	"""An x-axis of Application instances."""

	name = _("application")
	slug = "apps"

	def generate_values(self, sessions, filters):
		"""Return a list of all available Application instances ordered by name."""
		return list(Application.objects.all().order_by('name'))
	
	def render_value(self, value):
		"""Render the Application instance `value` as the application's name."""
		return value.name
	
	def verbose_value(self, value):
		"""Render the application name with a preposition."""
		return _("for %(app)s") % {'app': self.render_value(value)}

	def serialize_value(self, value):
		"""Serialize the application as its stringified primary key."""
		return unicode(value.pk)
	
	def deserialize_value(self, value):
		"""Deserialize the stringified app PK as an Application instance."""
		return Application.objects.get(pk=int(value))