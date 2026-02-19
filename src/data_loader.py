"""
Data loaders for VolCube420 and SOFR swap rate data
"""
import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime, date
import warnings

from src.config import HISTORICAL_DATA_DIR, SOFR_FILES, OPTION_TENORS, SWAP_TENORS


class VolCube420Loader:
    """Load VolCube420 ATM timeseries from local JSON files"""
    
    def __init__(self, cache_dir=None):
        self.cache_dir = cache_dir or Path("data/raw/volcube420")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def load_atm_timeseries(self, year=2024):
        """Load ATM timeseries for a year from local cache"""
        cache_file = self.cache_dir / f"atm_timeseries_{year}.json"
        
        if not cache_file.exists():
            raise FileNotFoundError(f"VolCube420 data file not found: {cache_file}")
        
        with open(cache_file, 'r') as f:
            data = json.load(f)
        
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
                
                for swap_tenor_str, vol in swaption.items():
                    if swap_tenor_str == "Option Tenor":
                        continue
                    
                    try:
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
        
        return df.sort_values(["date", "option_tenor", "swap_tenor"])
    
    def load_latest_atm_vol(self, date=None):
        """Load latest ATM vol data"""
        current_year = datetime.now().year
        try:
            df = self.load_atm_timeseries(current_year)
        except:
            df = self.load_atm_timeseries(current_year - 1)
        
        if date:
            df = df[df["date"] == date]
        else:
            latest_date = df["date"].max()
            df = df[df["date"] == latest_date]
        
        return df


class SOFRLoader:
    """Load SOFR swap rate data from Excel files"""
    
    def __init__(self):
        self.sofr_files = SOFR_FILES
    
    def load_sofr_rates(self, tenor):
        """Load SOFR rates for a specific tenor"""
        if tenor not in self.sofr_files:
            raise ValueError(f"Tenor {tenor} not available")
        
        file_path = self.sofr_files[tenor]
        if not file_path.exists():
            raise FileNotFoundError(f"SOFR file not found: {file_path}")
        
        df = pd.read_excel(file_path)
        
        # Find date and rate columns
        date_col = None
        rate_col = None
        
        for col in df.columns:
            col_lower = str(col).lower()
            if 'date' in col_lower:
                date_col = col
            elif any(x in col_lower for x in ['rate', 'close', 'price', 'value']):
                rate_col = col
        
        if date_col is None or rate_col is None:
            if len(df.columns) >= 2:
                date_col = df.columns[0]
                rate_col = df.columns[1]
            else:
                raise ValueError(f"Cannot parse SOFR file {file_path}")
        
        # Extract data
        dates = []
        rates = []
        
        for idx, row in df.iterrows():
            date_val = row[date_col]
            rate_val = row[rate_col]
            
            if isinstance(date_val, str) and any(x in date_val.lower() for x in ['date', 'start', 'end']):
                continue
            
            try:
                if pd.isna(date_val):
                    continue
                parsed_date = pd.to_datetime(date_val, errors='coerce')
                if pd.isna(parsed_date):
                    continue
                dates.append(parsed_date.date())
                
                rate_num = pd.to_numeric(rate_val, errors='coerce')
                if pd.isna(rate_num):
                    continue
                rates.append(rate_num)
            except:
                continue
        
        if not dates:
            raise ValueError(f"No valid data found in {file_path}")
        
        result = pd.DataFrame({"date": dates, "rate": rates, "tenor": tenor})
        result = result.dropna(subset=['date', 'rate']).sort_values('date')
        return result
    
    def load_all_sofr_rates(self):
        """Load all available SOFR rates"""
        all_data = []
        for tenor in sorted(self.sofr_files.keys()):
            try:
                df = self.load_sofr_rates(tenor)
                all_data.append(df)
            except Exception as e:
                warnings.warn(f"Failed to load SOFR {tenor}yr: {e}")
        
        if not all_data:
            raise ValueError("No SOFR data loaded")
        
        return pd.concat(all_data, ignore_index=True)


def load_vol_surface_data(as_of_date=None):
    """Load current vol surface data"""
    loader = VolCube420Loader()
    return loader.load_latest_atm_vol(as_of_date)


def load_sofr_data(tenors=None):
    """Load SOFR swap rate data"""
    loader = SOFRLoader()
    if tenors:
        all_data = []
        for tenor in tenors:
            df = loader.load_sofr_rates(tenor)
            all_data.append(df)
        return pd.concat(all_data, ignore_index=True)
    else:
        return loader.load_all_sofr_rates()
