
from django import forms
from django.utils.translation import ugettext_lazy as _

from panoptes.analysis.axes import axis_factory
from panoptes.analysis.panels import create_panel

def lens_factory(slug):
	"""Return a Lens class given a slug."""
	return LensBase.registered_lenses.get(slug, None)

def get_all_lenses():
	"""Return a list of all available lenses, ordered by their y-axis slug."""
	lenses = LensBase.registered_lenses.values()
	return sorted(lenses, key=lambda l: l.y_axis_slug)

def get_default_lens():
	"""Return the default lens' class."""
	for lens in get_all_lenses():
		if lens.default:
			return lens
	raise ValueError("You must declare one Lens to be the default")

class LensBase(type):
	"""Custom metaclass for lenses that maintains a repository of all lenses."""

	registered_lenses = {}
	_has_default = False

	def __init__(self, name, bases, attrs):
		"""Update our registry of declared lenses, keyed by the x- and y-axis."""

		super(LensBase, self).__init__(name, bases, attrs)

		if name == 'BaseLens':
			return

		if not attrs['x_axis_slug'] or not attrs['y_axis_slug']:
			raise TypeError("You must define an x- and a y-axis slug for each Lens")

		is_default = attrs.get('default', False)
		if is_default:
			if not LensBase._has_default:
				LensBase._has_default = True
			else:
				raise TypeError("You cannot define more than one default Lens")

		if not attrs['slug']:
			raise TypeError("You must define a slug for the %s Lens" % name)
		if attrs['slug'] in LensBase.registered_lenses:
			raise TypeError("You cannot have more than one Lens with the slug %s" % attrs['slug'])

		LensBase.registered_lenses[attrs['slug']] = self
		self.resolve_axes()

class BaseLens(object):
	"""
	An abstract lens through which data can be viewed.

	A child lens must define a few key attributes, which are as follows:

	  x_axis - An XAxis instance used for the x-axis.

	  y_axis - A YAxis instance used for the y-axis.

	"""

	__metaclass__ = LensBase

	slug = None

	default = False

	panels = ()

	x_axis_slug = None
	y_axis_slug = None

	def __init__(self, sessions):
		"""Create a lens for viewing the given FilteredSessions instance."""

		if not self.panels:
			raise TypeError("The %(lens)s lens must define at least one panel" % {'lens': self.__class__.name})

		self.sessions = sessions
		self._configure_panels()

	@classmethod
	def make_title(self):
		"""The verbose name of the lens, built using its x- and y-axis."""
		return _("%(y)s per %(x)s") % {
			'y': self.y_axis.name.title(),
			'x': self.x_axis.name.title()
		}

	@classmethod
	def resolve_axes(self):
		"""Resolve the axis slugs to XAxis and YAxis instances."""
		self.x_axis = axis_factory(self.x_axis_slug, x=True)
		self.y_axis = axis_factory(self.y_axis_slug, y=True)

	def _configure_panels(self):
		"""Resolve the panel slugs to Panel instances."""

		self._panels = []

		for i, panel in enumerate(self.panels):
			self._panels.append(create_panel(i, panel[0], self.sessions, panel[1]))

	def provide_media(self):
		"""Return a Django media object of all JavaScript and CSS used by the lens."""

		media = forms.Media(js=(), css={})
		for panel in self._panels:
			media += panel.provide_media()
		return media

	def ordered_panels(self):
		"""Return an ordered list of all panels used by the lens."""
		return self._panels

	def secondary_panels(self):
		"""Return a list of all secondary panels, which are all except the first."""
		return self._panels[1:]

	@property
	def title(self):
		"""The verbose title of the lens."""
		return self.__class__.make_title()
