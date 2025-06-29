from typing import Optional
import pdfplumber
import re
from datetime import datetime
from decimal import Decimal
from src.statement_ingestor.models import Transaction, Card, Statement


def _parse_transaction(line: str) -> Transaction | None:
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

    # Assuming the year is the current year.
    # This might need to be adjusted for statements spanning multiple years.
    date = datetime.strptime(f"{date_str}/{datetime.now().year}", "%d/%m/%Y")
    amount = Decimal(amount_str.replace(".", "").replace(",", "."))

    return Transaction(date=date, description=description, amount=amount)

from collections import defaultdict


def _extract_statement_lines(file_path: str) -> list[str]:
    with pdfplumber.open(file_path) as pdf:
        result = []

        for page in pdf.pages:
            result.extend(page.extract_text().split("\n"))

        return result


def ingest_statement(file_path: str) -> Statement:
    lines = _extract_statement_lines(file_path)

    header_index = next(
        i
        for i, line in enumerate(lines)
        if "Data de Vencimento Total da Fatura R$" in line
    )
    header_line = lines[header_index + 1]

    match = re.search(r"(\d{2}/\d{2}/\d{4})\s+([\d.,]+)", header_line)
    if match:
        due_date_str = match.group(1)
        total_amount_str = match.group(2)
    else:
        raise ValueError("Could not find due date and total amount")

    due_date = datetime.strptime(due_date_str, "%d/%m/%Y")
    total_amount = Decimal(total_amount_str.replace(".", "").replace(",", "."))

    transactions_by_card = defaultdict(list)
    card_identifier = "generic"
    for line in lines:
        new_card_identifier = _extract_card_number(line)
        if new_card_identifier is not None:
            card_identifier = new_card_identifier

        if _is_transaction_line(line):
            transaction = _parse_transaction(line)
            if transaction:
                transactions_by_card[card_identifier].append(transaction)

    cards = []
    for card_number, transactions in transactions_by_card.items():
        cards.append(Card(card_number=card_number, transactions=transactions))

    return Statement(due_date=due_date, total_amount=total_amount, cards=cards)


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
