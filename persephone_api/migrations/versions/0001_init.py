"""initial tables"""

from __future__ import annotations

from datetime import datetime

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "runs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("phase", sa.String(length=50), nullable=False),
        sa.Column("artifact_key", sa.String(length=512), nullable=False),
        sa.Column("gpu_id", sa.String(length=100), nullable=True),
        sa.Column("service_url", sa.String(length=512), nullable=True),
        sa.Column("progress", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )

    conn = op.get_bind()
    exists = conn.execute(
        sa.text("SELECT 1 FROM users WHERE email = :email"),
        {"email": "admin@persephone.local"},
    ).first()
    if not exists:
        conn.execute(
            sa.text(
                "INSERT INTO users (email, password_hash, created_at) VALUES (:email, :password_hash, :created_at)"
            ),
            {
                "email": "admin@persephone.local",
                "password_hash": "$2b$12$wEJ0oS9MhUlCT3VkOITkk.m1y4HJ2qxd6QbaO5jM90oCbGyF/F7Ai",
                "created_at": datetime.utcnow(),
            },
        )


def downgrade() -> None:
    op.drop_table("runs")
    op.drop_table("users")
