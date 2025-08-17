import pytest
from datetime import datetime, date
from statement_ingestor.models import AccountType, Statement, Transaction
from statement_ingestor import NubankCreditCardParser, NubankBankParser


def test_parse_nubank_card_statement():
    file_path = "anonymous_samples/nubank_card_statement.csv"

    transactions = [
        Transaction(
            date=date(2024, 1, 1),
            description="Uber* Trip",
            amount=15.50,
            currency="BRL",
            account_id="nubank_card_0000",
        ),
        Transaction(
            date=date(2024, 1, 2),
            description="Spotify",
            amount=19.90,
            currency="BRL",
            account_id="nubank_card_0000",
        ),
        Transaction(
            date=date(2024, 1, 3),
            description="Netflix",
            amount=39.90,
            currency="BRL",
            account_id="nubank_card_0000",
        ),
        Transaction(
            date=date(2024, 1, 4),
            description="Amazon.com.br",
            amount=79.90,
            currency="BRL",
            account_id="nubank_card_0000",
        ),
        Transaction(
            date=date(2024, 1, 5),
            description="iFood",
            amount=45.30,
            currency="BRL",
            account_id="nubank_card_0000",
        ),
        Transaction(
            date=date(2024, 1, 6),
            description="Posto Shell",
            amount=150.00,
            currency="BRL",
            account_id="nubank_card_0000",
        ),
        Transaction(
            date=date(2024, 1, 7),
            description="Padaria Pão de Ouro",
            amount=25.80,
            currency="BRL",
            account_id="nubank_card_0000",
        ),
        Transaction(
            date=date(2024, 1, 8),
            description="Farmácia Droga Raia",
            amount=65.40,
            currency="BRL",
            account_id="nubank_card_0000",
        ),
        Transaction(
            date=date(2024, 1, 9),
            description="Pagamento recebido",
            amount=-500.00,
            currency="BRL",
            account_id="nubank_card_0000",
        ),
        Transaction(
            date=date(2024, 1, 10),
            description="Supermercado Guanabara",
            amount=350.00,
            currency="BRL",
            account_id="nubank_card_0000",
        ),
    ]

    expected_statement = Statement(
        account_id="nubank_card_0000",
        account_type=AccountType.CREDIT_CARD,
        transactions=transactions,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 10),
    )

    parser = NubankCreditCardParser()
    result = parser.parse(file_path)
    assert result == expected_statement


def test_parse_nubank_card_statement_empty(tmp_path):
    empty_file = tmp_path / "empty_card_statement.csv"
    empty_file.write_text("date,title,amount\n")

    parser = NubankCreditCardParser()
    result = parser.parse(str(empty_file))

    expected_statement = Statement(
        account_id="nubank_card_0000",
        account_type=AccountType.CREDIT_CARD,
        transactions=[],
        start_date=None,
        end_date=None,
    )
    assert result == expected_statement


def test_parse_nubank_bank_statement():
    file_path = "anonymous_samples/nubank_bank_statement.csv"

    transactions = [
        Transaction(
            date=date(2024, 7, 14),
            description="Transferência recebida pelo Pix - João - •••.962.813-•• - Itaú (0341) Agência: 2938 Conta: 93843-2",
            amount=7568.39,
            currency="BRL",
            account_id="nubank_bank_0000",
        ),
        Transaction(
            date=date(2024, 3, 29),
            description="Pagamento de boleto efetuado - Empresa C",
            amount=-4532.59,
            currency="BRL",
            account_id="nubank_bank_0000",
        ),
        Transaction(
            date=date(2024, 9, 19),
            description="Transferência enviada pelo Pix - Ana - •••.334.693-•• - Bradesco (0237) Agência: 8821 Conta: 21333-3",
            amount=2519.42,
            currency="BRL",
            account_id="nubank_bank_0000",
        ),
        Transaction(
            date=date(2024, 2, 7),
            description="Pagamento de fatura",
            amount=-8923.25,
            currency="BRL",
            account_id="nubank_bank_0000",
        ),
        Transaction(
            date=date(2024, 11, 11),
            description="Compra no débito - Loja Z",
            amount=1693.48,
            currency="BRL",
            account_id="nubank_bank_0000",
        ),
        Transaction(
            date=date(2024, 6, 1),
            description="Recarga de celular",
            amount=-7843.82,
            currency="BRL",
            account_id="nubank_bank_0000",
        ),
        Transaction(
            date=date(2024, 8, 25),
            description="Reembolso recebido pelo Pix - Pedro - •••.833.111-•• - Santander (0033) Agência: 1183 Conta: 83213-8",
            amount=9421.86,
            currency="BRL",
            account_id="nubank_bank_0000",
        ),
        Transaction(
            date=date(2024, 4, 13),
            description="Pagamento de boleto efetuado - Empresa A",
            amount=-6732.41,
            currency="BRL",
            account_id="nubank_bank_0000",
        ),
        Transaction(
            date=date(2024, 12, 3),
            description="Transferência recebida pelo Pix - Mariana - •••.222.333-•• - Nubank (0260) Agência: 0001 Conta: 33322-1",
            amount=3141.59,
            currency="BRL",
            account_id="nubank_bank_0000",
        ),
        Transaction(
            date=date(2024, 7, 22),
            description="Compra no débito - Loja Y",
            amount=-5821.43,
            currency="BRL",
            account_id="nubank_bank_0000",
        ),
    ]

    expected_statement = Statement(
        account_id="nubank_bank_0000",
        account_type=AccountType.BANK,
        transactions=transactions,
        start_date=date(2024, 2, 7),
        end_date=date(2024, 12, 3),
    )

    parser = NubankBankParser()
    result = parser.parse(file_path)
    assert result == expected_statement


def test_parse_nubank_bank_statement_empty(tmp_path):
    empty_file = tmp_path / "empty_bank_statement.csv"
    empty_file.write_text("Data,Valor,Identificador,Descrição\n")

    parser = NubankBankParser()
    result = parser.parse(str(empty_file))

    expected_statement = Statement(
        account_id="nubank_bank_0000",
        account_type=AccountType.BANK,
        transactions=[],
        start_date=None,
        end_date=None,
    )
    assert result == expected_statement
