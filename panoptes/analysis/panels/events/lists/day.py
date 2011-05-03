
from django.conf import settings
from django.template.defaultfilters import date as django_date

from panoptes.analysis.panels.events.lists.base import BaseEvent, BaseEventList

from dateutil.parser import parser as dateutil_parser
from gdata.calendar.client import CalendarEventQuery

import datetime
from operator import attrgetter

class DayEvent(BaseEvent):
	"""An event that occurred on a single day."""

	def __init__(self, location, title, repeat_rule, start, end):
		"""Create the single-day event.

		Arguments:
		title -- a string containing the event's title
		repeat_rule -- a string containing a possible iCalendar repeat rule
		start -- a datetime of the event's start
		end -- a datetime of the event's end

		"""

		super(DayEvent, self).__init__(location, title, repeat_rule)
		self.start = start
		self.end = end

	def verbose_start(self):
		"""Show the event end as a datetime."""
		return django_date(self.start, settings.TIME_FORMAT)

	def verbose_end(self):
		"""Show the end as a datetime."""
		return django_date(self.end, settings.TIME_FORMAT)

class DayEventList(BaseEventList):
	"""An event list containing events that occurred on a given day."""

	slug = "day"

	event_class = DayEvent

	template = "panoptes/analysis/panels/event_lists/day.html"

	def __init__(self,  filters):
		"""Create an event list for events on the given day.

		Arguments:
		filters -- a FilteredSessions instance

		"""

		super(DayEventList, self).__init__(filters)
		self.day = filters.x_detail

		self._added_events = []

	def provide_render_args(self):
		"""Provide the day to the rendering context."""
		return {'day': self.day}

	def get_events(self, *args, **kwargs):
		"""Abort getting events if no day has been defined."""
		if not self.day:
			return
		super(DayEventList, self).get_events(*args, **kwargs)

	def sort_events(self, events):
		"""Sort the events by their start date.

		Arguments:
		events -- an unordered list of DayEvent instances

		"""
		return sorted(events, key=attrgetter('start'))

	def provide_feed_args(self):
		"""Return a query that restricts the events to a single day."""
		return {'query': CalendarEventQuery(
										start_min=self.rfc3339_localized(self.day),
										start_max=self.rfc3339_localized(self.day + datetime.timedelta(days=1)))}

	def handle_event(self, calendar, event):
		"""Add the event to the list.

		Arguments:
		calendar -- a LocationCalendar instance
		event -- a raw Google Calendar event

		"""

		event_id = event.id.text
		if event_id not in self._added_events:

			try:
				when = event.when[0]
			except IndexError:
				return
			else:
				parser = dateutil_parser()
				self.add_event(calendar, event.title.text, event.recurrence,
							parser.parse(when.start), parser.parse(when.end))
				self._added_events.append(event_id)
