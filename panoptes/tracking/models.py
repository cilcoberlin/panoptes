
from django.db import models
from django.utils.translation import ugettext_lazy as _

from panoptes.core.models import Location
from panoptes.tracking.model_fields import AccountListField

class AccountFilterManager(models.Manager):
	"""Custom manager for the AccountFilter model."""

	def _lc_name_list(self, names):
		"""Return a version of the given names list with every name in lowercase."""
		return [name.lower() for name in names]

	def is_user_loggable(self, username, workstation):
		"""Return True if the user at the workstation should be tracked.

		This works by making a master exclude and include list from the lists of all
		account filters set up for the location of the workstation.  Precedence is
		given to the include filter, so if an include list exists and the user is in
		it, they will be tracked, even if they appear in the exclude list.

		Arguments:
		username -- a string of the logged-in user's name
		workstation -- a Workstation instance reporting the session

		Returns: a boolean of whether the user should be tracked

		"""

		if not workstation:
			return False
		if username:
			username = username.lower()
			all_excludes = []
			all_includes = []
			for account_filter in self.filter(location=workstation.location):
				all_excludes.extend(account_filter.exclude or [])
				all_includes.extend(account_filter.include or [])
			if username in self._lc_name_list(all_excludes):
				return False
			if all_includes and username not in self._lc_name_list(all_includes):
				return False
		return True

class AccountFilter(models.Model):
	"""
	A filter controlling which reported session information will be tracked,
	depending upon the name of the user reported with it.
	"""

	_USER_NAME_SEPARATOR = ", "

	objects  = AccountFilterManager()

	location = models.ForeignKey(Location, verbose_name=_("for machines in the"))
	include  = AccountListField(verbose_name=_("include users"), help_text=_("only track sessions from these users"), blank=True, null=True)
	exclude  = AccountListField(verbose_name=_("exclude users"), help_text=_("track sessions from any users except these"), blank=True, null=True)

	class Meta:

		app_label = "panoptes"
		verbose_name = _("user account filter")
		verbose_name_plural = _("user account filters")

	def __unicode__(self):
		return self.location.__unicode__()

	def _join_user_names(self, names):
		"""Return the names in the iterable `names` as a joined string."""
		return self._USER_NAME_SEPARATOR.join(names)

	def include_users(self):
		return self._join_user_names(self.include)
	include_users.short_description = _("include users")

	def exclude_users(self):
		return self._join_user_names(self.exclude)
	exclude_users.short_description = _("exclude users")

