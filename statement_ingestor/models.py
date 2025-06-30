from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Transaction:
    date: datetime
    description: str
    amount: Decimal


@dataclass
class Card:
    card_number: str
    transactions: list[Transaction]


@dataclass
class CreditCardStatement:
    due_date: datetime
    total_amount: Decimal
    cards: list[Card]
