
from django.utils.dates import WEEKDAYS_ABBR as _WEEKDAYS_ABBR, WEEKDAYS as _WEEKDAYS
from django.utils.translation import ugettext_lazy as _

def weekday_name(iso_number):
	"""Return the weekday name for the given ISO weekday number or a blank string."""
	try:
		return _WEEKDAYS[iso_number - 1]
	except IndexError:
		return u""

WEEKDAYS = tuple([_WEEKDAYS[i] for i in sorted(_WEEKDAYS.keys())])
WEEKDAYS_ABBR = tuple([_WEEKDAYS_ABBR[i] for i in sorted(_WEEKDAYS_ABBR.keys())])
WEEKDAYS_SINGLE_LETTER = (_('M'), _('T'), _('W'), _('R'), _('F'), _('S'), _('U'))


