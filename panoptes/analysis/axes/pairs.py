
def get_y_generator_method(x_axis, y_axis):
	"""Return the y-value generator method for the given x-axis.
	
	Arguments:
	x_axis -- an instance of an XAxis class
	y_axis -- an instance of a YAxis class
	
	Returns: 
	A reference to the y-value generator if it was found, and otherwise None.
	
	"""
		
	try:
		method_name = AXIS_PAIRS[x_axis.slug][y_axis.slug]
	except KeyError:
		raise ValueError("A %(x)s x-axis cannot be paired with a %(y)s y-axis" % {
			'x': x_axis.__class__.name,
			'y': x_axis.__class__.name
		})

	y_method = getattr(y_axis, method_name, None)
	if not y_method:
		raise ValueError("No method named '%(method)s' exists for the %(axis)s y-axis" % {
			'method': method_name,
			'axis': y_axis.__class__.name
		})

	return y_method

def axis_pair_is_valid(x_axis, y_axis):
	"""Return True if the XAxis and YAxis classes passed can be used together."""
	return x_axis.slug in AXIS_PAIRS and y_axis.slug in AXIS_PAIRS[x_axis.slug]

#  The keys are the slugs of an x-axis class, the value of the keys are dicts
#  whose keys are y-axis class slugs and whose value is a single string that is
#  the name of a method on the y-axis class that generates values for the x-axis
#  that is the parent key.
AXIS_PAIRS = {

	'apps': {
		'app-use': 'application_values'
	},

	'days': {
		'avg-session-length': 'day_values',
		'session-count': 'day_values'
	},

	'hours': {
		'session-count': 'hour_values'
	},

	'workstations': {
		'app-use': 'workstation_values',
		'avg-session-length': 'workstation_values',
		'session-count': 'workstation_values'
	}
}