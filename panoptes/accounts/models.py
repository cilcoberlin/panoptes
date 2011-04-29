
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from panoptes.core.models import Location
from panoptes.analysis.model_fields import LensField
from panoptes.analysis.lenses import get_default_lens
import panoptes.settings as _settings

class UserProfileManager(models.Manager):
	"""Custom manager for the UserProfile model."""

	def create_for_user(self, user):
		"""Create a profile for the given user if one doesn't already exist."""

		try:
			profile = self.get(user=user)
		except UserProfile.DoesNotExist:
			profile = self.create(
								user=user,
								default_location=Location.objects.get_default(),
								default_lens=get_default_lens().slug)

		return profile

class UserProfile(models.Model):
	"""A user profile for storing preferences."""

	objects = UserProfileManager()

	user                = models.OneToOneField(User, verbose_name=_("user"))
	default_location    = models.ForeignKey(Location, verbose_name=_("default location"))
	default_lens        = LensField(verbose_name=_("default data view"))
	default_recent_days = models.PositiveSmallIntegerField(verbose_name=_("default recent days to show"), default=_settings.DEFAULT_ANALYSIS_RECENT_DAYS)

	class Meta:

		app_label = "panoptes"
		verbose_name = _("user profile")
		verbose_name_plural = _("user profiles")

	def __unicode__(self):
		return self.user.get_full_name()

	def user_full_name(self):
		return self.user.get_full_name()
	user_full_name.short_description = _("user")

	def default_lens_name(self):
		return self.default_lens.make_title()
	default_lens_name.short_description = _("default lens")

def _create_profile_on_user_update(sender, **kwargs):
	"""Possibly create a profile for a newly created user."""
	UserProfile.objects.create_for_user(kwargs['instance'])
post_save.connect(_create_profile_on_user_update, sender=User)
