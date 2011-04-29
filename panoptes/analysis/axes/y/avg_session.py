
from django.utils.translation import ugettext_lazy as _

from panoptes.analysis.axes.y import YAxis

class Axis(YAxis):
	"""A y-axis of the average session length."""

	name = _("average session length")
	slug = "avg-session-length"

	def _average_length_for_queryset(self, sessions):
		"""Return the average session length for the given Session queryset."""
		try:
			return sum([(session.end - session.start).seconds for session in sessions if session.end]) / sessions.count()
		except ZeroDivisionError:
			return 0

	def day_values(self, x_values, sessions, filters):
		"""
		Return a list of the average session length of each date instance in the
		`x_values` list.
		"""
		return [self._average_length_for_queryset(sessions.filter(start_date=use_date))
			for use_date in x_values]

	def workstation_values(self, x_values, sessions, filters):
		"""
		Return a list of the average session length for each Workstation
		instance in the `x_values` list.
		"""
		return [self._average_length_for_queryset(sessions.filter(workstation=workstation))
			for workstation in x_values]

	def render_value(self, value):
		"""Render the average session length in seconds as an HH:MM string."""
		minutes = value / 60
		return u"%d:%02d" % (minutes / 60, minutes % 60)

	def serialize_value(self, value):
		"""Serialize the duration as a stringified number of seconds."""
		return unicode(value)

	def deserialize_value(self, value):
		"""Deserialize the stringified integer as an integer."""
		return int(value)

