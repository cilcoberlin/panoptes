
from django import forms
from django.utils.translation import ugettext_lazy as _

from panoptes.core.models import Location

from pytz import common_timezones

import re

class TimeZoneSelectField(forms.ChoiceField):
	"""A form that allows the user to select a common timezone."""
	
	default_error_messages = {
		'invalid': _("select a proper timezone")
	}
	
	def __init__(self, *args, **kwargs):
		"""Populate the field's choices with common timezones."""
		kwargs['choices'] = zip(common_timezones, common_timezones) 
		super(TimeZoneSelectField, self).__init__(*args, **kwargs)

class MACAddressField(forms.RegexField):
	"""A form field that accepts a MAC address in its various forms."""

	default_error_messages = {
		'invalid': _('enter a valid MAC address'),
	}

	mac_re = re.compile(r'^([0-9a-fA-F]{2}([:-]?|$)){6}$')

	def __init__(self, *args, **kwargs):
		super(MACAddressField, self).__init__(self.mac_re, *args, **kwargs)

class LocationField(forms.ModelChoiceField):
	"""
	A model choice field to select a location, with the initial value being the
	default Location instance.
	"""

	def __init__(self, *args, **kwargs):

		kwargs['queryset'] = Location.objects.all().order_by('name')
		try:
			kwargs['initial'] = Location.objects.get_default().pk
		except AttributeError:
			pass

		super(LocationField, self).__init__(*args, **kwargs)
