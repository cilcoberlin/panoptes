
def axis_factory(axis_slug, x=False, y=False):
	"""
	Return a Axis-descended class whose slug matches the `axis_slug`
	string, and None if no axis was found. The search is restricted to X or Y
	axes based on the value of the Boolean kwargs `x` and `y`.
	"""

	if x == y:
		raise ValueError("You must set either `x` or `y` to True when searching for an axis slug")
	key_name = "x" if x else "y"
	
	try:
		return AxisBase.registered_axes[key_name][axis_slug]
	except KeyError:
		raise ValueError("No %(type)s-axis could be found with the slug '%(slug)s'" % {'type': key_name, 'slug': axis_slug})

class AxisBase(type):
	"""Custom metaclass for axes that maintains a repository of all axes."""

	_IGNORE_CLASSES = ['BaseAxis', 'XAxis', 'YAxis']
	_CLASS_MAP = {'XAxis': 'x', 'YAxis': 'y'}

	def __init__(self, name, bases, attrs):
		"""Update our registry of declared axes."""

		super(AxisBase, self).__init__(name, bases, attrs)
		
		if name in self._IGNORE_CLASSES:
			return
		
		base = self.__class__
		if not hasattr(base, 'registered_axes'):
			base.registered_axes = {'x': {}, 'y': {}}
		try:
			axis_type = self._CLASS_MAP[bases[0].__name__]
		except KeyError:
			raise TypeError("Axis %(axis)s should inherit from the XAxis or YAxis class" % {'axis': name})			
		if self.slug in base.registered_axes[axis_type]:
			raise TypeError(" axis %(axis)s cannot use the duplicate slug %(slug)s" % {'axis': name, 'slug': self.slug})
		
		base.registered_axes[axis_type][self.slug] = self

class BaseAxis(object):
	"""
	An axis that can be used to plot session usage data.

	In addition to defining all required methods, any axis class descended from
	this must define a `slug` attribute used for lookup and a `name` attribute
	used for display.
	"""

	__metaclass__ = AxisBase

	name = None
	slug = None

	def render_value(self, value):
		"""
		Render the value given in `value` as a string, so that it can appear in
		a plot of the data. The type of `value` will be determined by the
		method on the current class used to generate the values.
		"""
		raise NotImplementedError
	
	def verbose_value(self, value):
		"""Render the value as a string in a verbose, human-readable format.
		
		For example, an axis that shows the number of sessions could return a value
		like "20 sessions" when presented with a `value` of the integer 20.
		"""
		return self.render_value(value)

	def provide_related_fields(self):
		"""
		Return a list of related field names to follow out when performing the
		query for the current axis' data.
		"""
		return []
	
	def serialize_value(self, value):
		"""Return a serialized string version of the value."""
		raise NotImplementedError
	
	def deserialize_value(self, value):
		"""
		Return an instance of a value appropriate to the current axis from a
		serialized value.
		"""
		raise NotImplementedError
