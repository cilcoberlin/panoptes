
from django.contrib import admin

from panoptes.core.models import *

class LayoutCellInline(admin.TabularInline):

	model = LayoutCell

class MACAddressInline(admin.TabularInline):

	model = MACAddress

class ApplicationAdmin(admin.ModelAdmin):

	list_display = ('name',)
	ordering = ('name',)

class ApplicationUseAdmin(admin.ModelAdmin):

	list_display = ('application', 'session', 'duration')
	ordering = ('session__start_date',)

class LayoutCellAdmin(admin.ModelAdmin):

	list_display = ('row', 'workstation', 'human_order')
	ordering = ('row__order',)

class LayoutRowAdmin(admin.ModelAdmin):

	inlines = [LayoutCellInline]
	list_display = ('location', 'human_order')
	ordering = ('order',)

class LocationAdmin(admin.ModelAdmin):

	list_display = ('name', 'earliest_opening', 'latest_closing', 'timezone', 'default')
	ordering = ('name',)

class OSTypeAdmin(admin.ModelAdmin):

	list_display = ('name', 'version')
	ordering = ('name',)

class ReportedApplicationAdmin(admin.ModelAdmin):

	list_display = ('name', 'application', 'location')
	ordering = ('name',)

class SessionAdmin(admin.ModelAdmin):

	list_display = ('workstation', 'start', 'end', 'os_type')
	ordering = ('-start',)

class WorkstationAdmin(admin.ModelAdmin):

	inlines = [MACAddressInline]
	list_display = ('name', 'location', 'track')
	ordering = ('name',)

admin.site.register(Application, ApplicationAdmin)
admin.site.register(ApplicationUse, ApplicationUseAdmin)
admin.site.register(LayoutCell, LayoutCellAdmin)
admin.site.register(LayoutRow, LayoutRowAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(OSType, OSTypeAdmin)
admin.site.register(ReportedApplication, ReportedApplicationAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Workstation, WorkstationAdmin)
