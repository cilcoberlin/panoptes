
from django.template.defaultfilters import striptags
from django.utils.translation import ugettext as _

from icalendar.prop import vDatetime, vRecur
import pytz

import re

class RepeatRule(object):
	"""A representation of an iCalendar repeat rule."""

	#  A regex to find the timezone information in a recurrence rule
	_TIMEZONE_MATCH    = re.compile(r'BEGIN:VTIMEZONE.*END:VTIMEZONE', re.MULTILINE | re.DOTALL)
	_TIMEZONE_ID_MATCH = re.compile(r'TZID:([a-zA-Z\/_]+)')
	
	#  The names of important keys in the repeat rule text
	_REPEAT_KEYS = ('DTSTART', 'DTEND', 'RRULE')
	
	#  A mapping of iCalendar weekday abbreviations to their full names
	_WEEKDAYS = {
		'SU': _("sunday"),
		'MO': _("monday"),
		'TU': _("tuesday"),
		'WE': _("wednesday"),
		'TH': _("thursday"),
		'FR': _("friday"),
		'SA': _("saturday")
	}
	
	def __init__(self, recurrence, location):
		"""Create a representation of the rule from a recurrence instance.
		
		Arguments:
		rule -- a Google Calendar recurrence instance
		
		"""
		self.location = location
		self.recurrence = recurrence
		self._parse_rule()
		
	def __nonzero__(self):
		"""Count as nonzero only if a valid repeat rule is defined."""
		return self._rrule is not None 
		
	def _parse_ical_datetime(self, dt, tz_name):
		"""Return a timezone-aware datetime from the iCalendar datetime format.
		
		Since this will always be from a Google Calendar event feed, and each calendar
		has a timezone associated with it, the datetime string will always be in the
		TZID=Timezone_Name:YYYYMMDDTHHMMSS format.
		
		If the datetime is invalid, this will return None.  If no timezone is defined
		for the datetime string, the timezone whose name is specified in the tz_name
		string is used.
		
		Arguments:
		dt -- a string of the iCalendar datetime
		
		Returns: a timezone-aware datetime instance or None
		"""
			
		dt_parts = dt.split(':')
		_datetime = None
		
		#  Apply timezone information to the time, either from its own specification or
		#  from the passed timezone name
		if len(dt_parts) == 2:
			tzinfo = dt_parts[0].split('=')[1]
			timezone = pytz.timezone(tzinfo)
			_datetime = dt_parts[1]
		else:
			_datetime = dt_parts[0]
			if tz_name:
				timezone = pytz.timezone(tz_name)
	
		#  Return the datetime with timezone information
		try:
			parsed_datetime = vDatetime.from_ical(_datetime)
		except ValueError:
			return None
		else:
			return timezone.localize(parsed_datetime)
		
	def _parse_rule(self):
		"""Transform the iCalendar repeat rule into an object."""
		
		self.start_time = None
		self.end_time = None
		self.starts = None
		self.ends = None
		
		self._rrule = None
		self._frequency = None

		if not self.recurrence:
			return
		
		rule_text = self.recurrence.text
		
		#  Extract the timezone for the recurring event, using the given location's
		#  timezone if a timezone for the event could not be found
		try:
			tz_name = self._TIMEZONE_ID_MATCH.search(rule_text).group(1)
		except AttributeError:
			tz_name = self.location.timezone.zone
		
		#  Strip the tags and timezone information from the raw rule text, and break
		#  the start and end date apart from the repeat rule
		rule_parts = dict([(key, "") for key in self._REPEAT_KEYS])
		raw_rule = striptags(rule_text)
		raw_rule = re.sub(self._TIMEZONE_MATCH, "", raw_rule).strip()
		for line in re.split(r'\n+', raw_rule):
			line_parts = re.split(r'[:;]', line, 1)
			if len(line_parts) == 2:
				rule_parts[line_parts[0]] = line_parts[1].strip()
		
		#  Set a possible start date and time boundaries
		start = self._parse_ical_datetime(rule_parts['DTSTART'], tz_name)
		end = self._parse_ical_datetime(rule_parts['DTEND'], tz_name)
		if start:
			self.starts = start
			self.start_time = start.time()
		if end:
			self.end_time = end.time()
		
		#  Parse the repeat rule
		try:
			self._rrule = vRecur.from_ical(rule_parts['RRULE'])
		except ValueError:
			return
		self._frequency = self._rrule.get('FREQ', None)
		
		#  Get the localized end date if one is available
		try:
			until = self._rrule.get('UNTIL', [])[0]
		except IndexError:
			return
		self.ends = until.astimezone(pytz.timezone(tz_name))

	def repeats_between_times(self, start, end):
		"""Return True if the repeat rule occurs between the given times.
		
		Arguments:
		start -- the starting time bound, as a time instance
		end -- the ending time bound, as a time instance
		
		"""
		repeats = False
		if self.start_time:
			repeats |= start.hour <= self.start_time.hour < end.hour
		if self.end_time:
			repeats |= start.hour < self.end_time.hour <= end.hour
		return repeats

	def _frequency_has_key(self, key):
		"""Return True if the repeat rule's frequency has the given key."""
		return self._frequency and key in self._frequency

	@property
	def is_daily(self):
		"""True if the rule repeats daily."""
		return self._frequency_has_key('DAILY')

	@property
	def is_weekly(self):
		"""True if the rule repeats weekly."""
		return self._frequency_has_key('WEEKLY')
	
	@property
	def is_monthly(self):
		"""True if the rule repeats monthly."""
		return self._frequency_has_key('MONTHLY')

	@property
	def is_yearly(self):
		"""True if the rule repeats yearly."""
		return self._frequency_has_key('YEARLY')
	
	@property
	def weekdays(self):
		"""The ordered names of the days on which the rule repeats."""
		if self.is_weekly and 'BYDAY' in self._rrule:
			return [self._WEEKDAYS.get(day, u"").title() for day in self._rrule['BYDAY']]
		else:
			return []
		
	@property
	def has_time_bounds(self):
		"""True if the event has a start or end date defined."""
		return bool(self.starts or self.ends)
