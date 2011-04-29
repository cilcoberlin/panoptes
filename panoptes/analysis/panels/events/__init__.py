
from django import forms

from panoptes.analysis.panels import BasePanel
from panoptes.analysis.panels.events.lists import event_list_factory

#  Import all available event lists
from panoptes.analysis.panels.events.lists import day, hour

class Panel(BasePanel):
	"""A panel that shows a list of events for a given period."""

	slug = "events"
	template = "panoptes/analysis/panels/event_lists/panel.html"

	class Media:
		css = {'all': ("panoptes/css/analysis/panels/events/events.css",)}

	def __init__(self, *args, **kwargs):
		"""Create a new event list."""

		slug = kwargs.pop('list', None)
		if not slug:
			raise ValueError("You must provide a 'list' argument to the events panel")

		super(Panel, self).__init__(*args, **kwargs)

		EventList = event_list_factory(slug)
		self.event_list = EventList(self.sessions)
		self.event_list.get_events()

	def provide_template(self):
		"""Render using the template of the event list, if one exists."""
		return getattr(self.event_list, 'template', self.template)

	def provide_render_args(self):
		"""Return render args for an event list panel and the chosen list."""
		render_args = {'event_list': self.event_list}
		try:
			render_args.update(self.event_list.provide_render_args())
		except AttributeError:
			pass
		return render_args

	def provide_media(self):
		"""Return a Media instance for the events panel."""
		return forms.Media(self.Media)
