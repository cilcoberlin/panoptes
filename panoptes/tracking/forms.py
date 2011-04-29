
from django import forms

from panoptes.core.fields import WorkstationByMACAddressField
from panoptes.core.models import OSType
import panoptes.settings as _settings

import isodate

class CreateSessionForm(forms.Form):
	"""A form used to validate POST data passed when creating a session."""

	mac        = WorkstationByMACAddressField()
	os_type    = forms.ChoiceField(choices=_settings.OS_CHOICES)
	os_version = forms.CharField(required=False)
	user       = forms.CharField(required=False)

	def clean(self):
		"""Normalize some of our passed data."""

		#  Add an 'os' value to the cleaned data that will either be a valid OSType
		#  instance or None, if the OS type reported doesn't make sense
		self.cleaned_data['os'] = OSType.objects.get_or_create(
									self.cleaned_data.get('os_type', None),
									self.cleaned_data.get('os_version', None))

		#  Create an alias for the MAC address
		self.cleaned_data['workstation'] = self.cleaned_data.get('mac', None)

		return self.cleaned_data

class EndSessionForm(forms.Form):
	"""A form used to validate PUT data passed when ending a session."""

	mac    = WorkstationByMACAddressField()
	apps   = forms.CharField(required=False)
	offset = forms.IntegerField(required=False)

	def _parse_datetime(self, dt_string):
		"""Try to return the ISO 8601 datetime string as a datetime instance."""
		try:
			return isodate.parse_datetime(dt_string)
		except (AttributeError, ValueError):
			return None

	def clean_apps(self):
		"""
		Break the apps string passed to the API into a list of two-tuples
		formatted as (reported_name, duration).

		The cleaned data for this field will be a string with information on each app
		separated by a comma.  Each chunk of information will consist of the app name
		and the start and end ISO 8601 datetime of its usage, with each of these data
		separated by a # sign.
		"""

		all_apps = []
		for app in self.cleaned_data.get('apps', '').split(","):
			try:
				reported_name, start, end = app.split("#")
			except ValueError:
				pass
			else:
				try:
					dt_delta = self._parse_datetime(end) - self._parse_datetime(start)
				except TypeError:
					duration = 0
				else:
					duration = dt_delta.seconds
				all_apps.append((reported_name, duration))
		return all_apps

	def clean_offset(self):
		"""Make the offset value be a 0 if it is left blank."""
		offset = self.cleaned_data.get('offset', None)
		if offset is None:
			offset = 0
		return offset

	def clean(self):
		"""Normalize some of the passed data."""

		#  Create an alias for the MAC address
		self.cleaned_data['workstation'] = self.cleaned_data.get('mac', None)

		return self.cleaned_data


