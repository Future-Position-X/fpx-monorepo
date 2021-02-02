"""delete cascade

Revision ID: 4ba7b628888b
Revises: cb23a78d2118
Create Date: 2021-02-02 07:45:30.238995

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "4ba7b628888b"
down_revision = "cb23a78d2118"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("items_collection_uuid_fkey", "items", type_="foreignkey")
    op.create_foreign_key(
        None, "items", "collections", ["collection_uuid"], ["uuid"], ondelete="CASCADE"
    )
    op.drop_constraint("metrics_series_uuid_fkey", "metrics", type_="foreignkey")
    op.create_foreign_key(
        None, "metrics", "series", ["series_uuid"], ["uuid"], ondelete="CASCADE"
    )
    op.drop_constraint("series_item_uuid_fkey", "series", type_="foreignkey")
    op.create_foreign_key(
        None, "series", "items", ["item_uuid"], ["uuid"], ondelete="CASCADE"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "series", type_="foreignkey")
    op.create_foreign_key(
        "series_item_uuid_fkey", "series", "items", ["item_uuid"], ["uuid"]
    )
    op.drop_constraint(None, "metrics", type_="foreignkey")
    op.create_foreign_key(
        "metrics_series_uuid_fkey", "metrics", "series", ["series_uuid"], ["uuid"]
    )
    op.drop_constraint(None, "items", type_="foreignkey")
    op.create_foreign_key(
        "items_collection_uuid_fkey",
        "items",
        "collections",
        ["collection_uuid"],
        ["uuid"],
    )
    # ### end Alembic commands ###
