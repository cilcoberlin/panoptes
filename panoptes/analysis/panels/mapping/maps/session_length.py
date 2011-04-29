
from panoptes.analysis.panels.mapping.maps.base import BaseMap

class SessionLengthMap(BaseMap):
	"""A location map that shows the average session length per workstation."""

	slug = "session_length"
	template = "panoptes/analysis/panels/maps/session_length.html"
