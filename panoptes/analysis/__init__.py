
from django.db.models import Q
from django.template.loader import render_to_string

from panoptes.analysis.axes import AxisBase
from panoptes.analysis.axes.pairs import axis_pair_is_valid
from panoptes.analysis.exceptions import InvalidAxisPair
from panoptes.core.models import Session

import math

class FilteredSessions(object):
	"""An object that managers filters applied to session data."""

	def __init__(self, location=None, start_date=None, end_date=None, start_time=None, end_time=None, weekdays=[], x_detail=None):
		"""Initialize the session filters for the all-optional kwargs.

		Arguments:
		location -- a Location instance
		start_date -- a date instance for the date filter start
		end_date -- a date instance for the date filter end
		start_time -- a time instance for the time filter start
		end_time -- a time instance for the time filter end
		weekdays -- an iterable of ISO-format weekday numbers
		x_detail -- an instance of a datetime provided by an x-axis
		                   
		"""

		self.x_axis = None
		self.y_axis = None
		
		self.location   = location
		self.start_date = start_date
		self.end_date   = end_date
		self.start_time = start_time
		self.end_time   = end_time
		self.weekdays   = weekdays
		self.x_detail   = x_detail
		
	def _axis_class(self, axis):
		"""Return the class of the given axis, or None if the axis is None.
		
		This method exists due to the fact that the axes used are often referred to by
		class but are sometimes referred to as an instance of the class.  Since most
		internal calculations expect the axis to be a class, this tries to return the
		class of an axis instance.
		
		Arguments
		axis -- either a class or an instance descended from Axis.
		
		"""
		if not axis:
			return None
		elif axis.__class__ == AxisBase:
			return axis
		else:
			return axis.__class__  

	def set_axes(self, x_axis, y_axis):
		"""Set the axes to instances of the given XAxis and YAxis classes."""

		x_axis_class = self._axis_class(x_axis)
		y_axis_class = self._axis_class(y_axis)
		
		if x_axis_class and y_axis_class:
			if axis_pair_is_valid(x_axis_class, y_axis_class):
				self.x_axis = x_axis_class()
				self.y_axis = y_axis_class()
			else:
				raise InvalidAxisPair
			
			#  Allow an x-axis to apply filters to the session
			if self.x_detail:
				self.x_axis.filter_sessions_for_detail(self, self.x_detail)

	def new_axes(self, x_axis, y_axis):
		"""
		Create a copy of the filtered sessions using the given XAxis and YAxis
		instances.
		"""
		new_sessions = FilteredSessions(
			location=self.location,
			start_date=self.start_date,
			end_date=self.end_date,
			start_time=self.start_time,
			end_time=self.end_time,
			weekdays=self.weekdays,
			x_detail=self.x_detail
		)
		new_sessions.set_axes(x_axis, y_axis)
		return new_sessions

	def all_sessions(self):
		"""Return a queryset of Session instances matching the user's filters.

		This method allows the axes used to build the Session queryset to provide
		additional filtering if a detail view for a particular x-value is being
		requested.
		"""
						
		return Session.objects.filter_sessions(
			location=self.location,
			start_date=self.start_date,
			end_date=self.end_date,
			start_time=self.start_time,
			end_time=self.end_time,
			weekdays=self.weekdays,
			related_fields=self.x_axis.provide_related_fields() + self.y_axis.provide_related_fields())

	def create_plot(self):
		"""Create a plot of the data using the axes provided as a Plot instance."""

		if not self.x_axis or not self.y_axis:
			raise ValueError("You can only call create_plot() on a FilteredSessions instance that has had axes set via the set_axes() method")

		sessions = self.all_sessions()
		x_values = self.x_axis.generate_values(sessions, self)
		y_values = self.y_axis.generate_values(self.x_axis, x_values, sessions, self)

		return Plot(self.x_axis, self.y_axis, x_values, y_values)		 

