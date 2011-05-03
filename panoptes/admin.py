
#  This import exists to allow many of the analysis classes, which use a
#  metaclass registry, to register themselves before the admin autodiscover
#  starts looking for admin modules.  If it is not here, things like the lens
#  choice field crash, since the lenses have yet to be initialized.
import panoptes.models

import panoptes.accounts.admin
import panoptes.analysis.admin
import panoptes.core.admin
import panoptes.tracking.admin
