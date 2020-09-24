import uuid

import sqlalchemy as sa
import sqlalchemy_mixins
from sqlalchemy import or_
from sqlalchemy.dialects.postgresql import UUID

from app.dto import InternalUserDTO
from app.models.base_model import BaseModel


class ACL(BaseModel):
    __tablename__ = "acls"
    __table_args__ = (
        sa.UniqueConstraint(
            "granted_provider_uuid",
            "granted_user_uuid",
            "collection_uuid",
            "item_uuid",
            "access",
        ),
        sa.CheckConstraint(
            "((granted_provider_uuid is not null)::integer + (granted_user_uuid is not null)::integer) = 1",
            name="check_granted",
        ),
        sa.CheckConstraint(
            "((item_uuid is not null)::integer + (collection_uuid is not null)::integer) = 1",
            name="check_granted_object",
        ),
    )
    uuid = sa.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    provider_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("providers.uuid", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    granted_provider_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("providers.uuid", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    granted_user_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("users.uuid", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    collection_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("collections.uuid", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    item_uuid = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("items.uuid", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )

    access = sa.Column(sa.Enum("read", "write", name="permission"), nullable=False)

    @classmethod
    def accessable_query(cls, user: InternalUserDTO):
        user_uuid = user.uuid
        provider_uuid = user.provider_uuid
        q = cls.session.query(cls.uuid).filter(
            or_(
                cls.provider_uuid == provider_uuid,
                cls.granted_provider_uuid == provider_uuid,
                cls.granted_user_uuid == user_uuid,
            )
        )
        return q

    # TODO: Investigate if this should be done with JOIN instead of SUBQUERY
    @classmethod
    def find_accessable(cls, user: InternalUserDTO):
        readable_sq = cls.accessable_query(user).subquery()
        q = cls.query.filter(cls.uuid.in_(readable_sq))
        res = q.all()

        return res

    # TODO: Investigate if this should be done with JOIN instead of SUBQUERY
    @classmethod
    def find_accessable_or_fail(cls, user: InternalUserDTO, acl_uuid):
        readable_sq = cls.accessable_query(user).subquery()
        q = cls.query.filter(cls.uuid.in_(readable_sq))
        q = q.filter(cls.uuid == acl_uuid)
        res = q.first()
        if res is None:
            raise sqlalchemy_mixins.ModelNotFoundError

        return res
