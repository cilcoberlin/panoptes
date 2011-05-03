
from panoptes.core.utils.pages import Page

def error_404(request):
	"""Handle a 404 not found error."""
	page = Page(request)
	return page.render("panoptes/core/errors/404.html")

def error_500(request):
	"""Handle a 500 server error."""
	page = Page(request)
	return page.render("panoptes/core/errors/500.html")
