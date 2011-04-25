
from django import forms
from django.utils.translation import ugettext_lazy as _

from panoptes.analysis.lenses import get_all_lenses, get_default_lens, lens_factory
from panoptes.core.utils.constants import WEEKDAYS_SINGLE_LETTER

class LensChoiceField(forms.ChoiceField):
	"""
	A choice field for selecting a lens through which to view data. If a valid
	Lens is chosen, an instance of that Lens is returned as the cleaned data.
	"""

	def __init__(self, *args, **kwargs):
		"""Make any available lenses the choices."""

		kwargs.update({
			'choices': [(lens.slug, lens.make_title()) for lens in get_all_lenses()],
			'initial': get_default_lens().slug})
		super(LensChoiceField, self).__init__(*args, **kwargs)

	def clean(self, value):
		"""Return a Lens instance if the slug is valid."""

		Lens = lens_factory(value)
		if not Lens:
			raise forms.ValidationError(_("select a valid view"))
		return Lens

class WeekdayChoiceField(forms.MultipleChoiceField):
	"""A multiple-choice field for selecting one or more weekdays."""

	def __init__(self, *args, **kwargs):
		kwargs['choices'] = zip(range(1,8), [weekday.title() for weekday in WEEKDAYS_SINGLE_LETTER])
		kwargs['widget'] = forms.CheckboxSelectMultiple
		super(WeekdayChoiceField, self).__init__(*args, **kwargs)

	def clean(self, values):
		"""Cast the selections as integers."""
		try:
			return [int(value) for value in values]
		except (TypeError, ValueError):
			raise forms.ValidationError(_("invalid weekday"))
