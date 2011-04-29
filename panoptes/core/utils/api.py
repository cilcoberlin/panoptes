
from piston.resource import Resource
from piston.decorator import decorator
from piston.utils import FormValidationError

class CSRFExemptResource(Resource):
	"""A custom Piston resource that is exempt from CSRF checks."""

	def __init__(self, *args, **kwargs):
		super(CSRFExemptResource, self).__init__(*args, **kwargs)
		self.csrf_exempt = True

def validate(v_form, operation='POST'):
	@decorator
	def wrap(f, self, request, *a, **kwa):
		form = v_form(getattr(request, operation))
		if form.is_valid():
			setattr(request, 'form', form)
			return f(self, request, *a, **kwa)
		else:
			raise FormValidationError(form)
	return wrap

