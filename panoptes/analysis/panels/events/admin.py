
from django.contrib import admin

from panoptes.analysis.panels.events.models import LocationCalendar

class LocationCalendarAdmin(admin.ModelAdmin):

	list_display = ('name', 'location', 'calendar_id')
	ordering = ('location', 'order')

admin.site.register(LocationCalendar, LocationCalendarAdmin)
