
from panoptes.analysis.lenses import BaseLens

class Lens(BaseLens):
	"""A lens to view the average session length per day."""

	slug = "sessions-length-per-day"

	x_axis_slug = "days"
	y_axis_slug = "avg-session-length"

	panels = (
		('chart',  {'chart': 'bar'}),
		('map',    {'map': 'days'}),
		('events', {'list': 'day'})
	)
