
from django import forms
from django.utils.translation import ugettext_lazy as _

from cilcdjango.core.forms import DjangoForm

from panoptes.analysis import FilteredSessions
from panoptes.analysis.fields import LensChoiceField, WeekdayChoiceField
from panoptes.core.fields import LocationField
from panoptes.core.models import Session

import datetime

class SessionFilterForm(DjangoForm):
	"""A form for filtering session data based on user bounds."""

	location   = LocationField(label=_("location"))
	lens       = LensChoiceField(label=_("data view"))
	start      = forms.DateField(label=_("start date"), required=False)
	end        = forms.DateField(label=_("end date"), required=False)
	start_time = forms.TimeField(label=_("start time"), required=False)
	end_time   = forms.TimeField(label=_("end time"), required=False)
	weekdays   = WeekdayChoiceField(label=_("weekdays"), required=False)
	x_detail   = forms.CharField(label=_("x-value detail"), required=False, widget=forms.HiddenInput)
	y_detail   = forms.CharField(label=_("y-value detail"), required=False, widget=forms.HiddenInput)

	def clean(self):
		"""Perform extra validation and resolution of data.
		
		This adds an `x_detail` key to the cleaned data containing the resolved
		x-value whose details should be shown, and also makes sure that the dates and
		times are coherent.
		"""
		
		cleaned_data = self.cleaned_data
		today = datetime.date.today()
		
		#  If a start date is provided but the end date is left blank, end on the
		#  current date
		if cleaned_data.get('start',None) and not cleaned_data.get('end', None):
			cleaned_data['end'] = today
			
		#  If an end date is provided and no start date is given, start at the first
		#  date on which sessions were recorded, or a year ago, if no sessions exist
		if cleaned_data.get('end', None) and not cleaned_data.get('start', None):
			cleaned_data['start'] = Session.objects.first_session_date_for_location(cleaned_data['location'])
		
		#  If the date bounds are left blank, default to viewing the past week
		if not cleaned_data.get('start', None) and not cleaned_data.get('end', None):
			cleaned_data['start'] = today - datetime.timedelta(weeks=1)
			cleaned_data['end'] = today
		
		#  Have empty time filters use the opening or closing time of the location
		if not cleaned_data.get('start_time', None):
			cleaned_data['start_time'] = cleaned_data['location'].earliest_opening
		if not cleaned_data.get('end_time', None):
			cleaned_data['end_time'] = cleaned_data['location'].latest_closing
		
		#  Make sure that the start and end dates and times are properly ordered
		if cleaned_data['start'] > cleaned_data['end']:
			raise forms.ValidationError(_("The start must come before the end date"))
		if cleaned_data['start_time'] > cleaned_data['end_time']:
			raise forms.ValidationError(_("The start time must come before the end time"))
		
		#  Resolve the x- and y-value details if possible
		if cleaned_data.get('x_detail', None):
			x_axis = cleaned_data['lens'].x_axis()
			cleaned_data['x_detail'] = x_axis.deserialize_value(cleaned_data['x_detail'])
		if cleaned_data.get('y_detail', None):
			y_axis = cleaned_data['lens'].y_axis()
			cleaned_data['y_detail'] = y_axis.deserialize_value(cleaned_data['y_detail'])
		cleaned_data['x_detail'] = cleaned_data['x_detail'] or None
		cleaned_data['y_detail'] = cleaned_data['y_detail'] or None
			
		return cleaned_data
	
	def as_filtered_sessions(self):
		"""
		If the form was successfully validated, return a FilteredSessions
		instance built from the form's cleaned data.
		"""

		data = self.cleaned_data
		
		filtered_sessions = FilteredSessions(
			location=data['location'],
			start_date=data.get('start', None),
			end_date=data.get('end', None),
			start_time=data.get('start_time', None),
			end_time=data.get('end_time', None),
			weekdays=data.get('weekdays', []),
			x_detail=data.get('x_detail', None))

		lens = data.get('lens', None)
		if lens:
			filtered_sessions.set_axes(lens.x_axis, lens.y_axis)

		return filtered_sessions
