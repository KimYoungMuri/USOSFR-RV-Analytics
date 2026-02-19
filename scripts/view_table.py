"""
Simple script to view Swaption Vol Table for any date

Usage:
    python view_table.py                    # Uses latest available date
    python view_table.py 2024-12-31        # Uses specific date
"""
import sys
from pathlib import Path
from datetime import date, datetime
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.get_swaption_table import get_swaption_table, get_swaption_table_latest

# Get date from command line or use latest
if len(sys.argv) > 1:
    try:
        as_of_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
        print(f"Using date: {as_of_date}")
    except ValueError:
        print(f"Error: Invalid date format. Use YYYY-MM-DD (e.g., 2024-12-31)")
        sys.exit(1)
else:
    print("No date provided, using latest available date...")
    table = get_swaption_table_latest()
    as_of_date = table.attrs.get('as_of_date', 'latest') if hasattr(table, 'attrs') else 'latest'
    print(f"Latest date available")

# Build table
print(f"\nBuilding Swaption Vol Table for {as_of_date}...")
table = get_swaption_table(as_of_date) if isinstance(as_of_date, date) else get_swaption_table_latest()

print(f"\n✓ Table ready: {len(table)} rows\n")

# Display options
print("=" * 100)
print("SWAPTION VOL TABLE")
print("=" * 100)
print(f"\nAs of: {as_of_date if isinstance(as_of_date, date) else 'latest'}")
print(f"{len(table)} swaption combinations\n")

# Show formatted sections
print("-" * 100)
print("IMPLIED VOL (ANNUALIZED BP VOL)")
print("-" * 100)
cols_ann = ['term_tenor', 'implied_vol_ann_current', 'implied_vol_ann_1d_chg', 
            'implied_vol_ann_1w_chg', 'implied_vol_ann_1m_chg', 
            'implied_vol_ann_20d_high', 'implied_vol_ann_20d_low']
print(table[cols_ann].to_string(index=False))

print("\n\n" + "-" * 100)
print("IMPLIED VOL (DAILY BP VOL)")
print("-" * 100)
cols_daily = ['term_tenor', 'implied_vol_daily_current', 'implied_vol_daily_1d_chg',
              'implied_vol_daily_1w_chg', 'implied_vol_daily_1m_chg',
              'implied_vol_daily_20d_high', 'implied_vol_daily_20d_low']
print(table[cols_daily].to_string(index=False))

print("\n\n" + "-" * 100)
print("REALIZED VOL (BP VOL)")
print("-" * 100)
cols_realized = ['term_tenor', 'realized_vol_10d', 'realized_vol_20d', 'realized_vol_60d',
                 'realized_vol_90d', 'realized_vol_120d', 'realized_vol_180d']
print(table[cols_realized].to_string(index=False))

# Show specific swaption
print("\n\n" + "-" * 100)
print("SAMPLE: 1M × 2Y")
print("-" * 100)
sample = table[table['term_tenor'] == '1M × 2Y']
if len(sample) > 0:
    row = sample.iloc[0]
    print(f"\nImplied Vol (Annualized):")
    print(f"  Current: {row['implied_vol_ann_current']:.2f} bp")
    print(f"  1d Chg: {row['implied_vol_ann_1d_chg']:+.2f} bp")
    print(f"  1w Chg: {row['implied_vol_ann_1w_chg']:+.2f} bp")
    print(f"  1m Chg: {row['implied_vol_ann_1m_chg']:+.2f} bp")
    print(f"  20d High: {row['implied_vol_ann_20d_high']:.2f} bp")
    print(f"  20d Low: {row['implied_vol_ann_20d_low']:.2f} bp")
    
    print(f"\nImplied Vol (Daily):")
    print(f"  Current: {row['implied_vol_daily_current']:.2f} bp")
    print(f"  1d Chg: {row['implied_vol_daily_1d_chg']:+.2f} bp")
    print(f"  1w Chg: {row['implied_vol_daily_1w_chg']:+.2f} bp")
    print(f"  1m Chg: {row['implied_vol_daily_1m_chg']:+.2f} bp")
    
    print(f"\nRealized Vol (Daily):")
    for window in [10, 20, 60, 90, 120, 180]:
        col = f"realized_vol_{window}d"
        val = row[col]
        print(f"  {window}d: {val:.2f} bp" if not pd.isna(val) else f"  {window}d: N/A")

# Save to CSV
output_dir = Path(__file__).parent.parent / "outputs" / "tables"
output_dir.mkdir(parents=True, exist_ok=True)
csv_file = output_dir / f'swaption_vol_table_{as_of_date if isinstance(as_of_date, date) else "latest"}.csv'
table.to_csv(csv_file, index=False)
print(f"\n\n✓ Saved to: {csv_file}")

print("\n" + "=" * 100)
print("Usage in Python:")
print("=" * 100)
print("""
from src.modules.get_swaption_table import get_swaption_table
from datetime import date

# Get table for specific date
table = get_swaption_table(date(2024, 12, 31))

# Or get latest
from src.modules.get_swaption_table import get_swaption_table_latest
table = get_swaption_table_latest()

# View it
print(table)

# Filter
print(table[table['term_tenor'] == '1M × 2Y'])

# Export
table.to_csv('my_table.csv', index=False)
""")
