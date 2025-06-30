from unittest.mock import patch, MagicMock
from statement_ingestor.bradesco_credit_card import (
    ingest_statement,
    _extract_card_number,
    _is_transaction_line,
    _parse_transaction,
    _extract_statement_lines,
)
from statement_ingestor.models import Transaction, CreditCardStatement
from datetime import datetime
from decimal import Decimal


def test_ingest_statement():
    mock_pdf_content = [
        "Data de Vencimento Total da Fatura R$",
        "01/01/2025 100,00",
        "JOHN DOE Cartão 4066 XXXX XXXX 1234",
        "06/03 PAG BOLETO BANCARIO 1.234,56-",
        "07/03 COMPRA TESTE 100,00",
        "JOHN DOE Cartão 4066 XXXX XXXX 5678",
        "08/03 OUTRA COMPRA 50,00",
    ]

    with patch(
        "statement_ingestor.bradesco_credit_card._extract_statement_lines",
        return_value=mock_pdf_content,
    ):
        statement = ingest_statement("dummy.pdf")

        assert isinstance(statement, CreditCardStatement)
        assert statement.due_date == datetime(2025, 1, 1)
        assert statement.total_amount == Decimal("100.00")
        assert len(statement.cards) == 2

        card_1234 = next(card for card in statement.cards if card.card_number == "1234")
        assert len(card_1234.transactions) == 2
        assert card_1234.transactions[0] == Transaction(
            date=datetime(2025, 3, 6),
            description="PAG BOLETO BANCARIO",
            amount=Decimal("-1234.56"),
        )
        assert card_1234.transactions[1] == Transaction(
            date=datetime(2025, 3, 7),
            description="COMPRA TESTE",
            amount=Decimal("100.00"),
        )

        card_5678 = next(card for card in statement.cards if card.card_number == "5678")
        assert len(card_5678.transactions) == 1
        assert card_5678.transactions[0] == Transaction(
            date=datetime(2025, 3, 8),
            description="OUTRA COMPRA",
            amount=Decimal("50.00"),
        )


def test_extract_card_number():
    assert _extract_card_number("JOHN DOE Cartão 4066 XXXX XXXX 1234") == "1234"

    assert (
        _extract_card_number("4066 XXXX XXXX 9999 99.999,99 99.999,99 99.999,99")
        is None
    )


def test_is_transaction_line():
    # Regular transaction
    assert _is_transaction_line(
        "06/03 PAG BOLETO BANCARIO 1.234,56- PROGRAMA DE FIDELIDADE"
    )

    # Transaction with store name and city
    assert _is_transaction_line("06/03 PAO DE ACUCAR-1783 R. DE JANEIRO 24,05")

    # Transaction with additional text after amount
    assert _is_transaction_line(
        "27/02 POSTO CARDEAL RIO DE JANEIR 123,45 * Pontuação consolidada de todos os cartões do Associado."
    )

    # Transaction with negative amount
    assert _is_transaction_line("06/03 PAGAMENTO FATURA 1.234,56-")

    # Should not match non-transaction lines
    assert not _is_transaction_line("VISA INFINITE")
    assert not _is_transaction_line("Data de Vencimento Total da Fatura R$")
    assert not _is_transaction_line("JOHN DOE Cartão 9999 XXXX XXXX 1234")


def test_parse_transaction():
    line = "06/03 PAG BOLETO BANCARIO 1.234,56-"
    expected = Transaction(
        date=datetime(2025, 3, 6),
        description="PAG BOLETO BANCARIO",
        amount=Decimal("-1234.56"),
    )
    assert _parse_transaction(line) == expected
