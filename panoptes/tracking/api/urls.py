
from django.conf.urls.defaults import include, patterns, url

from panoptes.core.utils.api import CSRFExemptResource
from panoptes.tracking.api.handlers import LocationActivityHandler, LocationInfoHandler, SessionHandler

location_patterns = patterns('',
	url(r'^info/$', CSRFExemptResource(handler=LocationInfoHandler)),
	url(r'^activity/$', CSRFExemptResource(handler=LocationActivityHandler)),
	url(r'^activity/from/(?P<start_dt>[^\/]+)/to/(?P<end_dt>[^\/]+)/$', CSRFExemptResource(handler=LocationActivityHandler)),
)

urlpatterns = patterns('',
	(r'^location/(?P<location_slug>[^\/]+)/', include(location_patterns)),
	url(r'^sessions/$', CSRFExemptResource(handler=SessionHandler))
)
