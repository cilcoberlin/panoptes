
from django.db import models
from django.utils.translation import ugettext_lazy as _

from panoptes.tracking.widgets import AccountListWidget

import re

class AccountListField(models.CharField):
	"""
	A field that accepts a character-separated list of account names and renders
	them in python a tuple ordered by the account name.
	"""

	__metaclass__ = models.SubfieldBase

	description = _("Account list")

	DEFAULT_SEPARATOR = ","
	SEPARATORS = [" "]

	def __init__(self, *args, **kwargs):
		"""
		Accept an additional `separators` kwarg that allows a user to extend the
		separators than can be used.
		"""

		#  Combine possible user separators with the default
		self._separators = kwargs.pop('separators', self.SEPARATORS)
		if self.DEFAULT_SEPARATOR not in self._separators:
			self._separators.append(self.DEFAULT_SEPARATOR)

		defaults = {'max_length': 255}
		defaults.update(kwargs)

		super(AccountListField, self).__init__(*args, **defaults)

	def get_internal_type(self):
		return 'CharField'

	def get_prep_value(self, value):
		"""Reassemble the tuple of account names as a string."""
		try:
			return self.DEFAULT_SEPARATOR.join(value)
		except TypeError:
			return ""

	def to_python(self, value):
		"""Return the account names as a tuple."""
		if value is None:
			return ()
		if isinstance(value, tuple):
			return value
		return tuple(sorted([name for name in re.split(r'[%s]+' % "".join(self._separators), value) if name]))

	def formfield(self, **kwargs):
		kwargs['widget'] = AccountListWidget
		return super(AccountListField, self).formfield(**kwargs)
