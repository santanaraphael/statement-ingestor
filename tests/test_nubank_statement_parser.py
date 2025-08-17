import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from statement_ingestor.models import CreditCardStatement, Card, Transaction
from statement_ingestor.nubank import (
    parse_nubank_card_statement,
    parse_nubank_bank_statement,
)


def test_parse_nubank_card_statement():
    file_path = "anonymous_samples/nubank_card_statement.csv"

    transactions = [
        Transaction(
            date=datetime(2024, 1, 1), description="Uber* Trip", amount=Decimal("15.50")
        ),
        Transaction(
            date=datetime(2024, 1, 2), description="Spotify", amount=Decimal("19.90")
        ),
        Transaction(
            date=datetime(2024, 1, 3), description="Netflix", amount=Decimal("39.90")
        ),
        Transaction(
            date=datetime(2024, 1, 4),
            description="Amazon.com.br",
            amount=Decimal("79.90"),
        ),
        Transaction(
            date=datetime(2024, 1, 5), description="iFood", amount=Decimal("45.30")
        ),
        Transaction(
            date=datetime(2024, 1, 6),
            description="Posto Shell",
            amount=Decimal("150.00"),
        ),
        Transaction(
            date=datetime(2024, 1, 7),
            description="Padaria Pão de Ouro",
            amount=Decimal("25.80"),
        ),
        Transaction(
            date=datetime(2024, 1, 8),
            description="Farmácia Droga Raia",
            amount=Decimal("65.40"),
        ),
        Transaction(
            date=datetime(2024, 1, 9),
            description="Pagamento recebido",
            amount=Decimal("-500.00"),
        ),
        Transaction(
            date=datetime(2024, 1, 10),
            description="Supermercado Guanabara",
            amount=Decimal("350.00"),
        ),
    ]

    total_amount = sum(t.amount for t in transactions)
    due_date = datetime(2024, 2, 10)

    expected_statement = CreditCardStatement(
        due_date=due_date,
        total_amount=total_amount,
        cards=[Card(card_number="0000", transactions=transactions)],
    )

    result = parse_nubank_card_statement(file_path)
    assert result == expected_statement


def test_parse_nubank_bank_statement():
    file_path = "anonymous_samples/nubank_bank_statement.csv"

    expected_data = [
        Transaction(
            date=datetime(2024, 7, 14),
            description="Transferência recebida pelo Pix - João - •••.962.813-•• - Itaú (0341) Agência: 2938 Conta: 93843-2",
            amount=Decimal("7568.39"),
        ),
        Transaction(
            date=datetime(2024, 3, 29),
            description="Pagamento de boleto efetuado - Empresa C",
            amount=Decimal("-4532.59"),
        ),
        Transaction(
            date=datetime(2024, 9, 19),
            description="Transferência enviada pelo Pix - Ana - •••.334.693-•• - Bradesco (0237) Agência: 8821 Conta: 21333-3",
            amount=Decimal("2519.42"),
        ),
        Transaction(
            date=datetime(2024, 2, 7),
            description="Pagamento de fatura",
            amount=Decimal("-8923.25"),
        ),
        Transaction(
            date=datetime(2024, 11, 11),
            description="Compra no débito - Loja Z",
            amount=Decimal("1693.48"),
        ),
        Transaction(
            date=datetime(2024, 6, 1),
            description="Recarga de celular",
            amount=Decimal("-7843.82"),
        ),
        Transaction(
            date=datetime(2024, 8, 25),
            description="Reembolso recebido pelo Pix - Pedro - •••.833.111-•• - Santander (0033) Agência: 1183 Conta: 83213-8",
            amount=Decimal("9421.86"),
        ),
        Transaction(
            date=datetime(2024, 4, 13),
            description="Pagamento de boleto efetuado - Empresa A",
            amount=Decimal("-6732.41"),
        ),
        Transaction(
            date=datetime(2024, 12, 3),
            description="Transferência recebida pelo Pix - Mariana - •••.222.333-•• - Nubank (0260) Agência: 0001 Conta: 33322-1",
            amount=Decimal("3141.59"),
        ),
        Transaction(
            date=datetime(2024, 7, 22),
            description="Compra no débito - Loja Y",
            amount=Decimal("-5821.43"),
        ),
    ]

    result = parse_nubank_bank_statement(file_path)
    assert result == expected_data
