# Statement Ingestor

This project provides a tool to ingest bank statements from PDF files and extract transaction data.

## Installation

You can install the project directly from GitHub using pip:

```bash
pip install git+https://github.com/santanaraphael/statement-ingestor.git
```

## Usage

After installation, you can use the `ingest_statement` function to process your Bradesco PDF statements:

```python
from statement_ingestor.bradesco import ingest_statement

file_path = "path/to/your/bradesco_statement.pdf" # Replace with your actual PDF file path
statement = ingest_statement(file_path)

print(f"Due Date: {statement.due_date.strftime('%Y-%m-%d')}")
print(f"Total Amount: {statement.total_amount}")

for card in statement.cards:
    print(f"\nTransactions for card: {card.card_number}")
    for transaction in card.transactions:
        print(f"  Date: {transaction.date.strftime('%Y-%m-%d')}, Description: {transaction.description}, Amount: {transaction.amount}")
```

## License

`statement-ingestor` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Acknowledgements

This project was built with the assistance of the Gemini CLI.