from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class TransactionAction(Enum):
    buy = 0
    sell = 1
    invest_v1 = 2
    invest_v2 = 3


class Wallet(BaseModel):
    id: str = Field(to_lower=True, min_length=42, max_length=42)
    is_ignored: bool = False
    received_from_id: str | None = None


class WalletWithAggrInfo(Wallet):
    avax_invested: Decimal = Decimal("0")
    avax_got_back: Decimal = Decimal("0")
    usd_invested: Decimal = Decimal("0")
    usd_got_back: Decimal = Decimal("0")
    lvt_bought: Decimal = Decimal("0")
    lvt_invested_v1: Decimal = Decimal("0")
    lvt_invested_v2: Decimal = Decimal("0")
    lvt_invested_ratio: Decimal = Decimal("0")

    class Config:
        json_encoders = {Decimal: lambda d: f"{d.normalize()}"}


class Transaction(BaseModel):
    id: str = Field(to_lower=True, min_length=66, max_length=66)
    wallet: str = Field(to_lower=True, min_length=42, max_length=42)
    executed_at: datetime
    action: TransactionAction
    avax: Decimal = Decimal("0")
    price: Decimal = Decimal("0")
    lvt: Decimal = Decimal("0")

    class Config:
        json_encoders = {Decimal: lambda d: f"{d.normalize()}"}
