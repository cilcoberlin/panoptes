
from panoptes.analysis.lenses import BaseLens

class Lens(BaseLens):
	"""A lens to view the number of sessions per hour."""

	slug = "sessions-per-hour"

	x_axis_slug = "hours"
	y_axis_slug = "session-count"

	panels = (
		('chart',  {'chart': 'bar'}),
		('map',    {'map': 'hours'}),
		('events', {'list': 'hour'})
	)
