"""create measurements

Revision ID: fc9e4b24df27
Revises: c0f4b4aadb03
Create Date: 2026-10-11 23:33:52.370830

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fc9e4b24df27'
down_revision: Union[str, Sequence[str], None] = 'c0f4b4aadb03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE measurements (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            device_id VARCHAR(100) NOT NULL,
            measured_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
            x DOUBLE PRECISION NOT NULL,
            y DOUBLE PRECISION NOT NULL,
            z DOUBLE PRECISION NOT NULL,

            CONSTRAINT measurements_device_id_fk
                FOREIGN KEY (device_id) REFERENCES devices(id),

            CONSTRAINT measurements_x_finite
                CHECK (
                    x > '-Infinity'::double precision
                    AND x < 'Infinity'::double precision
                ),

            CONSTRAINT measurements_y_finite
                CHECK (
                    y > '-Infinity'::double precision
                    AND y < 'Infinity'::double precision
                ),

            CONSTRAINT measurements_z_finite
                CHECK (
                    z > '-Infinity'::double precision
                    AND z < 'Infinity'::double precision
                )
        );
        """
    )

    op.execute(
        """
        CREATE INDEX measurements_device_time_idx
        ON measurements (device_id, measured_at);
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE measurements;")