
from django.contrib import admin

from panoptes.accounts.forms import UserPreferencesForm
from panoptes.accounts.models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):

	form = UserPreferencesForm
	list_display = ('user_full_name', 'default_location', 'default_lens_name', 'default_recent_days')
	ordering = ('user__last_name', 'user__first_name')

admin.site.register(UserProfile, UserProfileAdmin)
