"""
Test the simple swaption vol table builder
"""
import sys
from pathlib import Path
from datetime import date
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from src.modules.swaption_vol_table import build_swaption_vol_table
from src.data.data_loader import VolCube420Loader, SOFRLoader

print("=" * 80)
print("Building Swaption Vol Table")
print("=" * 80)

# Load data
print("\n1. Loading VolCube420 data...")
vol_loader = VolCube420Loader()

# Load all years from 2017-2024
all_vol_data = []
for year in range(2017, 2025):
    try:
        year_data = vol_loader.load_atm_timeseries(year)
        all_vol_data.append(year_data)
        print(f"   ✓ Loaded {year}: {len(year_data)} rows")
    except Exception as e:
        print(f"   ✗ Failed {year}: {e}")

if not all_vol_data:
    print("ERROR: No vol data loaded!")
    sys.exit(1)

vol_data = pd.concat(all_vol_data, ignore_index=True)
print(f"\n   Total vol data: {len(vol_data)} rows")
print(f"   Date range: {vol_data['date'].min()} to {vol_data['date'].max()}")

# Rename columns to match expected format
vol_data = vol_data.rename(columns={
    'option_tenor': 'expiry',
    'swap_tenor': 'tenor',
    'normal_vol': 'implied_bpvol_annualized'
})

print(f"\n   Columns: {vol_data.columns.tolist()}")
print(f"   Unique expiries: {sorted(vol_data['expiry'].unique())}")
print(f"   Unique tenors: {sorted(vol_data['tenor'].unique())}")

print("\n2. Loading SOFR swap rates...")
sofr_loader = SOFRLoader()
swap_rates = sofr_loader.load_all_sofr_rates()
print(f"   Total SOFR data: {len(swap_rates)} rows")
print(f"   Date range: {swap_rates['date'].min()} to {swap_rates['date'].max()}")

# Rename to match expected format
swap_rates = swap_rates.rename(columns={'rate': 'swap_rate'})
print(f"   Columns: {swap_rates.columns.tolist()}")

# Build table
print("\n3. Building Swaption Vol Table...")
as_of_date = date(2024, 12, 31)
table = build_swaption_vol_table(vol_data, swap_rates, as_of_date)

print(f"\n✓ Table built: {table.shape}")
print(f"\nColumns: {table.columns.tolist()}")

# Display table
print("\n" + "=" * 80)
print("SWAPTION VOL TABLE")
print("=" * 80)
print(f"\nAs of: {as_of_date}")
print(f"\n{len(table)} swaption combinations")

# Show formatted output
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', 15)

print("\n" + "-" * 80)
print("IMPLIED VOL (ANNUALIZED BP VOL)")
print("-" * 80)
print(table[['term_tenor', 'implied_vol_ann_current', 'implied_vol_ann_1d_chg', 
            'implied_vol_ann_1w_chg', 'implied_vol_ann_1m_chg', 
            'implied_vol_ann_20d_high', 'implied_vol_ann_20d_low']].to_string(index=False))

print("\n" + "-" * 80)
print("IMPLIED VOL (DAILY BP VOL)")
print("-" * 80)
print(table[['term_tenor', 'implied_vol_daily_current', 'implied_vol_daily_1d_chg',
            'implied_vol_daily_1w_chg', 'implied_vol_daily_1m_chg',
            'implied_vol_daily_20d_high', 'implied_vol_daily_20d_low']].to_string(index=False))

print("\n" + "-" * 80)
print("REALIZED VOL (BP VOL)")
print("-" * 80)
print(table[['term_tenor', 'realized_vol_10d', 'realized_vol_20d', 'realized_vol_60d',
            'realized_vol_90d', 'realized_vol_120d', 'realized_vol_180d']].to_string(index=False))

print("\n" + "-" * 80)
print("HIGHLIGHTING FLAGS")
print("-" * 80)
movers = table[table['is_largest_1d_mover'] | table['is_largest_1w_mover'] | table['is_largest_1m_mover']]
if len(movers) > 0:
    print(movers[['term_tenor', 'is_largest_1d_mover', 'is_largest_1w_mover', 'is_largest_1m_mover']].to_string(index=False))
else:
    print("No largest movers identified")

print("\n" + "=" * 80)
print("Sample row (1M × 2Y):")
print("=" * 80)
sample = table[table['term_tenor'] == '1M × 2Y']
if len(sample) > 0:
    print(sample.iloc[0].to_dict())
