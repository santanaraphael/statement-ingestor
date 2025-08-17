from dataclasses import dataclass
from datetime import date
from enum import Enum


class AccountType(Enum):
    BANK = "bank"
    CREDIT_CARD = "credit_card"
    INVESTMENT = "investment"


@dataclass
class Transaction:
    date: date
    description: str
    amount: float
    currency: str
    account_id: str
    category: str | None = None
    metadata: dict | None = None


@dataclass
class Statement:
    account_id: str
    account_type: AccountType
    transactions: list[Transaction]
    start_date: date | None = None
    end_date: date | None = None
