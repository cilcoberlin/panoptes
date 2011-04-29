
from django.db import models
from django.utils.translation import ugettext

from panoptes.analysis.lenses import BaseLens, lens_factory
from panoptes.analysis.fields import LensChoiceField

class LensField(models.Field):
	"""A field for selecting a lens used to analyze data.

	The choice of lenses is dynamically built from the currently registered lenses,
	and the chosen lens is stored using its slug.
	"""

	__metaclass__ = models.SubfieldBase

	empty_strings_allowed = False

	_DEFAULT_MAX_LENGTH = 100

	def __init__(self, *args, **kwargs):
		kwargs['max_length'] = self._DEFAULT_MAX_LENGTH
		super(LensField, self).__init__(*args, **kwargs)

	def get_internal_type(self):
		return "SlugField"

	def formfield(self, **kwargs):
		defaults = {'form_class': LensChoiceField}
		defaults.update(kwargs)
		return super(LensField, self).formfield(**defaults)

	def _resolve_lens_from_slug(self, slug):
		"""Return the Lens class matching the given slug."""
		Lens = lens_factory(slug)
		if not Lens:
			raise TypeError(ugettext("Invalid lens for slug %(slug)s") % {'slug': slug})
		return Lens

	def to_python(self, value):
		"""Resolve the lens slug to a Lens class."""

		if value is None:
			return None
		try:
			if issubclass(value, BaseLens):
				return value
		except TypeError:
			return self._resolve_lens_from_slug(value)

	def get_prep_value(self, value):
		"""Render the lens as its slug before saving."""
		return getattr(value, 'slug', None)

	def get_prep_lookup(self, lookup_type, value):
		"""Search for a lens using its slug."""

		if lookup_type == 'exact':
			return self.get_prep_value(value)
		else:
			raise TypeError(ugettext('Lookup type %(lookup)s not supported') % {'lookup': lookup_type})
