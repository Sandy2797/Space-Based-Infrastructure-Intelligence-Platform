"""Convert geographic JSON columns to PostGIS geometry.

Revision ID: c2e8fb907a31
Revises: ff19b93b4b3f
"""

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry


revision = "c2e8fb907a31"
down_revision = "ff19b93b4b3f"
branch_labels = None
depends_on = None


SPATIAL_COLUMNS = [
    ("monitoring_areas", "geometry", "GEOMETRY"),
    ("infrastructure_assets", "location", "GEOMETRY"),
    ("detections", "geometry", "POINT"),
]


def upgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return

    for table, column, geometry_type in SPATIAL_COLUMNS:
        op.alter_column(
            table,
            column,
            existing_type=sa.JSON(),
            type_=Geometry(
                geometry_type=geometry_type,
                srid=4326,
                spatial_index=False,
            ),
            existing_nullable=False,
            postgresql_using=(
                f"ST_SetSRID("
                f"ST_GeomFromGeoJSON({column}::text), 4326)"
            ),
        )

        op.create_index(
            f"idx_{table}_{column}_gist",
            table,
            [column],
            postgresql_using="gist",
        )


def downgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return

    for table, column, geometry_type in reversed(SPATIAL_COLUMNS):
        op.drop_index(
            f"idx_{table}_{column}_gist",
            table_name=table,
        )

        op.alter_column(
            table,
            column,
            existing_type=Geometry(
                geometry_type=geometry_type,
                srid=4326,
                spatial_index=False,
            ),
            type_=sa.JSON(),
            existing_nullable=False,
            postgresql_using=(
                f"ST_AsGeoJSON({column})::json"
            ),
        )