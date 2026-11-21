"""Add satellite image monitoring area foreign key

Revision ID: ff19b93b4b3f
Revises:
Create Date: 2026-11-21
"""

from typing import Sequence, Union

from alembic import op


revision: str = "ff19b93b4b3f"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table(
        "satellite_images",
        schema=None,
    ) as batch_op:

        batch_op.create_index(
            "ix_satellite_images_monitoring_area_id",
            ["monitoring_area_id"],
            unique=False,
        )

        batch_op.create_foreign_key(
            "fk_satellite_images_monitoring_area_id_monitoring_areas",
            "monitoring_areas",
            ["monitoring_area_id"],
            ["id"],
            ondelete="RESTRICT",
        )


def downgrade() -> None:
    with op.batch_alter_table(
        "satellite_images",
        schema=None,
    ) as batch_op:

        batch_op.drop_constraint(
            "fk_satellite_images_monitoring_area_id_monitoring_areas",
            type_="foreignkey",
        )

        batch_op.drop_index(
            "ix_satellite_images_monitoring_area_id"
        )
