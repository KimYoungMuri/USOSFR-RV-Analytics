"""
Data loaders for VolCube420 and SOFR swap rate data
"""
import pandas as pd
import numpy as np
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, date
import warnings

from src.utils.config import (
    HISTORICAL_DATA_DIR,
    SOFR_FILES,
    VOLCUBE420_ATM_TIMESERIES_URL,
    OPTION_TENORS,
    SWAP_TENORS,
)


class VolCube420Loader:
    """Loader for VolCube420 ATM timeseries data"""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path("data/raw/volcube420")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def load_atm_timeseries(self, year: int = 2024) -> pd.DataFrame:
        """
        Load ATM timeseries data from VolCube420 GitHub repo
        
        Args:
            year: Year to load (default: 2024)
            
        Returns:
            DataFrame with columns: date, option_tenor, swap_tenor, normal_vol
        """
        url = f"{VOLCUBE420_ATM_TIMESERIES_URL}/{year}.json"
        cache_file = self.cache_dir / f"atm_timeseries_{year}.json"
        
        # Try to load from cache first
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                data = json.load(f)
        else:
            # Download from GitHub
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                # Cache it
                with open(cache_file, 'w') as f:
                    json.dump(data, f)
            except Exception as e:
                raise ValueError(f"Failed to load VolCube420 data: {e}")
        
        # Parse JSON structure
        # Format: {date: [{Option Tenor, 1Y, 2Y, ...}, ...]}
        records = []
        for date_str, swaptions in data.items():
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                continue
            
            for swaption in swaptions:
                option_tenor = swaption.get("Option Tenor", "")
                if not option_tenor:
                    continue
                
                # Extract swap tenors and vols
                for swap_tenor_str, vol in swaption.items():
                    if swap_tenor_str == "Option Tenor":
                        continue
                    
                    try:
                        # Convert swap tenor string to integer
                        swap_tenor = int(swap_tenor_str.replace("Y", ""))
                        if swap_tenor in SWAP_TENORS:
                            records.append({
                                "date": dt,
                                "option_tenor": option_tenor,
                                "swap_tenor": swap_tenor,
                                "normal_vol": vol,
                            })
                    except (ValueError, AttributeError):
                        continue
        
        df = pd.DataFrame(records)
        if df.empty:
            raise ValueError(f"No data found for year {year}")
        
        df = df.sort_values(["date", "option_tenor", "swap_tenor"])
        return df
    
    def load_latest_atm_vol(self, date: Optional[date] = None) -> pd.DataFrame:
        """
        Load latest ATM vol data
        
        Args:
            date: Specific date to load (default: latest available)
            
        Returns:
            DataFrame with current ATM vols
        """
        # Try current year first
        current_year = datetime.now().year
        try:
            df = self.load_atm_timeseries(current_year)
        except:
            # Try previous year
            df = self.load_atm_timeseries(current_year - 1)
        
        if date:
            df = df[df["date"] == date]
        else:
            # Get latest date
            latest_date = df["date"].max()
            df = df[df["date"] == latest_date]
        
        return df


class SOFRLoader:
    """Loader for SOFR swap rate historical data"""
    
    def __init__(self):
        self.sofr_files = SOFR_FILES
    
    def load_sofr_rates(self, tenor: int) -> pd.DataFrame:
        """
        Load SOFR swap rate data for a specific tenor
        
        Args:
            tenor: Swap tenor in years (1, 2, 3, 5, 7, 10, 15, 20, 30)
            
        Returns:
            DataFrame with columns: date, rate
        """
        if tenor not in self.sofr_files:
            raise ValueError(f"Tenor {tenor} not available. Available: {list(self.sofr_files.keys())}")
        
        file_path = self.sofr_files[tenor]
        if not file_path.exists():
            raise FileNotFoundError(f"SOFR file not found: {file_path}")
        
        # Read Excel file
        # Try different possible column names
        df = pd.read_excel(file_path)
        
        # Standardize column names
        # Common formats: Date/date/DATE, Rate/rate/RATE/Close/close
        date_col = None
        rate_col = None
        
        for col in df.columns:
            col_lower = str(col).lower()
            if 'date' in col_lower:
                date_col = col
            elif any(x in col_lower for x in ['rate', 'close', 'price', 'value']):
                rate_col = col
        
        if date_col is None or rate_col is None:
            # Try first two columns
            if len(df.columns) >= 2:
                date_col = df.columns[0]
                rate_col = df.columns[1]
            else:
                raise ValueError(f"Cannot parse SOFR file {file_path}. Columns: {df.columns.tolist()}")
        
        # Extract and clean data
        # Convert date column, handling errors and skipping header rows
        dates = []
        rates = []
        
        for idx, row in df.iterrows():
            date_val = row[date_col]
            rate_val = row[rate_col]
            
            # Skip if date is a string header (like "Start Date")
            if isinstance(date_val, str) and any(x in date_val.lower() for x in ['date', 'start', 'end']):
                continue
            
            # Try to parse date
            try:
                if pd.isna(date_val):
                    continue
                parsed_date = pd.to_datetime(date_val, errors='coerce')
                if pd.isna(parsed_date):
                    continue
                dates.append(parsed_date.date())
                
                # Parse rate
                rate_num = pd.to_numeric(rate_val, errors='coerce')
                if pd.isna(rate_num):
                    continue
                rates.append(rate_num)
            except:
                continue
        
        # Create result DataFrame
        if not dates:
            raise ValueError(f"No valid data found in {file_path}")
        
        result = pd.DataFrame({
            "date": dates,
            "rate": rates,
            "tenor": tenor
        })
        
        # Remove any remaining rows with missing data
        result = result.dropna(subset=['date', 'rate'])
        result = result.sort_values('date')
        
        return result
    
    def load_all_sofr_rates(self) -> pd.DataFrame:
        """
        Load all available SOFR swap rate data
        
        Returns:
            DataFrame with columns: date, tenor, rate
        """
        all_data = []
        for tenor in sorted(self.sofr_files.keys()):
            try:
                df = self.load_sofr_rates(tenor)
                all_data.append(df)
            except Exception as e:
                warnings.warn(f"Failed to load SOFR {tenor}yr: {e}")
        
        if not all_data:
            raise ValueError("No SOFR data loaded")
        
        combined = pd.concat(all_data, ignore_index=True)
        return combined


def load_vol_surface_data(as_of_date: Optional[date] = None) -> pd.DataFrame:
    """
    Convenience function to load current vol surface data
    
    Args:
        as_of_date: Specific date (default: latest)
        
    Returns:
        DataFrame with vol surface data
    """
    loader = VolCube420Loader()
    return loader.load_latest_atm_vol(as_of_date)


def load_sofr_data(tenors: Optional[List[int]] = None) -> pd.DataFrame:
    """
    Convenience function to load SOFR swap rate data
    
    Args:
        tenors: List of tenors to load (default: all available)
        
    Returns:
        DataFrame with SOFR rates
    """
    loader = SOFRLoader()
    if tenors:
        all_data = []
        for tenor in tenors:
            df = loader.load_sofr_rates(tenor)
            all_data.append(df)
        return pd.concat(all_data, ignore_index=True)
    else:
        return loader.load_all_sofr_rates()
