from datetime import datetime
from decimal import Decimal
from enum import IntEnum

from pydantic import BaseModel, Field


class TransactionAction(IntEnum):
    buy = 0
    sell = 1
    invest_v1 = 2
    invest_v2 = 3


class Wallet(BaseModel):
    id: str = Field(to_lower=True, min_length=42, max_length=42)
    is_ignored: bool = False
    received_from_id: str | None = None


class WalletWithSentTo(Wallet):
    sent_to: list[Wallet] = []


class Transaction(BaseModel):
    id: str = Field(to_lower=True, min_length=66, max_length=66)
    executed_at: datetime
    action: TransactionAction
    avax: Decimal = Decimal("0")
    price: Decimal = Decimal("0")
    lvt: Decimal = Decimal("0")
