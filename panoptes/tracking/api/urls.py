
from django.conf.urls.defaults import *

from panoptes.core.utils.api import CSRFExemptResource
from panoptes.tracking.api.handlers import SessionHandler

urlpatterns = patterns('',
	url(r'^sessions/$', CSRFExemptResource(handler=SessionHandler))
)
