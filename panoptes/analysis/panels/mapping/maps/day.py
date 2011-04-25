
from panoptes.analysis.panels.mapping.maps.base import BaseMap

class DayMap(BaseMap):
	"""A location map that shows workstation usage for a day."""

	slug = "days"

	template = "panoptes/analysis/panels/maps/day.html"
