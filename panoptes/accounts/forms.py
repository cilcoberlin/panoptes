
from django import forms

from panoptes.accounts.fields import UserField
from panoptes.accounts.models import UserProfile
from panoptes.core.fields import LocationField
from panoptes.core.utils.forms import replace_form_field

class UserPreferencesForm(forms.ModelForm):
	"""A form for editing a user's prferences."""

	class Meta:

		model = UserProfile

	def __init__(self, *args, **kwargs):
		"""Customize form fields."""

		super(UserPreferencesForm, self).__init__(*args, **kwargs)

		replace_form_field(self, 'user', UserField())
		replace_form_field(self, 'default_location', LocationField())

		#  If an initial default lens is set, use its slug as the initial value,
		#  unless the initial value is already a slug
		default_lens = self.initial.get('default_lens', None)
		if default_lens:
			self.initial['default_lens'] = getattr(default_lens, 'slug', default_lens)
