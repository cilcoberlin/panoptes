
from django.utils.translation import ugettext_lazy as _

from panoptes.analysis.axes.y import YAxis

import copy

class Axis(YAxis):
	"""A y-axis of the average session length."""

	name = _("average session length")
	slug = "avg-session-length"

	def _average_length_for_queryset(self, sessions, field_name, x_values):
		"""
		Return the average length for the given sessions, grouped by field.

		Arguments:
		sessions -- a Session queryset
		field_name -- the string name of the field to group by
		x_values -- a list of x-values for which to generate data

		Returns: a list of integers as long as x_values

		"""

		by_field = dict(zip(x_values, [0] * len(x_values)))
		counts = copy.copy(by_field)
		for session in sessions.iterator():
			field_key = getattr(session, field_name)
			by_field[field_key] += (session.end - session.start).seconds
			counts[field_key] += 1

		y_values = []
		for x_value in x_values:
			try:
				y_value = by_field[x_value] / counts[x_value]
			except (ZeroDivisionError, KeyError):
				y_value = 0
			y_values.append(y_value)
		return y_values

	def day_values(self, x_values, sessions, filters):
		"""
		Return a list of the average session length of each date instance in the
		`x_values` list.
		"""
		return self._average_length_for_queryset(sessions, 'start_date', x_values)

	def workstation_values(self, x_values, sessions, filters):
		"""
		Return a list of the average session length for each Workstation
		instance in the `x_values` list.
		"""
		return self._average_length_for_queryset(sessions, 'workstation', x_values)

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

