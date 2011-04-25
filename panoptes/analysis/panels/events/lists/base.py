
from panoptes.analysis.panels.events.models import LocationCalendar
from panoptes.analysis.panels.events.rrule import RepeatRule
from panoptes.core.utils.registry import create_registry

from gdata.calendar.client import CalendarClient

EventRegistry = create_registry('slug')

class BaseEvent(object):
	"""A single Google Calendar event."""

	def __init__(self, location, title, repeat_rule):
		"""Create a new representation of a Google Calendar event.
		
		Arguments:
		title -- a string with the event's title
		repeat_rule -- a Recurrence object containing a possible repeat rule
		
		"""

		self.title = title
		self.location = location
		self.repeat_rule = RepeatRule(repeat_rule, location)
			
	def verbose_start(self):
		"""A verbose, readable rendition of the event's start."""
		raise NotImplementedError
	
	def verbose_end(self):
		"""A verbose, readable rendition of the event's end."""
		raise NotImplementedError
	
	def verbose_repeat_rule(self):
		"""A verbose, readable rendition of the repeat rule."""
		return self.repeat_rule.verbose_rule()
	
	@property
	def is_repeating(self):
		"""True if the event has a repeat rule applied to it."""
		return bool(self.repeat_rule)

class BaseEventList(object):
	"""An abstract base list of Google Calendar events.
	
	This is intended to be extended by child event list classes.  A child event can
	override the following attributes:
	
	event_class -- An instance of an object descended from BaseEvent that
	               represents an event of the type stored by the list
	"""

	__metaclass__ = EventRegistry

	slug = None

	event_class = BaseEvent
	
	template = "panoptes/analysis/events.html"
	
	_GCAL_VISIBILITY = "public"
	_GCAL_PROJECTION = "full"

	def __init__(self, filters):
		"""Initialize the event list.
		
		Arguments:
		filters -- a FilteredSessions instance
		
		"""
		self._events = {}
		self.location = filters.location
		self.filters = filters
		
	def __nonzero__(self):
		"""Report as nonzero if no events are defined for any calendar."""
		return any(events for events in self._events.values())
		
	def has_requested_events(self):
		"""
		Return True if the event list has made an attempt to fetch Google Calendar
		events, which is indicated by default by the presence of an x-value filter in
		the sessions object.
		"""
		return self.filters.x_detail is not None
		
	def events_by_calendar(self):
		"""Return a list of dicts with information on the calendar and events.
		
		The list of dicts will be organized by the `order` attribute of the
		LocationCalendar.  Each dict will have a `calendar` key holding a
		LocationCalendar instance and an `events` key holding a list of objects
		descended from BaseEvent, ordered by their defined sorting method.
		"""
		
		by_calendar = []
		for calendar in LocationCalendar.objects.all_for_location(self.location):
			if self._events.get(calendar, None):
				by_calendar.append({
								'calendar': calendar,
								'events': self.sort_events(self._events[calendar])})
		return by_calendar
	
	def sort_events(self, events):
		"""Sort the passed events in an appropriate manner.
		
		This can be overridden by a child event list to allow it to perform a custom
		sort appropriate to the type of events being stored.
		
		Arguments:
		events -- a list of objects descended from BaseEvent
		
		"""
		raise NotImplementedError
		
	def get_events(self):
		"""Populate the event list with Google Calendar events."""
		
		calendars = LocationCalendar.objects.all_for_location(self.location)
		if not calendars:
			return None

		client = CalendarClient()
		for calendar in calendars:
			feed_uri = client.GetCalendarEventFeedUri(
												calendar=calendar.calendar_id,
												projection=self._GCAL_PROJECTION,
												visibility=self._GCAL_VISIBILITY)
			feed_args = {'uri': feed_uri}
			feed_args.update(self.provide_feed_args())
			feed = client.GetCalendarEventFeed(**feed_args)
			
			#  Allow a child event list to determine how to handle an event
			self._events[calendar] = []
			for event in feed.entry:
				self.handle_event(calendar, event)
			
	def provide_feed_args(self):
		"""Return a dict used to provide additional kwargs to the GetCalendarEventFeed call."""
		return {}
	
	def handle_event(self, calendar, event):
		"""Perform an action on a Google Calendar event.
		
		This allows a child event list to determine what to do with an event.
		
		Arguments:
		calendar -- a LocationCalendar instance where the event occurred
		event -- a raw Google Calendar event, as returned from GetCalendarEventFeed
		
		"""
		raise NotImplementedError
		
	def add_event(self, calendar, title, repeat_rule, *args):
		"""Add a new event to the event list.
		
		The rest of the arguments for this method will be the same as the arguments
		that are passed to the `__init__` method of the event class associated with
		this list.
		
		Arguments:
		calendar -- a LocationCalendar instance
		title -- a string of the event's title
		repeat_rule -- a string of the event's possible iCalendar repeat rule
		
		"""
		self._events[calendar].append(self.event_class(self.location, title, repeat_rule, *args))
		
	def provide_render_args(self):
		"""Render context arguments used to render the list."""
		return {}
		


