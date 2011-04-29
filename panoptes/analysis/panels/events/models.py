
from django.db import models
from django.utils.translation import ugettext_lazy as _

from panoptes.core.models import Location

class LocationCalendarManager(models.Manager):
	"""Custom manager for the LocationCalendar model."""

	def all_for_location(self, location):
		"""Return a queryset of all LocationCalendar instances for the location.

		Arguments:
		location -- a Location instance

		"""
		return location.location_calendars.all().order_by('order')

class LocationCalendar(models.Model):
	"""A Google Calendar used to schedule events in a location or related rooms."""

	objects     = LocationCalendarManager()

	location    = models.ForeignKey(Location, verbose_name=_("location"), related_name="location_calendars")
	name        = models.CharField(max_length=50, verbose_name=_("name"))
	calendar_id = models.CharField(max_length=100, verbose_name=_("Google Calendar ID"))
	order       = models.PositiveIntegerField(verbose_name=_("display order"))

	class Meta:

		app_label = "panoptes"
		verbose_name = _("location calendar")
		verbose_name_plural = _("location calendars")

	def __unicode__(self):
		return self.name
