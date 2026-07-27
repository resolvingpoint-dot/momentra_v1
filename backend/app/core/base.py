from app.domains.users.models import Base

# Import all models so Alembic and the ORM registry discover them
from app.domains.preferences.models import UserPreferencesModel  # noqa: F401
from app.domains.module_states.models import ModuleStateModel  # noqa: F401
from app.domains.moments.models import MomentModel, MomentMediaModel  # noqa: F401
from app.domains.auth.models import AuthRefreshSessionModel  # noqa: F401

# Momentra domain models (personal / group / business / circle / life360).
# Importing the modules registers every model on the shared Base so that
# cross-domain relationships resolve at mapper-configuration time.
from app.domains.personal import models as personal_models  # noqa: F401
from app.domains.group import models as group_models  # noqa: F401
from app.domains.business import models as business_models  # noqa: F401
from app.domains.circle import models as circle_models  # noqa: F401
from app.domains.life360 import models as life360_models  # noqa: F401
from app.shared.events import models as event_models  # noqa: F401

__all__ = ["Base"]
