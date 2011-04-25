
from django import forms
from django.template.loader import render_to_string

from panoptes.core.utils.registry import create_registry

PanelRegistry = create_registry('slug')

def create_panel(index, slug, sessions, options):
	"""Return an instance of the panel defined by the slug.
	
	Arguments:
	index -- the 0-indexed order of the panel
	slug -- a string that should match the `slug` attribute of a panel
	sessions -- a FilteredSessions instance
	options -- a dict that will be used as kwargs for the panel's `init` call
	
	Returns: an instance of a panel
	
	"""
	Panel = PanelRegistry.get_registry_item(slug)
	return Panel(index, sessions, **options)

class BasePanel(object):
	"""An abstract base for an analysis panel."""
		
	__metaclass__ = PanelRegistry
	
	slug = None
	template = None
	
	def __init__(self, index, sessions):
		"""Create the panel for viewing the given sessions.
		
		Arguments:
		index -- the 0-indexed order of the panel in its lens
		sessions -- a FilteredSessions instance
		
		"""
		self.index = index
		self.sessions = sessions
		
	def render(self):
		"""Return HTML representing the panel."""
		kwargs = self.provide_base_render_args()
		kwargs.update(self.provide_render_args())
		return render_to_string(self.provide_template() or self.template, kwargs)
	
	def provide_base_render_args(self):
		"""Provide shared render args that all panels will expect."""
		return {'panel': self, 'filters': self.sessions}
	
	def provide_render_args(self):
		"""Return a dict of render args to use for rendering the panel."""
		return {}
	
	def provide_template(self):
		"""Return a path to a template used to render the panel.
		
		This allows a child template to dynamically provide a template."""
		return None
	
	def provide_media(self):
		"""Return a Django form media object of the panel's media."""
		return forms.Media()
	
	@property
	def is_primary(self):
		"""True if the panel is the first in its lens."""
		return self.index == 0
