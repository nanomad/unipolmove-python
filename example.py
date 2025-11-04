#!/usr/bin/env python3
"""
Example usage of the Unipol Move Python Client

This script demonstrates how to:
1. Authenticate with Unipol Move
2. Fetch toll movements
3. Filter movements by date
4. Generate PDF expense reports
"""

import os
from datetime import date
from unipolmove_client import UnipolMoveClient


def main():
    # Get credentials from environment variables
    # You can also hardcode them for testing (but never commit credentials!)
    contract_id = os.getenv("UNIPOL_CONTRACT_ID", "P000000000")
    username = os.getenv("UNIPOL_USERNAME", "your@email.com")
    password = os.getenv("UNIPOL_PASSWORD", "yourpassword")
    recipient = os.getenv("REPORT_RECIPIENT", "JOHN DOE")

    print("Unipol Move API Client - Example Usage")
    print("=" * 50)

    # Initialize the client
    print(f"\n1. Initializing client with contract ID: {contract_id}")
    client = UnipolMoveClient(contract_id=contract_id)

    # Login
    print(f"\n2. Logging in as: {username}")
    try:
        if client.login(username, password):
            print("   ✓ Login successful!")
        else:
            print("   ✗ Login failed - invalid credentials or missing cookies")
            return
    except Exception as e:
        print(f"   ✗ Login error: {e}")
        return

    # Fetch all movements
    print("\n3. Fetching all movements from the last year...")
    try:
        movements = client.fetch_all_movements(interval="ULTIMO_ANNO")
        print(f"   ✓ Found {len(movements)} movements")
    except Exception as e:
        print(f"   ✗ Error fetching movements: {e}")
        return

    # Display first few movements
    if movements:
        print("\n   First 3 movements:")
        for i, movement in enumerate(movements[:3], 1):
            entry_date = movement.get("dataIngresso")
            exit_data = movement.get("dataUscita", "N/A")
            amount = movement.get("saldo", "N/A")
            entry_point = movement.get("inizioTratta", "N/A")
            exit_point = movement.get("fineTratta", "N/A")
            print(f"   {i}. {entry_date or exit_data}: {entry_point} → {exit_point} ({amount} EUR)")

    # Filter by date range (example: current month)
    print("\n4. Filtering movements by date range...")
    today = date.today()
    start_of_month = date(today.year, today.month, 1)
    filtered_movements = client.filter_movements_by_date(
        movements, start_date=start_of_month, end_date=today
    )
    print(f"   ✓ Found {len(filtered_movements)} movements in current month")
    print(f"   Date range: {start_of_month} to {today}")

    # Generate PDF report
    if filtered_movements:
        print(f"\n5. Generating PDF report for {len(filtered_movements)} movements...")
        output_filename = f"expense_report_{today.strftime('%Y%m%d')}.pdf"

        try:
            pdf_bytes = client.generate_pdf_report(
                movements=filtered_movements,
                intestatario=recipient,
                output_filename=output_filename,
            )
            print(f"   ✓ PDF report generated successfully!")
            print(f"   File: {output_filename}")
            print(f"   Size: {len(pdf_bytes):,} bytes")
        except Exception as e:
            print(f"   ✗ Error generating PDF: {e}")
    else:
        print("\n5. No movements found for current month - skipping PDF generation")

    # Example: Fetch single page of movements
    print("\n6. Example: Fetching single page (first 10 movements)...")
    try:
        page = client.fetch_movements(offset=1, limit=10, interval="ULTIMO_ANNO")
        movements_count = len(page.get("listaMovimenti", []))
        print(f"   ✓ Fetched {movements_count} movements")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    print("\n" + "=" * 50)
    print("Example completed successfully!")
    print("\nNext steps:")
    print("- Set environment variables: UNIPOL_CONTRACT_ID, UNIPOL_USERNAME, UNIPOL_PASSWORD")
    print("- Customize date ranges and filters")
    print("- Integrate into your expense reporting workflow")


if __name__ == "__main__":
    main()
