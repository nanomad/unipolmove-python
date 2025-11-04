# Unipol Move Python Client

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A Python client library for programmatic access to the Unipol Move API. Fetch toll movements and generate expense report PDFs.

## Features

- 🔐 Authentication with username/password
- 📊 Fetch toll movements with automatic pagination
- 📄 Generate official PDF expense reports
- 🗓️ Filter movements by date range
- 🐍 Clean, typed Python API
- ⚡ Minimal dependencies (only `requests`)

## Installation

```bash
pip install requests
```

Then copy `unipolmove_client.py` to your project or install via:

```bash
pip install git+https://github.com/yourusername/unipolmove-python.git
```

## Quick Start

```python
from unipolmove_client import UnipolMoveClient
from datetime import date

# Initialize client
client = UnipolMoveClient(contract_id="P000000000")

# Login
if client.login("your@email.com", "yourpassword"):
    print("Login successful!")

    # Fetch all movements
    movements = client.fetch_all_movements(interval="ULTIMO_ANNO")
    print(f"Found {len(movements)} movements")

    # Filter by date range
    filtered = client.filter_movements_by_date(
        movements,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31)
    )

    # Generate PDF report
    pdf_bytes = client.generate_pdf_report(
        movements=filtered,
        intestatario="JOHN DOE",
        output_filename="expense_report.pdf"
    )
    print("PDF generated successfully!")
```

## API Documentation

### UnipolMoveClient

#### `__init__(contract_id, mrh_session=None, last_mrh_session=None, session_id=None)`

Initialize the client.

**Args:**
- `contract_id` (str): Your Unipol Move contract ID (e.g., 'P000000000')
- `mrh_session` (str, optional): MRHSession cookie (if you have it already)
- `last_mrh_session` (str, optional): LastMRH_Session cookie (if you have it already)
- `session_id` (str, optional): Session ID (auto-generated if not provided)

#### `login(username, password) -> bool`

Authenticate and obtain session cookies.

**Args:**
- `username` (str): Your Unipol Move email
- `password` (str): Your Unipol Move password

**Returns:**
- `bool`: True if login successful, False otherwise

#### `fetch_movements(offset=1, limit=100, interval="ULTIMO_ANNO", order_by="date-D", payment_status="0,1,3,4") -> Dict`

Fetch toll movements from the API.

**Args:**
- `offset` (int): Starting offset for pagination (default: 1)
- `limit` (int): Maximum records per request (default: 100)
- `interval` (str): Time interval (default: 'ULTIMO_ANNO' = last year)
- `order_by` (str): Sorting order (default: 'date-D' = date descending)
- `payment_status` (str): Payment status filter (default: '0,1,3,4')

**Returns:**
- `dict`: API response with 'dispositivi' and 'listaMovimenti'

#### `fetch_all_movements(batch_size=100, interval="ULTIMO_ANNO") -> List[Dict]`

Fetch all toll movements with automatic pagination.

**Args:**
- `batch_size` (int): Records per request (default: 100)
- `interval` (str): Time interval (default: 'ULTIMO_ANNO')

**Returns:**
- `list`: All movements

#### `generate_pdf_report(movements, intestatario, output_filename=None) -> bytes`

Generate PDF expense report for selected movements.

**Args:**
- `movements` (list): Movement dictionaries to include
- `intestatario` (str): Report recipient name
- `output_filename` (str, optional): Save to file if provided

**Returns:**
- `bytes`: PDF file content

#### `filter_movements_by_date(movements, start_date, end_date) -> List[Dict]`

Filter movements by date range.

**Args:**
- `movements` (list): Movement dictionaries
- `start_date` (date): Start date (inclusive)
- `end_date` (date): End date (inclusive)

**Returns:**
- `list`: Filtered movements

## Examples

### Basic Usage

```python
from unipolmove_client import UnipolMoveClient

client = UnipolMoveClient(contract_id="P000000000")
client.login("your@email.com", "password")

# Get movements
movements = client.fetch_all_movements()
for movement in movements[:5]:
    print(f"{movement['dataIngresso']}: {movement['importoAddebitato']} EUR")
```

### Date Filtering

```python
from datetime import date

# Get movements from January 2024
movements = client.fetch_all_movements()
january_movements = client.filter_movements_by_date(
    movements,
    start_date=date(2024, 1, 1),
    end_date=date(2024, 1, 31)
)
```

### Generate PDF Report

```python
# Generate report for specific movements
pdf_bytes = client.generate_pdf_report(
    movements=january_movements,
    intestatario="JOHN DOE",
    output_filename="january_2024_report.pdf"
)
```

### Pagination

```python
# Fetch movements in smaller batches
page1 = client.fetch_movements(offset=1, limit=50)
page2 = client.fetch_movements(offset=51, limit=50)
```

## Environment Variables

You can use environment variables for configuration:

```python
import os
from unipolmove_client import UnipolMoveClient

contract_id = os.getenv("UNIPOL_CONTRACT_ID")
username = os.getenv("UNIPOL_USERNAME")
password = os.getenv("UNIPOL_PASSWORD")

client = UnipolMoveClient(contract_id=contract_id)
client.login(username, password)
```

## API Endpoints

The client interfaces with two separate Unipol Move API endpoints:

1. **Movements API**: Fetches toll movement data
   - Endpoint: `/api/ut/prv/unipolmove/portale-tlpd/servizi-mobilita/v6/contratti/{contract_id}/movimenti`

2. **PDF Generation API**: Generates expense report PDFs
   - Endpoint: `/api/us/prv/tpd/telepedaggio-us/post-vendita/v1/contratti/{contract_id}/movimenti/stampa`

Both endpoints require authentication via session cookies obtained through the login flow.

## Requirements

- Python 3.8+
- `requests` library

## Security Notes

- Never commit credentials to version control
- Use environment variables for sensitive data
- Session cookies are stored in memory only
- API credentials are embedded in the client (required for IBM API Gateway)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This is an unofficial client library. It is not affiliated with or endorsed by Unipol Move or UnipolSai Assicurazioni S.p.A.

Use at your own risk. The API endpoints and authentication mechanisms were reverse-engineered and may change without notice.

## Author

This library was created to simplify expense reporting workflows for Unipol Move users.
