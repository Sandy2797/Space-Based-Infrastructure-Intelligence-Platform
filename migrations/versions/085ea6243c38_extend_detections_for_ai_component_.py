
"""extend detections for AI component outputs

Revision ID: 085ea6243c38
Revises: c2e8fb907a31
"""

from typing import Sequence, Union

import geoalchemy2
from alembic import op
import sqlalchemy as sa


revision: str = "085ea6243c38"
down_revision: Union[str, Sequence[str], None] = "c2e8fb907a31"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add optional AI component metadata.
    op.add_column(
        "detections",
        sa.Column("component_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "detections",
        sa.Column("change_score", sa.Float(), nullable=True),
    )
    op.add_column(
        "detections",
        sa.Column("threshold", sa.JSON(), nullable=True),
    )
    op.add_column(
        "detections",
        sa.Column("pixel_count", sa.Integer(), nullable=True),
    )
    op.add_column(
        "detections",
        sa.Column("area_m2", sa.Float(), nullable=True),
    )
    op.add_column(
        "detections",
        sa.Column("evidence_quality", sa.JSON(), nullable=True),
    )
    op.add_column(
        "detections",
        sa.Column("quality_flags", sa.JSON(), nullable=True),
    )
    op.add_column(
        "detections",
        sa.Column("mask_reference", sa.String(length=512), nullable=True),
    )

    # Preserve existing Point geometries while allowing
    # Point, Polygon, and MultiPolygon geometries.
    op.alter_column(
        "detections",
        "geometry",
        existing_type=geoalchemy2.types.Geometry(
            geometry_type="POINT",
            srid=4326,
        ),
        type_=geoalchemy2.types.Geometry(
            geometry_type="GEOMETRY",
            srid=4326,
            spatial_index=False,
        ),
        existing_nullable=False,
        postgresql_using="geometry::geometry(Geometry,4326)",
    )

    # Confidence may be unavailable until calibrated.
    op.alter_column(
        "detections",
        "confidence",
        existing_type=sa.DOUBLE_PRECISION(precision=53),
        nullable=True,
    )

    # Existing PostGIS GiST indexes are intentionally preserved.


def downgrade() -> None:
    # A downgrade is unsafe if Polygon or MultiPolygon records
    # have been inserted. Do not silently discard their geometry.
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM detections
                WHERE GeometryType(geometry) <> 'POINT'
                   OR confidence IS NULL
            ) THEN
                RAISE EXCEPTION
                    'Cannot downgrade: non-Point detections or NULL confidence values exist.';
            END IF;
        END $$;
    """)

    op.alter_column(
        "detections",
        "confidence",
        existing_type=sa.DOUBLE_PRECISION(precision=53),
        nullable=False,
    )

    op.alter_column(
        "detections",
        "geometry",
        existing_type=geoalchemy2.types.Geometry(
            geometry_type="GEOMETRY",
            srid=4326,
            spatial_index=False,
        ),
        type_=geoalchemy2.types.Geometry(
            geometry_type="POINT",
            srid=4326,
        ),
        existing_nullable=False,
        postgresql_using="geometry::geometry(Point,4326)",
    )

    op.drop_column("detections", "mask_reference")
    op.drop_column("detections", "quality_flags")
    op.drop_column("detections", "evidence_quality")
    op.drop_column("detections", "area_m2")
    op.drop_column("detections", "pixel_count")
    op.drop_column("detections", "threshold")
    op.drop_column("detections", "change_score")
    op.drop_column("detections", "component_id")