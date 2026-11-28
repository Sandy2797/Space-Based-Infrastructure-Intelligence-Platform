"""Create initial application database schema."""

from alembic import op
import sqlalchemy as sa


revision = "b8f3c2d91a60"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.create_table(
        "monitoring_areas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("crs", sa.String(50), nullable=False),
        sa.Column("geometry", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "satellite_images",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("monitoring_area_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(120), nullable=False),
        sa.Column("file_reference", sa.String(512), nullable=False),
        sa.Column("acquired_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("crs", sa.String(120), nullable=False),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("band_count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "detections",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("before_image_id", sa.Integer(), nullable=False),
        sa.Column("after_image_id", sa.Integer(), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("geometry", sa.JSON(), nullable=False),
        sa.Column("origin_category", sa.String(30), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("model_version", sa.String(120), nullable=False),
        sa.CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="ck_detections_confidence",
        ),
        sa.ForeignKeyConstraint(
            ["before_image_id"],
            ["satellite_images.id"],
        ),
        sa.ForeignKeyConstraint(
            ["after_image_id"],
            ["satellite_images.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_detections_before_image_id",
        "detections",
        ["before_image_id"],
    )

    op.create_index(
        "ix_detections_after_image_id",
        "detections",
        ["after_image_id"],
    )

    op.create_table(
        "infrastructure_assets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("monitoring_area_id", sa.Integer(), nullable=False),
        sa.Column("asset_name", sa.String(120), nullable=False),
        sa.Column("asset_type", sa.String(80), nullable=False),
        sa.Column("location", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["monitoring_area_id"],
            ["monitoring_areas.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_infrastructure_assets_monitoring_area_id",
        "infrastructure_assets",
        ["monitoring_area_id"],
    )


def downgrade() -> None:

    op.drop_index(
        "ix_infrastructure_assets_monitoring_area_id",
        table_name="infrastructure_assets",
    )
    op.drop_table("infrastructure_assets")

    op.drop_index(
        "ix_detections_after_image_id",
        table_name="detections",
    )
    op.drop_index(
        "ix_detections_before_image_id",
        table_name="detections",
    )
    op.drop_table("detections")

    op.drop_table("satellite_images")
    op.drop_table("monitoring_areas")
