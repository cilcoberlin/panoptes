
from django.template.loader import render_to_string

from cilcdjango.core.decorators import ajax_view
from cilcdjango.core.shortcuts import get_object_or_ajax_error

from panoptes.core.models import Location

@ajax_view
def refresh_layout(request, location_id=0, x_filter=None, y_filter=None, start=None, end=None):#, overlayFilter=None, overlayDatum=None):
	"""
	Return markup for the layout of the Location instance whose primary key is
	given in `location_id`, with an optional overlay of the the dataset
	referenced by the various filters.
	"""

	location = get_object_or_ajax_error(Location, pk=location_id)

	return {
		'markup': {
			'layout': render_to_string('panoptes/core/layout.html', {'location': location })
		}
	}
