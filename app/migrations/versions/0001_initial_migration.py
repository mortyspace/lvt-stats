"""Initial migration

Revision ID: 0001
Revises:
Created Date: 2022-07-10 19:43:57.892832

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "wallet",
        sa.Column("id", sa.String(length=42), nullable=False),
        sa.Column("is_ignored", sa.Boolean(), nullable=False),
        sa.Column("received_from_id", sa.String(length=42), nullable=True),
        sa.ForeignKeyConstraint(
            ["received_from_id"], ["wallet.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_table(
        "transaction",
        sa.Column("id", sa.String(length=66), nullable=False),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("wallet", sa.String(length=42), nullable=False),
        sa.Column(
            "action",
            sa.Enum(
                "buy",
                "sell",
                "invest_v1",
                "invest_v2",
                name="transactionaction",
            ),
            nullable=False,
        ),
        sa.Column("avax", sa.Numeric(precision=23, scale=8), nullable=False),
        sa.Column("price", sa.Numeric(precision=23, scale=8), nullable=False),
        sa.Column("lvt", sa.Numeric(precision=23, scale=8), nullable=False),
        sa.ForeignKeyConstraint(["wallet"], ["wallet.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("transaction")
    op.drop_table("wallet")
    # ### end Alembic commands ###
