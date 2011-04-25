
from django.template.defaultfilters import time as django_time

from panoptes.analysis.panels.events.lists.base import BaseEvent, BaseEventList
from panoptes.analysis.panels.events.rrule import RepeatRule

import datetime 

class HourEvent(BaseEvent):
	"""A repeating event that occurs during a certain hour."""
		
	def verbose_start(self):
		"""Show the event end as a time."""
		return django_time(self.repeat_rule.start_time)
	
	def verbose_end(self):
		"""Show the event end as a time."""
		return django_time(self.repeat_rule.end_time)

class HourEventList(BaseEventList):
	"""An event list containing repeating events that occur during a given hour."""
	
	slug = "hour"
	
	event_class = HourEvent
	
	template = "panoptes/analysis/panels/event_lists/hour.html"
	
	def __init__(self, filters):
		"""Create an event list for events on the given hour.
		
		Arguments:
		filters -- a FilteredSessions instance
		
		"""
		
		super(HourEventList, self).__init__(filters)
		self.hour = filters.x_detail
		
		self._added_events = []
		
	def provide_render_args(self):
		"""Provide the hour to the rendering context."""
		return {'hour': self.hour}
		
	def get_events(self, *args, **kwargs):
		"""Abort getting events if no hour has been defined."""
		if not self.hour:
			return
		super(HourEventList, self).get_events(*args, **kwargs)
		
	def sort_events(self, events):
		"""Sort the events by their start time.
		
		Arguments:
		events -- an unordered list of HourEvent instances
		
		"""
		return sorted(events, key=lambda e: getattr(e.repeat_rule, 'start_time', None))
	
	def _repeating_event_in_hour(self, event):
		"""Return True if the event indicated falls within this list's hour."""
		repeat_rule = RepeatRule(event.recurrence, self.location)
		return repeat_rule.repeats_between_times(self.hour, datetime.time(hour=self.hour.hour + 1))		
	
	def handle_event(self, calendar, event):
		"""Add an event to the list if it is a repeating event at the right time.
		
		Arguments:
		calendar -- a LocationCalendar instance
		event -- a raw Google Calendar event
		
		"""
		
		event_id = event.id.text
		if event_id not in self._added_events:
			if self._repeating_event_in_hour(event):
				self.add_event(calendar, event.title.text, event.recurrence)
				self._added_events.append(event_id)

