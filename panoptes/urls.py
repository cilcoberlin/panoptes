
from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

api_v1_patterns = patterns('',
	(r'^tracking/', include('panoptes.tracking.api.urls'))
)

api_version_patterns = patterns('',
	(r'^1/', include(api_v1_patterns))
)

api_patterns = patterns('',
	(r'^versions/', include(api_version_patterns))
)

account_patterns = patterns('django.contrib.auth.views',
	url(r'login/$', 'login', {'template_name': 'panoptes/accounts/login.html'}, 'login'),
	url(r'logout/$', 'logout', {'template_name': 'panoptes/accounts/logout.html'}, 'logout')
)

urlpatterns = patterns('',

	(r'^accounts/', include(account_patterns)),
	(r'^analysis/', include('panoptes.analysis.urls')),
	(r'^api/', include(api_patterns)),
	
	#  Redirect an index view to the analysis index
	url(r'^/?$', redirect_to, {'url': 'analysis/', 'permanent': False}),
	
)
