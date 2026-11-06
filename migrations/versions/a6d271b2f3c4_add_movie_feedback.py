"""Add per-user movie preference feedback."""

from alembic import op
import sqlalchemy as sa


revision = "a6d271b2f3c4"
down_revision = "5479874111e2"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "movie_feedback",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("tmdb_movie_id", sa.Integer(), nullable=False),
        sa.Column("movie_title", sa.String(length=200), nullable=False),
        sa.Column("feature_text", sa.Text(), nullable=False),
        sa.Column("preference", sa.SmallInteger(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "preference IN (-1, 1)",
            name="ck_movie_feedback_preference",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "tmdb_movie_id",
            name="uq_movie_feedback_user_tmdb",
        ),
    )


def downgrade():
    op.drop_table("movie_feedback")
