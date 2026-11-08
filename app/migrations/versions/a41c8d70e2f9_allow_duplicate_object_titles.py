"""Allow objects with different codes to share a display title.

Revision ID: a41c8d70e2f9
Revises: fc7deb334c55
"""

from alembic import op

revision = "a41c8d70e2f9"
down_revision = "fc7deb334c55"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("object_title_key", "object", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint("object_title_key", "object", ["title"])
