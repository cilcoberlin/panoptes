
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

urlpatterns = patterns('',

	(r'^accounts/', include('panoptes.accounts.urls')),
	(r'^analysis/', include('panoptes.analysis.urls')),
	(r'^api/', include(api_patterns)),

	#  Redirect an index view to the analysis index
	url(r'^/?$', redirect_to, {'url': 'analysis/', 'permanent': False}),

)
