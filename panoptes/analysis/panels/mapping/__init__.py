
from django import forms
from django.conf import settings

from panoptes.analysis.panels import BasePanel
from panoptes.analysis.panels.mapping.maps import map_factory

import os

#  Import all available map types
from panoptes.analysis.panels.mapping.maps import app_use, sessions, session_length

class Panel(BasePanel):
	"""A panel that shows the map of a location and an optional data overlay."""

	slug = "map"
	template = "panoptes/analysis/panels/maps/panel.html"

	_LOCATION_MEDIA_BASE = "panoptes/%(media)s/analysis/panels/mapping/locations/"

	class Media:
		css = {'all': ("panoptes/css/analysis/panels/mapping/map.css",)}

	def __init__(self, *args, **kwargs):
		"""Create a new usage map."""

		slug = kwargs.pop('map', None)
		if not slug:
			raise ValueError("You must provide a 'map' argument to the mapping panel")

		super(Panel, self).__init__(*args, **kwargs)

		Map = map_factory(slug)
		self.map = Map(self.sessions)

	def provide_render_args(self):
		"""Return render args for the map."""
		if self.map:
			return self.map.provide_render_args()
		return {}

	def provide_template(self):
		"""Render using the template of the map, if one exists."""
		return getattr(self.map, 'template', self.template)

	def _location_media(self, media):
		"""Return a list of the media used by the location."""
		media_file = os.path.join(
								self._LOCATION_MEDIA_BASE % {'media': media},
								"%(slug)s.%(ext)s" % {'slug': self.sessions.location.slug, 'ext': media})
		if os.path.isfile(os.path.join(settings.MEDIA_ROOT, media_file)):
			return (os.path.join(settings.MEDIA_URL, media_file),)
		else:
			return ()

	def provide_media(self):
		"""Return the media used by the chart and the location."""
		location_media = forms.Media(
									js=self._location_media("js"),
									css={'all': self._location_media("css")})
		return forms.Media(self.Media) + location_media + self.map.media


