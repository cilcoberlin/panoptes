
from django.db.models.aggregates import Count
from django.utils.translation import ugettext_lazy as _, ungettext 

from panoptes.analysis.axes.y import YAxis

class Axis(YAxis):
	"""A y-axis of the number of sessions."""

	name = _("number of sessions")
	slug = "session-count"

	def _make_count_lookup(self, sessions, field_name):
		"""
		Return a dict whose keys are the valueified versions of the Session
		field specified in `field_name` and whose keys are the counts grouped by
		that field.
		"""
		counts = sessions.values(field_name).order_by().annotate(count=Count(field_name))
		return dict([(count[field_name], count['count']) for count in counts])

	def day_values(self, x_values, sessions, filters):
		"""
		Return a list of the number of sessions that occurred for each date
		instance in the `x_values` list.
		"""
		counts = self._make_count_lookup(sessions, 'start_date')
		return [counts.get(use_date, 0) for use_date in x_values]

	def hour_values(self, x_values, sessions, filters):
		"""
		Return a list of the number of sessions that occurred during the hour
		specified by each time instance in the `x_values` list.
		"""
		return [sessions.filter(start_time__gte=hour, end_time__lte=hour.replace((hour.hour + 1) % 24)).count()
			for hour in x_values]

	def workstation_values(self, x_values, sessions, filters):
		"""
		Return a list of the number of sessions that occurred for each
		Workstation instance in the `x_values` list.
		"""
		counts = self._make_count_lookup(sessions, 'workstation')
		return [counts.get(workstation.pk, 0) for workstation in x_values]

	def render_value(self, value):
		"""Render the integer number of sessions as a stringified integer."""
		return unicode(value)
	
	def verbose_value(self, value):
		"""Render the integer as the number of sessions."""
		return ungettext("%(count)d session", "%(count)d sessions", value) % {
			'count': value}
	
	def serialize_value(self, value):
		"""Serialize the number as a string."""
		return unicode(value)
	
	def deserialize_value(self, value):
		"""Deserialize the stringified integer as an integer."""
		return int(value)
