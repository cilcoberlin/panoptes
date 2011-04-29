
from django import forms

from django.utils.importlib import import_module

from panoptes.analysis.panels import BasePanel
from panoptes.analysis.panels.charting.charts.base import ChartBase

#  Import all chart types so that they can register themselves
from panoptes.analysis.panels.charting.charts import bar

def chart_factory(chart_slug):
	"""
	Return a BaseChart-descended class matching the string given in
	`chart_slug`, otherwise return None.
	"""
	try:
		return ChartBase.registered_charts[chart_slug]
	except KeyError:
		raise ValueError("No chart could be found with the slug %s" % chart_slug)

class Panel(BasePanel):
	"""A panel that shows a list of events for a given period."""

	slug = "chart"
	template = "panoptes/analysis/panels/charts/panel.html"

	class Media:
		css = {'all': ("panoptes/css/analysis/panels/charting/chart.css",)}

	def __init__(self, *args, **kwargs):
		"""Create a new chart."""

		slug = kwargs.pop('chart', None)
		if not slug:
			raise ValueError("You must provide a 'chart' argument to the charting panel")

		super(Panel, self).__init__(*args, **kwargs)

		Chart = chart_factory(slug)
		self.chart = Chart(self.sessions)

	def provide_render_args(self):
		"""Return args for rendering the chart."""
		return {'chart': self.chart.render()}

	def provide_media(self):
		"""Return the media used by the chart."""
		return forms.Media(self.Media) + self.chart.media


