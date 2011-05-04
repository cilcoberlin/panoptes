
from django.contrib.admin.widgets import AdminTextInputWidget

class AccountListWidget(AdminTextInputWidget):
	"""A widget that handles the tuple of names that the AccountListField uses."""

	def render(self, name, value, attrs=None):
		"""Show the tuple as strings joined with the default separator."""
		from panoptes.tracking.model_fields import AccountListField
		if isinstance(value, tuple):
			value = AccountListField.DEFAULT_SEPARATOR.join(value)
		return super(AccountListWidget, self).render(name, value, attrs)
