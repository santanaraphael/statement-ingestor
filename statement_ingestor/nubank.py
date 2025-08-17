import csv
from datetime import datetime, timedelta
from decimal import Decimal
from statement_ingestor.models import CreditCardStatement, Card, Transaction


def parse_nubank_card_statement(file_path):
    transactions = []
    with open(file_path, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            transactions.append(
                Transaction(
                    date=datetime.strptime(row["date"], "%Y-%m-%d"),
                    description=row["title"],
                    amount=Decimal(row["amount"]),
                )
            )

    if not transactions:
        return None

    total_amount = sum(t.amount for t in transactions)

    first_transaction_date = transactions[0].date
    due_date_month = first_transaction_date.month + 1
    due_date_year = first_transaction_date.year
    if due_date_month > 12:
        due_date_month = 1
        due_date_year += 1
    due_date = datetime(due_date_year, due_date_month, 10)

    card = Card(card_number="0000", transactions=transactions)

    return CreditCardStatement(
        due_date=due_date, total_amount=total_amount, cards=[card]
    )


def parse_nubank_bank_statement(file_path):
    transactions = []
    with open(file_path, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            transactions.append(
                Transaction(
                    date=datetime.strptime(row["Data"], "%d/%m/%Y"),
                    description=row["Descrição"],
                    amount=Decimal(row["Valor"]),
                )
            )
    return transactions
