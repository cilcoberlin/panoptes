
from django.utils.translation import ugettext_lazy as _

from panoptes.analysis.axes.x import XAxis
from panoptes.core.models import Workstation

class Axis(XAxis):
	"""An x-axis of Workstation instances."""

	name = _("workstation")
	slug = "workstations"

	def generate_values(self, sessions, filters):
		"""Return a list of Workstation instances for the location, ordered by name."""
		return list(Workstation.objects.all_for_location(filters.location))

	def render_value(self, value):
		"""Render the Workstation instance `value` as the workstation name."""
		return value.name

	def verbose_value(self, value):
		"""Render the workstation name with a preposition."""
		return _("for %(workstation)s") % {'workstation': self.render_value(value)}

	def provide_related_fields(self):
		"""Follow the workstation field out on any queries."""
		return ['workstation']

	def serialize_value(self, value):
		"""Serialize the workstation as its stringified primary key."""
		return unicode(value.pk)

	def deserialize_value(self, value):
		"""Deserialize the stringified workstation PK as a Workstation instance."""
		return Workstation.objects.get(pk=int(value))
