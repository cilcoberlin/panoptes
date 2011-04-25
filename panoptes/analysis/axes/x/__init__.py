
from panoptes.analysis.axes import BaseAxis

class XAxis(BaseAxis):
	"""Abstract base class for an x-axis."""

	def generate_values(self, sessions, filters):
		"""
		This method, which must be implemented by a child class, returns a list
		of values defining the data points used for the current x-axis.

		It takes a `sessions` argument that is a queryset of all the Session
		objects that the axis should consider as part of the data set, as well
		as a FilteredSessions instance in `filters` which defines the filters
		used to arrive at the given Sessions queryset. It should return a list
		of values defining the x-axis.
		"""
		raise NotImplementedError
	
	def filter_sessions_for_detail(self, sessions, value):
		"""
		A template function that can be implemented by a child x-axis that applies
		filters to the FilteredSessions instance to restrict it to a detail view of
		the value passed in, which will be an instance of the type of data generated
		by the current x-axis.
		
		Arguments:
		sessions -- a FilteredSessions instance
		value -- an instance of the data types generated by the x-axis
		
		"""
		pass 
