"""add init tables

Revision ID: d566fd96ec54
Revises:
Create Date: 2022-02-15 16:23:44.410558

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd566fd96ec54'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("username", sa.String(256), unique=True, nullable=False),
        sa.Column("password", sa.String(256), nullable=False),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.Column("last_request_at", sa.DateTime(), nullable=False)
    )
    op.create_table(
        "post",
        sa.Column("id", sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False)
    )
    op.create_table(
        "like",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["post.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ),
        sa.PrimaryKeyConstraint("id", "user_id", "post_id")
    )


def downgrade():
    result = input("You are dropping all initial tables. Continue? [Y/N]")
    if result.lower() != "y":
        print("Canceled")
        exit()
    op.drop_table("like")
    op.drop_table("post")
    op.drop_table("user")
