
from panoptes.analysis.panels.mapping.maps.base import BaseMap

class SessionMap(BaseMap):
	"""A location map that shows the number of sessions per workstation."""

	slug = "sessions"
	template = "panoptes/analysis/panels/maps/sessions.html"
