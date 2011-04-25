
from django.conf.urls.defaults import *

location_patterns = patterns('panoptes.analysis.views',
	url(r'^/$', 'analysis', name="analysis"),
)

lens_patterns = patterns('panoptes.analysis.views',
	url(r'^update-panels/$', 'update_supporting_panels', name="update-supporting-panels")
)

urlpatterns = patterns('',

	url(r'^/?$', 'panoptes.analysis.views.index', name="analysis-index"),

	(r'^location/(?P<location_slug>[^/]+)', include(location_patterns)),
	(r'^lenses/', include(lens_patterns))
)
