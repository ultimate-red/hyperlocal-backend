"""task abort: add abort_reason, hidden flags, convert status to string

Revision ID: 0001
Revises:
Create Date: 2026-04-28
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Convert PostgreSQL enum to plain varchar (SQLite is a no-op)
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TABLE tasks ALTER COLUMN status TYPE VARCHAR USING status::text")
        op.execute("DROP TYPE IF EXISTS taskstatus")

    op.add_column("tasks", sa.Column("abort_reason",         sa.String(),  nullable=True))
    op.add_column("tasks", sa.Column("hidden_from_creator",  sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("tasks", sa.Column("hidden_from_acceptor", sa.Boolean(), nullable=False, server_default="false"))


def downgrade() -> None:
    op.drop_column("tasks", "hidden_from_acceptor")
    op.drop_column("tasks", "hidden_from_creator")
    op.drop_column("tasks", "abort_reason")
