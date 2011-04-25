
from django.conf.urls.defaults import *

ajax_patterns = patterns('panoptes.analysis.mapping.views',
	url(r'^refresh/', 'refresh_layout', name="refresh-layout-overlay"),
)

urlpatterns = patterns('',
	(r'^remote/', include(ajax_patterns))
)
