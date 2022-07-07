import sqlalchemy as sa

from app.resources.providers import METADATA

from .models import TransactionAction

WALLET_TABLE = sa.Table(
    "wallet",
    METADATA,
    sa.Column(
        "id", sa.String(42), primary_key=True, nullable=False, unique=True
    ),
    sa.Column("is_ignored", sa.Boolean, nullable=False, default=False),
    sa.Column(
        "received_from_id",
        sa.String(42),
        sa.ForeignKey("wallet.id", ondelete="CASCADE"),
        nullable=True,
    ),
)


TRANSACTION_TABLE = sa.Table(
    "transaction",
    METADATA,
    sa.Column("id", sa.String(66), nullable=False, unique=True),
    sa.Column("executed_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column(
        "wallet",
        sa.String(42),
        sa.ForeignKey("wallet.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column("action", sa.Enum(TransactionAction), nullable=False),
    sa.Column("avax", sa.Numeric(23, 8), nullable=False),
    sa.Column("price", sa.Numeric(23, 8), nullable=False),
    sa.Column("lvt", sa.Numeric(23, 8), nullable=False),
)
