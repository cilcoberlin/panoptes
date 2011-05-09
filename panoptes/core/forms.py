
from django import forms
from django.utils.translation import ugettext_lazy as _

from panoptes.core.models import ReportedApplication

class ReportedApplicationForm(forms.ModelForm):

	def clean(self, *args, **kwargs):
		"""
		Check that the reported application name is case-insensitively unique for the
		chosen location.
		"""

		location = self.cleaned_data.get('location', None)
		if location:
			app_name = self.cleaned_data.get('name', u"")
			named_apps = ReportedApplication.objects.filter(name__iexact=app_name, location=location)
			if self.instance.pk:
				named_apps = named_apps.exclude(pk=self.instance.pk)
			if named_apps.exists():
				raise forms.ValidationError(_("An application reported as %(app)s already exists") % {'app': app_name})

		return self.cleaned_data
