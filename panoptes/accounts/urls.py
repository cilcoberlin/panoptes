
from django.conf.urls.defaults import patterns, url

auth_patterns = patterns('django.contrib.auth.views',
	url(r'login/$', 'login', {'template_name': 'panoptes/accounts/login.html'}, 'login'),
	url(r'logout/$', 'logout_then_login', name='logout')
)

pref_patterns = patterns('panoptes.accounts.views',
	url(r'^preferences/$', 'preferences', name="account-preferences"),
)

urlpatterns = auth_patterns + pref_patterns
