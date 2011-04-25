
from panoptes.analysis.panels.mapping.maps.base import BaseMap

class HourMap(BaseMap):
	"""A location map that shows workstation usage for an hour."""

	slug = "hours"

	template = "panoptes/analysis/panels/maps/day.html"
