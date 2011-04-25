
from django.contrib import admin

from panoptes.tracking.models import AccountFilter

class AccountFilterAdmin(admin.ModelAdmin):

	list_display = ('location', 'include', 'exclude')
	ordering = ('location',)

admin.site.register(AccountFilter, AccountFilterAdmin)
