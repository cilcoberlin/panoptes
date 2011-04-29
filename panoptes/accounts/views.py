
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from cilcdjango.core.pages import DjangoPage

from panoptes.accounts.forms import UserPreferencesForm

_PREFS_UPDATED_KEY = "preferences_updated"

@login_required
def preferences(request):
	"""A view that allows the user to edit their preferences."""

	page = DjangoPage(request)
	profile = request.user.get_profile()

	if request.POST:
		post_data = request.POST.copy()
		post_data['user'] = request.user.pk
		prefs_form = UserPreferencesForm(post_data, instance=profile)
		if prefs_form.is_valid():
			prefs_form.save()
			request.session[_PREFS_UPDATED_KEY] = True
			return HttpResponseRedirect(reverse("account-preferences"))
	else:
		prefs_form = UserPreferencesForm(instance=profile)

	if request.session.get(_PREFS_UPDATED_KEY, False):
		page.add_render_args({'updated': True})
		del request.session[_PREFS_UPDATED_KEY]

	page.add_render_args({'form': prefs_form})
	return page.render("panoptes/accounts/preferences.html")
