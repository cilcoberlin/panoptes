
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from panoptes.analysis.forms import SessionFilterForm
from panoptes.core.models import Location
from panoptes.core.utils.ajax import AjaxError, ajax_view
from panoptes.core.utils.pages import Page

@login_required
def index(request):
	"""Redirect to the default location's index, if one exists."""
	default_location = get_object_or_404(Location, default=True)
	return HttpResponseRedirect(
		reverse("analysis", kwargs={'location_slug': default_location.slug}))

@login_required
def analysis(request, location_slug=None):
	"""Base page for the analysis of tracked sessions."""

	page = Page(request)
	page.add_render_args({'location': get_object_or_404(Location, slug=location_slug)})

	#  Use default data determined by the user's profile if the form has no POST
	#  data given to it
	if request.POST:
		form_data = request.POST
		profile = None
	else:
		form_data = None
		profile = request.user.get_profile()

	filter_form = SessionFilterForm(form_data, profile=profile)
	if filter_form.is_valid():
		filters = filter_form.as_filtered_sessions()
		Lens = filter_form.cleaned_data['lens']
		lens = Lens(filters)
		page.add_render_args({
							'filters': filters,
							'lens_media': lens.provide_media(),
							'panels': lens.ordered_panels()})

	page.add_render_args({'filter_form': filter_form})
	return page.render("panoptes/analysis/base.html")

@ajax_view
def update_supporting_panels(request):
	"""Return markup for the layout and events panel.

	In addition to the normal filter data, this also receives the integer index of
	an x-value to use to restrict the data, which is contained in the POST data.
	"""

	if request.POST:
		filter_form = SessionFilterForm(request.POST)
		if filter_form.is_valid():
			Lens = filter_form.cleaned_data['lens']
			lens = Lens(filter_form.as_filtered_sessions())

			#  Provide the rendered markup for the panels in a dict keyed by the slug of
			#  the panel, excepting the primary panel
			panel_markup = {}
			for panel in lens.secondary_panels():
				panel_markup[panel.slug] = panel.render()
			return {
				'markup': {
					'panels': panel_markup
				}
			}
		else:
			raise AjaxError
	else:
		raise AjaxError
