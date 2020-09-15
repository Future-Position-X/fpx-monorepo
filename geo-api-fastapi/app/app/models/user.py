# from typing import TYPE_CHECKING
#
# from sqlalchemy import Boolean, Column, Integer, String
# from sqlalchemy.orm import relationship
#
# from app.db.base_class import Base
#
# if TYPE_CHECKING:
#     from .item import Item  # noqa: F401
#
#
# class User(Base):
#     id = Column(Integer, primary_key=True, index=True)
#     full_name = Column(String, index=True)
#     email = Column(String, unique=True, index=True, nullable=False)
#     hashed_password = Column(String, nullable=False)
#     is_active = Column(Boolean(), default=True)
#     is_superuser = Column(Boolean(), default=False)
#     items = relationship("Item", back_populates="owner")
from sqlalchemy.dialects.postgresql import UUID


from app.models import BaseModel
import sqlalchemy as sa


class User(BaseModel):
    __tablename__ = "users"

    uuid = sa.Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
        unique=True,
        nullable=False,
    )
    email = sa.Column(sa.Text(), unique=True)
    password = sa.Column(sa.Text())

    provider_uuid = sa.Column(
        UUID(as_uuid=True), sa.ForeignKey("providers.uuid"), index=True, nullable=False
    )
