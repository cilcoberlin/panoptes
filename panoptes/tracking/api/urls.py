
from django.conf.urls.defaults import *

from panoptes.core.utils.api import CSRFExemptResource
from panoptes.tracking.api.handlers import LocationHandler, SessionHandler

urlpatterns = patterns('',
	url(r'^locations/(?P<slug>[^\/]+)/$', CSRFExemptResource(handler=LocationHandler)),
	url(r'^sessions/$', CSRFExemptResource(handler=SessionHandler))
)
