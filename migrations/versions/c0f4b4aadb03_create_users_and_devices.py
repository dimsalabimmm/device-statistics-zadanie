"""create users and devices

Revision ID: c0f4b4aadb03
Revises: 
Create Date: 2026-10-11 23:11:06.466707

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0f4b4aadb03'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE users (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            CONSTRAINT users_name_not_blank
                CHECK (length(trim(name)) > 0)
        );
        """
    )

    op.execute(
        """
        CREATE TABLE devices (
            id VARCHAR(100) PRIMARY KEY,
            user_id BIGINT NOT NULL,
            CONSTRAINT devices_id_not_blank
                CHECK (length(trim(id)) > 0),
            CONSTRAINT devices_user_id_fk
                FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
    )

    op.execute(
        """
        CREATE INDEX devices_user_id_idx
        ON devices (user_id);
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE devices;")
    op.execute("DROP TABLE users;")

def downgrade() -> None:
    op.execute("DROP TABLE devices;")
    op.execute("DROP TABLE users;")
