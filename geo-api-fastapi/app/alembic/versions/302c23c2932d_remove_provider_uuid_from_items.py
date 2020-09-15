"""Remove provider_uuid from items

Revision ID: 302c23c2932d
Revises: 0d059bac5d15
Create Date: 2020-06-11 10:50:31.533636

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "302c23c2932d"
down_revision = "0d059bac5d15"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("ix_items_provider_uuid", table_name="items")
    op.drop_constraint("items_provider_uuid_fkey", "items", type_="foreignkey")
    op.drop_column("items", "provider_uuid")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "items",
        sa.Column(
            "provider_uuid", postgresql.UUID(), autoincrement=False, nullable=False
        ),
    )
    op.create_foreign_key(
        "items_provider_uuid_fkey", "items", "providers", ["provider_uuid"], ["uuid"]
    )
    op.create_index("ix_items_provider_uuid", "items", ["provider_uuid"], unique=False)
    # ### end Alembic commands ###
