
from django import forms

from panoptes.core.utils.registry import create_registry

ChartRegistry = create_registry('slug')

class BaseChart(object):
	"""Abstract base class for a chart.

	A child chart must define a string value for the `slug` attribute, and can
	optionally define values for the `js` and `css` attributes, which should be
	structured in the same way as the attributes of a Django Media class.
	"""

	__metaclass__ = ChartRegistry

	slug = None
	template = None

	def __init__(self, sessions):
		"""
		Create a chart for the data contained in the FilteredSessions instance
		`sessions`.
		"""
		self.sessions = sessions

	def provide_render_args(self):
		"""Allow a chart to return render arguments.."""
		return {}

	@property
	def media(self):
		return forms.Media(getattr(self, 'Media', None))
