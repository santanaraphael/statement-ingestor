from unittest.mock import patch, MagicMock
from statement_ingestor import BradescoCreditCardParser
from statement_ingestor.bradesco_credit_card_parser import (
    _extract_card_number,
    _is_transaction_line,
    _parse_transaction,
    _extract_statement_lines,
)
from statement_ingestor.models import AccountType, Statement, Transaction
from datetime import datetime, date


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
        "statement_ingestor.bradesco_credit_card_parser._extract_statement_lines",
        return_value=mock_pdf_content,
    ):
        parser = BradescoCreditCardParser()
        statement = parser.parse("dummy.pdf")

        assert isinstance(statement, Statement)
        assert statement.account_id == "bradesco_credit_card_0000"
        assert statement.account_type == AccountType.CREDIT_CARD
        assert statement.start_date == date(2025, 3, 6)
        assert statement.end_date == date(2025, 3, 8)
        assert len(statement.transactions) == 3

        expected_transactions = [
            Transaction(
                date=date(2025, 3, 6),
                description="PAG BOLETO BANCARIO",
                amount=-1234.56,
                currency="BRL",
                account_id="bradesco_credit_card_0000",
            ),
            Transaction(
                date=date(2025, 3, 7),
                description="COMPRA TESTE",
                amount=100.00,
                currency="BRL",
                account_id="bradesco_credit_card_0000",
            ),
            Transaction(
                date=date(2025, 3, 8),
                description="OUTRA COMPRA",
                amount=50.00,
                currency="BRL",
                account_id="bradesco_credit_card_0000",
            ),
        ]

        assert statement.transactions == expected_transactions


def test_ingest_statement_empty(tmp_path):
    empty_file = tmp_path / "empty_statement.pdf"
    empty_file.write_text("")

    with patch(
        "statement_ingestor.bradesco_credit_card_parser._extract_statement_lines",
        return_value=[],
    ):
        parser = BradescoCreditCardParser()
        statement = parser.parse(str(empty_file))

        assert isinstance(statement, Statement)
        assert statement.account_id == "bradesco_credit_card_0000"
        assert statement.account_type == AccountType.CREDIT_CARD
        assert statement.transactions == []
        assert statement.start_date is None
        assert statement.end_date is None


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
        date=date(2025, 3, 6),
        description="PAG BOLETO BANCARIO",
        amount=-1234.56,
        currency="BRL",
        account_id="test_account_id",  # Dummy account ID for testing
    )
    assert _parse_transaction(line, "test_account_id", None) == expected


def test_parse_transaction_year_boundary():
    # Test case where statement spans across year-end
    # Due date is in January, transaction is in December of previous year
    line = "28/12 COMPRA DE NATAL 150,00"
    due_date = date(2024, 1, 15)
    expected = Transaction(
        date=date(2023, 12, 28),
        description="COMPRA DE NATAL",
        amount=150.00,
        currency="BRL",
        account_id="test_account_id",
    )
    assert _parse_transaction(line, "test_account_id", due_date) == expected
