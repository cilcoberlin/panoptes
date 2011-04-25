
from django.db import models
from django.utils.translation import ugettext

import pytz

import datetime

#  Code for this comes from http://djangosnippets.org/snippets/1337/
class MACAddressField(models.Field):
	"""A model field that contains a normalized MAC address."""

	empty_strings_allowed = False

	def __init__(self, *args, **kwargs):
		kwargs['max_length'] = 17
		super(MACAddressField, self).__init__(*args, **kwargs)

	def get_internal_type(self):
		return "CharField"

	def formfield(self, **kwargs):

		from panoptes.core.fields import MACAddressField as FormField

		defaults = {'form_class': FormField}
		defaults.update(kwargs)
		return super(MACAddressField, self).formfield(**defaults)

	def get_prep_value(self, value):
		"""Normalize the MAC address as AABBCCDDEEFF before saving."""
		return "".join([c for c in value if c not in ':-']).upper()

	def get_prep_lookup(self, lookup_type, value):
		"""Normalize a MAC address that's being requested."""

		if lookup_type == 'exact':
			return self.get_prep_value(value)
		else:
			raise TypeError(ugettext('Lookup type %(lookup)s not supported') % {'lookup': lookup_type})

class TimeZoneField(models.Field):
	"""A model field that stores a timezone by its string identifier."""
	
	empty_strings_allowed = False
	
	_DEFAULT_MAX_LENGTH = 100
	
	def __init__(self, *args, **kwargs):
		kwargs['max_length'] = self._DEFAULT_MAX_LENGTH
		super(TimeZoneField, self).__init__(*args, **kwargs)

	def get_internal_type(self):
		return "CharField"

	def formfield(self, **kwargs):

		from panoptes.core.fields import TimeZoneSelectField

		defaults = {'form_class': TimeZoneSelectField}
		defaults.update(kwargs)
		return super(TimeZoneField, self).formfield(**defaults)

	def to_python(self, value):
		"""Return the timezone string as a pytz timezone."""
		if isinstance(value, datetime.tzinfo):
			return value
		
		try:
			return pytz.timezone(value)
		except pytz.exceptions.UnknownTimeZoneError:
			raise TypeError(ugettext("Invalid time zone %(zone)s") % {'zone': value})
		