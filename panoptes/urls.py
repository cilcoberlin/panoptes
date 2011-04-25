
from django.conf.urls.defaults import *

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

	(r'^analysis/', include('panoptes.analysis.urls')),
	(r'^api/', include(api_patterns))
)
