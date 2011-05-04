
from django.contrib import admin

from panoptes.tracking.models import AccountFilter

class AccountFilterAdmin(admin.ModelAdmin):

	list_display = ('location', 'include_users', 'exclude_users')
	ordering = ('location',)

admin.site.register(AccountFilter, AccountFilterAdmin)
