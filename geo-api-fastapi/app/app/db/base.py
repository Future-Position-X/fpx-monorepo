# Import all the models, so that Base has them before being
# imported by Alembic
from app.models.item import Item  # noqa
from app.models.user import User  # noqa
from app.models.provider import Provider  # noqa
from app.models.collection import Collection  # noqa
from app.models.acl import ACL  # noqa
