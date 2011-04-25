
from django.template.loader import render_to_string

from panoptes.analysis.panels.charting.charts.base import BaseChart

class BarChart(BaseChart):
	"""A two-dimensional bar chart."""

	slug = "bar"

	class Media:	
		js = ('panoptes/js/analysis/charts/bar.js',)
		css = {
			'all': ('panoptes/css/analysis/panels/charting/charts/bar.css',)}

	def render(self):
		"""Return HTML used to build a 2D bar chart."""

		return render_to_string('panoptes/analysis/panels/charts/bar.html', {
			'plot':     self.sessions.create_plot(),
			'sessions': self.sessions
		})
	