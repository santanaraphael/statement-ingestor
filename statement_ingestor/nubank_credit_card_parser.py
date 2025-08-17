import csv
from datetime import datetime, date
from statement_ingestor.models import AccountType, Statement, Transaction
from statement_ingestor.base_parser import BaseParser


class NubankCreditCardParser(BaseParser):
    def parse(self, file_path: str) -> Statement:
        transactions = []
        with open(file_path, "r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                transactions.append(
                    Transaction(
                        date=datetime.strptime(row["date"], "%Y-%m-%d").date(),
                        description=row["title"],
                        amount=float(row["amount"]),
                        currency="BRL",
                        account_id="nubank_card_0000",
                    )
                )

        if not transactions:
            return Statement(
                account_id="nubank_card_0000",
                account_type=AccountType.CREDIT_CARD,
                transactions=[],
                start_date=None,
                end_date=None,
            )

        start_date = min(t.date for t in transactions)
        end_date = max(t.date for t in transactions)

        return Statement(
            account_id="nubank_card_0000",
            account_type=AccountType.CREDIT_CARD,
            transactions=transactions,
            start_date=start_date,
            end_date=end_date,
        )
