
from panoptes.analysis.panels.mapping.maps.base import BaseMap

class AppMap(BaseMap):
	"""A location map that shows workstation usage for an application."""

	slug = "apps"
	
	template = "panoptes/analysis/panels/maps/app.html"
