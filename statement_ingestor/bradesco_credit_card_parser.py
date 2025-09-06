from typing import Optional
import pdfplumber
import re
from datetime import datetime, date
from decimal import Decimal
from statement_ingestor.models import AccountType, Statement, Transaction
from statement_ingestor.base_parser import BaseParser
from collections import defaultdict


class BradescoCreditCardParser(BaseParser):
    def parse(self, file_path: str) -> Statement:
        lines = _extract_statement_lines(file_path)
        due_date = _extract_due_date(lines)

        transactions = []
        current_card_number = "0000"  # Default card number

        for line in lines:
            if card_number := _extract_card_number(line):
                current_card_number = card_number

            if _is_transaction_line(line):
                account_id = f"bradesco_credit_card_{current_card_number}"
                transaction = _parse_transaction(line, account_id, due_date)
                if transaction:
                    transactions.append(transaction)

        if not transactions:
            return Statement(
                account_id="bradesco_credit_card_multi",
                account_type=AccountType.CREDIT_CARD,
                transactions=[],
                start_date=None,
                end_date=None,
            )

        start_date = min(t.date for t in transactions)
        end_date = max(t.date for t in transactions)

        return Statement(
            account_id="bradesco_credit_card_multi",
            account_type=AccountType.CREDIT_CARD,
            transactions=transactions,
            start_date=start_date,
            end_date=end_date,
        )


def _parse_transaction(
    line: str, account_id: str, due_date: Optional[date]
) -> Transaction | None:
    match = re.match(
        r"""(?P<date>\d{2}/\d{2})\s+
        (?P<description>.*?)\s+
        (?P<amount>[\d.,]+-?)""",
        line,
        re.VERBOSE,
    )
    if not match:
        return None

    date_str = match.group("date")
    description = match.group("description")
    amount_str = match.group("amount")

    is_negative = amount_str.endswith("-")
    if is_negative:
        amount_str = "-" + amount_str[:-1]

    transaction_year = datetime.now().year
    if due_date:
        transaction_month = int(date_str.split("/")[1])
        if transaction_month > due_date.month:
            transaction_year = due_date.year - 1
        else:
            transaction_year = due_date.year

    transaction_date = datetime.strptime(
        f"{date_str}/{transaction_year}", "%d/%m/%Y"
    ).date()
    amount = float(Decimal(amount_str.replace(".", "").replace(",", ".")))

    return Transaction(
        date=transaction_date,
        description=description,
        amount=amount,
        currency="BRL",
        account_id=account_id,
    )


def _extract_due_date(lines: list[str]) -> Optional[date]:
    """
    Extracts the statement due date from the statement lines.
    It looks for a line containing "VENCIMENTO" and a date in dd/mm/yyyy format.
    """
    for line in lines:
        if "VENCIMENTO" in line.upper():
            match = re.search(r"(\d{2}/\d{2}/\d{4})", line)
            if match:
                return datetime.strptime(match.group(1), "%d/%m/%Y").date()
    return None


def _extract_statement_lines(file_path: str) -> list[str]:
    with pdfplumber.open(file_path) as pdf:
        result = []

        for page in pdf.pages:
            result.extend(page.extract_text().split("\n"))

        return result


def _is_transaction_line(line: str) -> bool:
    """
    Check if a line matches the format of a transaction line.
    Examples:
    - "06/03 PAG BOLETO BANCARIO 8.804,23- PROGRAMA DE FIDELIDADE"
    - "06/03 PAO DE ACUCAR-1783 R. DE JANEIRO 24,05"
    - "27/02 POSTO CARDEAL RIO DE JANEIR 117,50 * Pontuação consolidada de todos os cartões do Associado."
    """
    pattern = r"^\d{2}/\d{2}\s+.*?\s+[\d.,]+-?"
    return bool(re.match(pattern, line))


def _extract_card_number(line: str) -> Optional[str]:
    """
    Check if a line is a card header and return its last 4 digits.
    Example:
    - "JOHN DOE Cartão 4066 XXXX XXXX 3029" -> "3029"
    """
    pattern = r".*Cartão\s+\d{4}\s+XXXX\s+XXXX\s+(\d{4})"
    match = re.search(pattern, line)
    if match:
        return match.group(1)
    return None