class Plot(object):
	"""A container for a plot of x- and y-values."""

	_KEYPOINT_COUNT = 5
	_Y_VALUE_POINTS = 3

	def __init__(self, x_axis, y_axis, x_values, y_values):
		"""Create a plot for the given data on the given Axis instances."""

		self.x_axis   = x_axis
		self.y_axis   = y_axis
		self.x_values = x_values
		self.y_values = y_values

		self._length = len(x_values)
		self._index  = -1

		try:
			max_y = int(max(self.y_values))
		except (ValueError, TypeError):
			max_y = 0

		#  Generate data on the percentage of each y-value relative to the maximum
		#  y-val contained in the set, making sure to provide an intensity of at least
		#  1% if the y-value has data but has a percentage less than 1%, since the int
		#  version of the percentage is used for all display calculations.
		if max_y:
			self.y_percentages = []
			for y_value in self.y_values:
				try:
					intensity = int(math.ceil((float(y_value) / float(max_y)) * 100))
				except (ValueError, ZeroDivisionError):
					intensity = 0
				self.y_percentages.append(intensity)			
		else:
			self.y_percentages = [0] * len(self.y_values)

		#  Assemble a keypoint lookup table
		self._keypoints = []
		if self._KEYPOINT_COUNT:
			x_values_length = len(self.x_values)
			keypoint_step = max(x_values_length / self._KEYPOINT_COUNT, 1)
			self._keypoints = [not i % keypoint_step for i in xrange(0, x_values_length)]
			
		#  Assemble a list of evenly spaced rendered y-values that can be used in
		#  visualizing the data, as long as the y-values are simple integers
		self.y_labels = []
		if self._Y_VALUE_POINTS and max_y and isinstance(max_y, (long, int)): 
			current_y = self._Y_VALUE_POINTS
			while current_y > 0:
				raw_y = int(max_y * float(current_y) / self._Y_VALUE_POINTS)
				try:
					rendered_y = self.y_axis.render_value(raw_y)
				except:
					rendered_y = raw_y
				self.y_labels.append(rendered_y)
				current_y -= 1
				
	@property
	def max_y_value(self):
		"""The maximum y-value in the plot."""
		return max(self.y_values)

	def __iter__(self):
		return self
	
	def __getitem__(self, key):
		"""Return a PlotPoint instance for the point at the given x-value.
		
		Arguments:
		key -- an instance of a unique and valid value in the plot's x-values
		
		Returns: a PlotPoint instance for the found x-value, or raises a KeyError
		
		"""
		try:
			point = self._make_plot_point(self.x_values.index(key))
		except ValueError:
			raise KeyError
		else:
			if not point:
				raise KeyError
			return point

	def _is_keypoint(self, i):
		"""Return True if the point whose x-index is at `i` is a keypoint."""
		try:
			return self._keypoints[i]
		except IndexError:
			return False

	def _make_plot_point(self, i):
		"""Return a PlotPoint instance to plot the values at the x-index `i`."""
		try:
			return PlotPoint(
				self.x_values[i],
				self.x_axis.render_value(self.x_values[i]),
				self.x_axis.serialize_value(self.x_values[i]),
				self.y_values[i],
				self.y_axis.render_value(self.y_values[i]),
				self.y_axis.serialize_value(self.y_values[i]),
				self.y_percentages[i],
				u"%(y)s %(x)s" % {
								'x': self.x_axis.verbose_value(self.x_values[i]),
								'y': self.y_axis.verbose_value(self.y_values[i])},
				self._is_keypoint(i))
		except IndexError:
			return None

	def next(self):
		"""Cycle to the next x-value."""
		self._index += 1
		point = self._make_plot_point(self._index)
		if point:
			return point
		else:
			self._index = -1
			raise StopIteration

class PlotPoint(object):
	"""A point on a plot, describing the raw values and their rendered form."""

	def __init__(self, x_value, x_label, x_serialized, y_value, y_label, y_serialized, y_percent, y_verbose, is_keypoint):
		"""Store the values and labels for the point."""
		self.x_value      = x_value
		self.x_label      = x_label
		self.x_serialized = x_serialized
		self.y_value      = y_value
		self.y_label      = y_label
		self.y_serialized = y_serialized
		self.y_percent    = y_percent
		self.y_verbose    = y_verbose
		self.is_keypoint  = is_keypoint
