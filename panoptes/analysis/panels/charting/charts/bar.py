
from panoptes.analysis.panels.charting.charts.base import BaseChart

class BarChart(BaseChart):
	"""A two-dimensional bar chart."""

	slug = "bar"
	template = "panoptes/analysis/panels/charts/bar.html"

	class Media:
		js = ('panoptes/js/analysis/charts/bar.js',)
		css = {
			'all': ('panoptes/css/analysis/panels/charting/charts/bar.css',)}

	def provide_render_args(self):
		"""Return HTML used to build a 2D bar chart."""

		return {
			'plot':     self.sessions.create_plot(),
			'sessions': self.sessions
		}
