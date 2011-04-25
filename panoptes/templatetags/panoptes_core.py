
from django import template

register = template.Library()

@register.inclusion_tag("panoptes/core/form_field.html")
@register.simple_tag
def form_field(field):
	"""Render the given form field."""
	return {'field': field}

@register.inclusion_tag("panoptes/core/form_field.html")
@register.simple_tag
def multi_form_field(field):
	"""Render the given form field, which uses a multipart widget."""
	return {'field': field, 'is_multi': True}