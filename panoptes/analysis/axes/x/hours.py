
from django.template.defaultfilters import time as django_time
from django.utils.translation import ugettext_lazy as _

from panoptes.analysis.axes.x import XAxis

import datetime

class Axis(XAxis):
	"""An x-axis of hours."""

	name = _("hour")
	slug = "hours"

	def filter_sessions_for_detail(self, sessions, hour):
		"""Restrict the sessions to only the hour requested.

		Arguments:
		sessions -- a FilteredSessions instance of the full range of sessions
		hour -- a time instance for the hour whose details are being requested

		"""
		sessions.start_time = hour
		sessions.end_time = hour.replace(hour.hour + 1)

	def generate_values(self, sessions, filters):
		"""
		Return an ordered list of hours, represented as time instances, during
		which the given sessions occurred.
		"""

		#  Use the filter starting and ending times as our time bounds, as these will
		#  default to the location's open hours if the user doesn't specify any bounds
		start_hour = filters.start_time
		end_hour   = filters.end_time

		#  Return the evenly-spaced hours as the x-axis
		return [datetime.time(hour) for hour in xrange(start_hour.hour, end_hour.hour + 1)]

	def render_value(self, value):
		"""Render the time instance `value` as a localized time."""
		return django_time(value)

	def verbose_value(self, value):
		"""Render the time with a preposition."""
		return _("at %(time)s") % {'time': self.render_value(value)}

	def serialize_value(self, value):
		"""Serialize the time instance as its stringified hour."""
		return unicode(value.hour)

	def deserialize_value(self, value):
		"""Deserialize the stringified hour as a time instance."""
		return datetime.time(int(value))
