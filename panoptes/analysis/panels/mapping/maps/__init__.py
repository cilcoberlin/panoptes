
from panoptes.analysis.panels.mapping.maps.base import MapRegistry

def map_factory(map_slug):
	"""Return an instance of a Map class with the given slug."""
	return MapRegistry.get_registry_item(map_slug)