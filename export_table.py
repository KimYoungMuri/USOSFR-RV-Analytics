"""
Export Swaption Vol Table to Excel with Nomura-style formatting

Usage:
    python export_table.py 2024-12-31
    python export_table.py                    # Uses latest date
"""
import sys
from pathlib import Path
from datetime import date, datetime

sys.path.insert(0, str(Path(__file__).parent))

from src.modules.get_swaption_table import get_swaption_table_excel, get_swaption_table_latest

# Get date from command line or use latest
if len(sys.argv) > 1:
    try:
        as_of_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
        print(f"Exporting table for date: {as_of_date}")
    except ValueError:
        print(f"Error: Invalid date format. Use YYYY-MM-DD (e.g., 2024-12-31)")
        sys.exit(1)
else:
    print("No date provided, using latest available date...")
    from src.modules.get_swaption_table import _load_data
    vol_data, _ = _load_data()
    as_of_date = vol_data['date'].max()
    print(f"Latest date: {as_of_date}")

# Export to Excel
print(f"\nBuilding and formatting table...")
excel_file = get_swaption_table_excel(as_of_date)

print(f"\n✓ Excel file created: {excel_file}")
print(f"\nOpen the file to view the formatted table with:")
print(f"  - Nomura-style formatting")
print(f"  - Color-coded largest movers (dark gray)")
print(f"  - Negative values in parentheses")
print(f"  - Professional layout")
