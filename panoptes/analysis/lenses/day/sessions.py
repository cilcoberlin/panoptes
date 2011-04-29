
from panoptes.analysis.lenses import BaseLens

class Lens(BaseLens):
	"""A lens to view the number of sessions per day."""

	default = True

	slug = "sessions-per-day"

	x_axis_slug = "days"
	y_axis_slug = "session-count"

	panels = (
		('chart',  {'chart': 'bar'}),
		('map',    {'map': 'days'}),
		('events', {'list': 'day'})
	)
