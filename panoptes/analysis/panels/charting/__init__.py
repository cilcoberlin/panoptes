
from django import forms

from django.utils.importlib import import_module

from panoptes.analysis.panels import BasePanel
from panoptes.analysis.panels.charting.charts.base import ChartRegistry

#  Import all chart types so that they can register themselves
from panoptes.analysis.panels.charting.charts import bar

def chart_factory(chart_slug):
	"""
	Return a BaseChart-descended class matching the string given in
	`chart_slug`, otherwise return None.
	"""
	return ChartRegistry.get_registry_item(chart_slug)

class Panel(BasePanel):
	"""A panel that shows a chart of usage for a given period."""

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
		"""Return render args for the chart."""
		if self.chart:
			return self.chart.provide_render_args()
		return {}

	def provide_template(self):
		"""Render using the template of the chart, if one exists."""
		return getattr(self.chart, 'template', self.template)

	def provide_media(self):
		"""Return the media used by the chart."""
		return forms.Media(self.Media) + self.chart.media


