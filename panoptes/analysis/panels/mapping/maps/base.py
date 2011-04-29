
from django import forms
from django.template.loader import render_to_string

from panoptes.analysis.axes.x.workstations import Axis as Workstations
from panoptes.analysis.exceptions import InvalidAxisPair
from panoptes.core.models import LayoutRow
from panoptes.core.utils.registry import create_registry

MapRegistry = create_registry('slug')

class BaseMap(object):
	"""An abstract base class for a location map."""

	__metaclass__ = MapRegistry

	slug = None

	template = "panoptes/analysis/layout.html"

	def __init__(self, sessions):
		"""Create the location map.

		Arguments:
		sessions -- a FilteredSessions instance

		"""
		self.location = sessions.location
		self.sessions = sessions

	def render(self):
		"""Return HTML of the location with an optional overlay of data."""

		#  Attempt to create an overlay as a plot of the sessions, with the x-axis
		#  remapped to workstations from whatever it was before
		plot = None
		if self.sessions:
			try:
				sessions = self.sessions.new_axes(Workstations, self.sessions.y_axis)
			except InvalidAxisPair:
				pass
			else:
				plot = sessions.create_plot()

		return render_to_string(self.template, {
			'location': self.location,
			'rows':     LayoutRow.objects.overlaid_rows(self.location, plot)
		})

	@property
	def media(self):
		"""Return the map's media."""
		return forms.Media(getattr(self, 'Media', None))


