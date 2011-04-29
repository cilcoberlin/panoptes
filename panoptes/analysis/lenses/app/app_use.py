
from panoptes.analysis.lenses import BaseLens

class Lens(BaseLens):
	"""A lens to view the number of sessions that used an application."""

	slug = "app-usage-per-app"

	x_axis_slug = "apps"
	y_axis_slug = "app-use"

	panels = (
		('chart',  {'chart': 'bar'}),
		('map',    {'map': 'apps'})
	)
