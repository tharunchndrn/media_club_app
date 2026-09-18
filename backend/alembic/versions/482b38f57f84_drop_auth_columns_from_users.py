"""drop auth columns from users

Revision ID: 482b38f57f84
Revises: b793dd612c10
Create Date: 2026-09-17 21:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '482b38f57f84'
down_revision: Union[str, None] = 'b793dd612c10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('users', 'role')
    op.drop_column('users', 'password_hash')
    op.execute("DROP TYPE IF EXISTS user_role")


def downgrade() -> None:
    op.add_column(
        'users',
        sa.Column('password_hash', sa.String(length=255), nullable=False, server_default=''),
    )
    user_role = sa.Enum('student', 'admin', name='user_role')
    user_role.create(op.get_bind(), checkfirst=True)
    op.add_column(
        'users',
        sa.Column('role', user_role, server_default='student', nullable=False),
    )
