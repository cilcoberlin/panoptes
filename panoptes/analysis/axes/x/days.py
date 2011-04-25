
from django.template.defaultfilters import date as django_date
from django.utils.translation import ugettext_lazy as _

from panoptes.analysis.axes.x import XAxis

import datetime

class Axis(XAxis):
	"""An x-axis of days."""

	name = _("day")
	slug = "days"

	def generate_values(self, sessions, filters):
		"""
		Return an ordered list of the days defining the sessions, expressed as
		date instances.
		"""

		next_day = datetime.timedelta(days=1)
		current_date = filters.start_date
		end_date = filters.end_date
	
		#  Add each day between the start and end to a list, provided that it
		#  should not be excluded due to a weekday filter
		days = []
		while current_date <= end_date:
			tomorrow = current_date + next_day
			if filters.weekdays and current_date.isoweekday() not in filters.weekdays:
				current_date = tomorrow
				continue
			days.append(current_date)
			current_date = tomorrow

		return days

	def render_value(self, value):
		"""Render the datetime `value` as a localized date."""
		return django_date(value)
	
	def verbose_value(self, value):
		"""Render the datetime with a preposition."""
		return _("on %(date)s") % {'date': self.render_value(value)}
	
	def filter_sessions_for_detail(self, sessions, day):
		"""Restrict the sessions to only the day requested.
		
		Arguments:
		sessions -- a FilteredSessions instance of the full range of sessions
		day -- a date instance of the day whose details are being requested
		
		"""
		sessions.start_date = day
		sessions.end_date = day

	def serialize_value(self, value):
		"""Serialize the date instance as a stringified ordinal."""
		return unicode(value.toordinal())
	
	def deserialize_value(self, value):
		"""Deserialize the stringified ordinal as a date instance."""
		return datetime.date.fromordinal(int(value))
	