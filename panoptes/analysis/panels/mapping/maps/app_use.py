
from panoptes.analysis.panels.mapping.maps.base import BaseMap

class AppMap(BaseMap):
	"""A location map that shows workstation usage for an application."""

	slug = "apps"
	template = "panoptes/analysis/panels/maps/app_use.html"

	def provide_render_args(self):
		"""Add the possible single app being viewed to the render args."""
		render_args = super(AppMap, self).provide_render_args()
		render_args['app'] = self.sessions.x_detail
		return render_args
