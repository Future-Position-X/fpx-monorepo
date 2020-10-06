"""Initial migration

Revision ID: 0d059bac5d15
Revises:
Create Date: 2020-06-08 14:52:02.878497

"""
import os

import bcrypt
import geoalchemy2
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm.session import Session

from alembic import op

# revision identifiers, used by Alembic.
from app.core.security import create_access_token
from app.models import Provider, User
from app.models.base_model import BaseModel

revision = "0d059bac5d15"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.create_table(
        "providers",
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "revision", sa.Integer(), server_default=sa.text("1"), nullable=False
        ),
        sa.Column(
            "uuid",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("name", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_table(
        "collections",
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "revision", sa.Integer(), server_default=sa.text("1"), nullable=False
        ),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=True),
        sa.Column("provider_uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["provider_uuid"], ["providers.uuid"]),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("provider_uuid", "name"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index(
        op.f("ix_collections_provider_uuid"),
        "collections",
        ["provider_uuid"],
        unique=False,
    )
    op.create_table(
        "users",
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "revision", sa.Integer(), server_default=sa.text("1"), nullable=False
        ),
        sa.Column(
            "uuid",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("email", sa.Text(), nullable=True),
        sa.Column("password", sa.Text(), nullable=True),
        sa.Column("provider_uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["provider_uuid"], ["providers.uuid"]),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index(
        op.f("ix_users_provider_uuid"), "users", ["provider_uuid"], unique=False
    )
    op.create_table(
        "items",
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "revision", sa.Integer(), server_default=sa.text("1"), nullable=False
        ),
        sa.Column(
            "uuid",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "geometry",
            geoalchemy2.types.Geometry(from_text="ST_GeomFromEWKT", name="geometry"),
            nullable=True,
        ),
        sa.Column("properties", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("collection_uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider_uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["collection_uuid"], ["collections.uuid"]),
        sa.ForeignKeyConstraint(["provider_uuid"], ["providers.uuid"]),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index(
        op.f("ix_items_collection_uuid"), "items", ["collection_uuid"], unique=False
    )
    op.create_index(
        op.f("ix_items_provider_uuid"), "items", ["provider_uuid"], unique=False
    )

    seed_initial_user()
    # ### end Alembic commands ###


def seed_initial_user():
    session = Session(bind=op.get_bind())
    BaseModel.set_session(session)
    provider = Provider.create(name="fpx")
    password = None
    try:
        password = os.environ["FIRST_SUPERUSER_PASSWORD"].encode("utf-8")
    except KeyError:
        print("You must set env variable USER_PASSWORD!!!")
        exit()

    user = User.create(
        email=os.environ.get("FIRST_SUPERUSER", "info@fpx.se"),
        provider_uuid=provider.uuid,
        password=bcrypt.hashpw(password, bcrypt.gensalt()).decode("utf-8"),
    )
    print("Your master user token: " + create_access_token(str(user.uuid)))


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_items_provider_uuid"), table_name="items")
    op.drop_index(op.f("ix_items_collection_uuid"), table_name="items")
    op.drop_table("items")
    op.drop_index(op.f("ix_users_provider_uuid"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_collections_provider_uuid"), table_name="collections")
    op.drop_table("collections")
    op.drop_table("providers")
    # ### end Alembic commands ###
