"""
Simple function to get Swaption Vol Table for any date

Usage:
    from src.modules.get_swaption_table import get_swaption_table
    from datetime import date
    
    table = get_swaption_table(date(2024, 12, 31))
    print(table)
"""
import sys
from pathlib import Path

# Add parent directory to path if running as script
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pandas as pd
from datetime import date
from typing import Optional

from src.modules.swaption_vol_table import build_swaption_vol_table
from src.data.data_loader import VolCube420Loader, SOFRLoader
from src.reporting.excel_formatter import format_swaption_vol_table_excel


# Cache data loaders
_vol_loader = None
_sofr_loader = None
_vol_data_cache = None
_swap_rates_cache = None


def _load_data():
    """Load and cache vol and SOFR data"""
    global _vol_loader, _sofr_loader, _vol_data_cache, _swap_rates_cache
    
    if _vol_data_cache is None or _swap_rates_cache is None:
        print("Loading data (first time only, will cache)...")
        
        _vol_loader = VolCube420Loader()
        _sofr_loader = SOFRLoader()
        
        # Load vol data (2017-2024)
        all_vol_data = []
        for year in range(2017, 2025):
            try:
                year_data = _vol_loader.load_atm_timeseries(year)
                all_vol_data.append(year_data)
            except:
                pass
        
        if not all_vol_data:
            raise ValueError("No vol data loaded")
        
        _vol_data_cache = pd.concat(all_vol_data, ignore_index=True)
        _vol_data_cache = _vol_data_cache.rename(columns={
            'option_tenor': 'expiry',
            'swap_tenor': 'tenor',
            'normal_vol': 'implied_bpvol_annualized'
        })
        
        # Load SOFR rates
        _swap_rates_cache = _sofr_loader.load_all_sofr_rates()
        _swap_rates_cache = _swap_rates_cache.rename(columns={'rate': 'swap_rate'})
        
        print(f"✓ Loaded {len(_vol_data_cache)} vol data points")
        print(f"✓ Loaded {len(_swap_rates_cache)} SOFR data points")
    
    return _vol_data_cache, _swap_rates_cache


def get_swaption_table(as_of_date: date) -> pd.DataFrame:
    """
    Get Swaption Vol Table for a specific date
    
    Args:
        as_of_date: Date to build table for (must be between 2017-01-01 and 2024-12-31)
        
    Returns:
        DataFrame with Swaption Vol Table
        
    Example:
        >>> from datetime import date
        >>> table = get_swaption_table(date(2024, 12, 31))
        >>> print(table)
    """
    # Load data (cached after first call)
    vol_data, swap_rates = _load_data()
    
    # Validate date
    min_date = vol_data['date'].min()
    max_date = vol_data['date'].max()
    
    if as_of_date < min_date:
        raise ValueError(f"Date {as_of_date} is before earliest data: {min_date}")
    if as_of_date > max_date:
        raise ValueError(f"Date {as_of_date} is after latest data: {max_date}")
    
    # Build table
    table = build_swaption_vol_table(vol_data, swap_rates, as_of_date)
    
    return table


def get_swaption_table_excel(
    as_of_date: date,
    output_file: Optional[str] = None
) -> str:
    """
    Get Swaption Vol Table and export to Excel with Nomura-style formatting
    
    Args:
        as_of_date: Date to build table for
        output_file: Output filename (default: swaption_vol_table_YYYY-MM-DD.xlsx)
        
    Returns:
        Path to created Excel file
        
    Example:
        >>> from datetime import date
        >>> excel_file = get_swaption_table_excel(date(2024, 12, 31))
        >>> print(f"Saved to: {excel_file}")
    """
    table = get_swaption_table(as_of_date)
    return format_swaption_vol_table_excel(table, as_of_date, output_file)


def get_swaption_table_latest() -> pd.DataFrame:
    """
    Get Swaption Vol Table for the latest available date
    
    Returns:
        DataFrame with Swaption Vol Table
    """
    vol_data, _ = _load_data()
    latest_date = vol_data['date'].max()
    return get_swaption_table(latest_date)


if __name__ == "__main__":
    from datetime import datetime
    
    # Command line usage
    if len(sys.argv) > 1:
        # Date provided as argument (format: YYYY-MM-DD)
        date_str = sys.argv[1]
        try:
            as_of_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print(f"Error: Invalid date format. Use YYYY-MM-DD (e.g., 2024-12-31)")
            sys.exit(1)
    else:
        # Use latest date
        print("No date provided, using latest available date...")
        vol_data, _ = _load_data()
        as_of_date = vol_data['date'].max()
        print(f"Latest date: {as_of_date}")
    
    # Get table
    print(f"\nBuilding Swaption Vol Table for {as_of_date}...")
    table = get_swaption_table(as_of_date)
    
    print(f"\n✓ Table ready: {len(table)} rows")
    print(f"\nColumns: {table.columns.tolist()}")
    print(f"\nFirst few rows:")
    print(table.head(10))
    
    # Save to CSV
    csv_file = f'swaption_vol_table_{as_of_date}.csv'
    table.to_csv(csv_file, index=False)
    print(f"\n✓ Saved to: {csv_file}")
