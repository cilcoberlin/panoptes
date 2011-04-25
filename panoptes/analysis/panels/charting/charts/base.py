
from django import forms

class ChartBase(type):
	"""Custom metaclass for charts that maintains a repository of all charts."""

	registered_charts = {}

	def __init__(self, name, bases, attrs):
		"""Update our registry of declared charts, keyed by the chart slug."""

		super(ChartBase, self).__init__(name, bases, attrs)

		if name == "BaseChart":
			return

		if not attrs.get('slug', None):
			raise TypeError("You must provide a slug for the %(chart)s chart" % {'chart': name})

		ChartBase.registered_charts[attrs['slug']] = self

class BaseChart(object):
	"""Abstract base class for a chart.
	
	A child chart must define a string value for the `slug` attribute, and can
	optionally define values for the `js` and `css` attributes, which should be
	structured in the same way as the attributes of a Django Media class.
	"""

	__metaclass__ = ChartBase

	slug = None
	
	def __init__(self, sessions):
		"""
		Create a chart for the data contained in the FilteredSessions instance
		`sessions`.
		"""
		self.sessions = sessions

	def render(self):
		"""Return HTML describing the chart."""
		return u""
	
	@property
	def media(self):
		return forms.Media(getattr(self, 'Media', None))
