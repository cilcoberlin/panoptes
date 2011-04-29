
from django import template
from django.template.defaultfilters import escapejs
from django.template.loader import render_to_string
from django.utils.translation import ugettext

from panoptes.analysis import FilteredSessions
from panoptes.core.utils.constants import weekday_name

import re

register = template.Library()

def _make_filter_context(filters):
	"""Render the context used to render the given filters."""

	if not isinstance(filters, FilteredSessions):
		raise template.TemplateSyntaxError(ugettext("Argument 'filters' must be a FilteredSessions instance"))

	#  Provide capitalized weekday names to the template
	weekdays = []
	for weekday in filters.weekdays:
		weekdays.append(weekday_name(weekday).title())

	return {
		'location':   filters.location,
		'start_date': filters.start_date,
		'end_date':   filters.end_date,
		'start_time': filters.start_time,
		'end_time':   filters.end_time,
		'weekdays':   weekdays,
		'x_axis':     filters.x_axis.name,
		'y_axis':     filters.y_axis.name
	}

@register.inclusion_tag("panoptes/analysis/filters_simple.html")
@register.simple_tag
def simple_filters(filters):
	return _make_filter_context(filters)

@register.inclusion_tag("panoptes/analysis/filters_verbose.html")
@register.simple_tag
def verbose_filters(filters):
	return _make_filter_context(filters)

@register.inclusion_tag("panoptes/analysis/lens_form.html")
@register.simple_tag
def lens_form(form):
	"""Render the lens form using the passed Form instance."""
	return {
		'lens_form': form
	}

@register.simple_tag
def loading_fragment():
	"""Render the loading fragment with quotes escaped."""
	loading = render_to_string("panoptes/analysis/loading.html")
	return re.sub(r'[\n\r\t]', '', escapejs(loading))
