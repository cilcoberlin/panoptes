
from django import forms
from django.contrib.auth.models import User

class UserField(forms.ModelChoiceField):
	"""A select field for a user that uses their full name for sorting and display."""

	def __init__(self, *args, **kwargs):

		kwargs['queryset'] = User.objects.all().order_by('last_name', 'first_name')
		super(UserField, self).__init__(*args, **kwargs)

	def label_from_instance(self, user):
		"""Return the user's full name."""
		return user.get_full_name()
