
from django.conf.urls.defaults import include, patterns, url

from panoptes.core.utils.api import CSRFExemptResource
from panoptes.tracking.api.handlers import *

location_patterns = patterns('',
	url(r'^activity/$', CSRFExemptResource(handler=LocationActivityHandler)),
	url(r'^activity/from/(?P<start_dt>[^\/]+)/to/(?P<end_dt>[^\/]+)/$', CSRFExemptResource(handler=LocationActivityHandler)),
	url(r'^current-usage/$', CSRFExemptResource(handler=CurrentUsageHandler)),
	url(r'^info/$', CSRFExemptResource(handler=LocationInfoHandler))
)

urlpatterns = patterns('',
	(r'^location/(?P<location_slug>[^\/]+)/', include(location_patterns)),
	url(r'^sessions/$', CSRFExemptResource(handler=SessionHandler))
)
