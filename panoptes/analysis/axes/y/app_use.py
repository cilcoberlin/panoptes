
from django.utils.translation import ugettext_lazy as _, ungettext

from panoptes.analysis.axes.y import YAxis
from panoptes.core.models import ApplicationUse

class Axis(YAxis):
	"""A y-axis of the number of sessions that used an application."""

	name = _("application usage count")
	slug = "app-use"

	def application_values(self, x_values, sessions, filters):
		"""
		Return a list of the number of sessions that used the  Application instance
		contained in `x_values`.
		"""

		app_uses = ApplicationUse.objects.all_for_filters(
			location=filters.location,
			start_date=filters.start_date,
			end_date=filters.end_date,
			start_time=filters.start_time,
			end_time=filters.end_time,
			weekdays=filters.weekdays
		)

		by_app = dict(zip(x_values, [0] * len(x_values)))
		for app_use in app_uses.select_related('application').iterator():
			by_app[app_use.application] += 1

		return [by_app[app] for app in x_values]

	def workstation_values(self, x_values, sessions, filters):
		"""
		Return a list of the number of times the Application instance
		specified in `filters` was used per workstation.

		This method will only return valid data if an x-value detail has been
		specified in the filters passed.  If no single application has been passed, a
		zero is provided as the value of every y-value.
		"""
		app = filters.x_detail
		if not app:
			return [0] * len(x_values)
		else:
			return [sessions.filter(workstation=workstation, apps_used__application=app).count()
				for workstation in x_values]

	def render_value(self, value):
		"""
		Render the integer of the number of times an application was used
		contained in value as a stringified integer.
		"""
		return unicode(value)

	def verbose_value(self, value):
		"""Render the usage count as a verbose string."""
		return ungettext("%(count)d use", "%(count)d uses", value) % {'count': value}

	def serialize_value(self, value):
		"""Serialize the use count as a stringified number."""
		return unicode(value)

	def deserialize_value(self, value):
		"""Deserialize the stringified integer as an integer."""
		return int(value)
