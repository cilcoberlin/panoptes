
from panoptes.analysis.panels.events.lists.base import EventRegistry

def event_list_factory(list_slug):
	"""Return an event list class with the given slug."""
	return EventRegistry.get_registry_item(list_slug)
