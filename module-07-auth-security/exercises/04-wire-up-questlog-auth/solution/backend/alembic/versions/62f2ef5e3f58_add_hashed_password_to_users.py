"""add hashed_password to users

Revision ID: 62f2ef5e3f58
Revises: 4dbdce72cca0
Create Date: 2026-08-07 09:05:00.000000

See lessons/06-building-signup-login.md's "the migration, concretely" box
for the full walkthrough of this file. Short version: Module 06's initial
migration (`4dbdce72cca0`, this file's `down_revision` below -- that's the
literal chain link Alembic uses to know this migration applies *on top of*
that one, never before it) created `users` with no password column at
all, because Module 06 deliberately stopped short of real authentication.
This migration adds exactly the one column Module 07 needs.

**A real production migration adding a NOT NULL column to an already
populated table cannot look this simple** -- every existing row would
need a real value for the new column *before* the NOT NULL constraint
could be safely applied, usually via a multi-step migration (add the
column nullable, backfill every existing row, then a second migration
that finally applies NOT NULL). This module's setup lesson has you start
from a genuinely empty, freshly created database specifically so this
migration can skip that entire dance and stay focused on this module's
own topic -- see lessons/00-setup.md, Step 2, and
lessons/06-building-signup-login.md's callout box for exactly why that's
a deliberate simplification, not an oversight, and a pointer back to
Module 06, Lesson 07 (Alembic) for how the multi-step version works for
real.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '62f2ef5e3f58'
down_revision: Union[str, Sequence[str], None] = '4dbdce72cca0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'hashed_password')
