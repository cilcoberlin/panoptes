
from django.db import models
from django.utils.translation import ugettext_lazy as _

from panoptes.core.models import Location, Workstation

import re

class AccountListField(models.CharField):
	"""
	A field that accepts a character-separated list of account names and renders
	them in python a tuple ordered by the account name.
	"""

	_separators = [' ', ',']

	def __init__(self, *args, **kwargs):
		"""
		Accept an additional `separators` kwarg that allows a user to extend the
		separators than can be used.
		"""

		defaults = {'max_length': 255}
		defaults.update(kwargs)

		super(AccountListField, self).__init__(*args, **defaults)

		if 'separators' in kwargs:
			self._separators = kwargs['separators']

	def get_internal_type(self):
		return 'CharField'

	def to_python(self, value):
		"""Return the account names as a tuple."""
		return tuple(sorted(re.split(r'[%s]+' % "".join(self._separators), re.sub(r'\s{2,}', r' ', value))))

class AccountFilterManager(models.Manager):
	"""Custom manager for the AccountFilter model."""

	def is_user_loggable(self, username, mac_address):
		"""
		Return True if the user whose username is provided in the string
		`username` should have their usage sessions for the workstation whose
		MAC address is given in the `mac_address` string.
		"""
	
		try:
			location = Workstation.objects.get(mac_address=mac_address).location
		except Workstation.DoesNotExist:
			return False
		else:
			if username:
				return all([
					account_filter.user_is_trackable(username)
					for account_filter in self.filter(location=location)])
			else:
				return True

class AccountFilter(models.Model):
	"""
	A filter controlling which reported session information will be tracked,
	depending upon the name of the user reported with it.
	"""

	objects  = AccountFilterManager()

	location = models.ForeignKey(Location, verbose_name="For machines in the")
	include  = AccountListField(verbose_name=_("include users"), help_text=_("only track sessions from these users"), blank=True, null=True)
	exclude  = AccountListField(verbose_name=_("exclude users"), help_text=_("track sessions from any users except these"), blank=True, null=True)

	class Meta:

		app_label = "panoptes"
		verbose_name = _("user account filter")
		verbose_name_plural = _("user account filters")

	def __unicode__(self):
		return self.location.__unicode__()

	def user_is_trackable(self, username):
		"""
		Return True if the user provided in the `username` string should have
		their session tracked.
		"""
		include_list = self.include or []
		exclude_list = self.exclude or []
		return username in include_list or username not in exclude_list
