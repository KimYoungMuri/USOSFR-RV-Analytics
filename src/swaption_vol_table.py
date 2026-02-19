"""
Swaption Vol Table Builder
"""
import pandas as pd
import numpy as np
from datetime import date

from src.config import OPTION_TENORS, SWAP_TENORS, REALIZED_VOL_WINDOWS


def compute_implied_vol_changes(vol_data, as_of_date):
    """Compute implied vol changes and stats"""
    vol_data = vol_data[vol_data['date'] <= as_of_date].copy()
    vol_data = vol_data.sort_values(['date', 'expiry', 'tenor'])
    
    results = []
    
    for (expiry, tenor), group in vol_data.groupby(['expiry', 'tenor']):
        if len(group) < 5:
            continue
        
        vol_series = group.set_index('date')['implied_bpvol_annualized'].sort_index()
        
        current_vol = vol_series.iloc[-1]
        
        # Changes
        change_1d = vol_series.iloc[-1] - vol_series.iloc[-2] if len(vol_series) >= 2 else np.nan
        change_1w = vol_series.iloc[-1] - vol_series.iloc[-6] if len(vol_series) >= 6 else np.nan
        change_1m = vol_series.iloc[-1] - vol_series.iloc[-21] if len(vol_series) >= 21 else np.nan
        
        # 20-day rolling stats
        last_20d = vol_series.tail(20)
        high_20d = last_20d.max() if len(last_20d) > 0 else np.nan
        low_20d = last_20d.min() if len(last_20d) > 0 else np.nan
        
        results.append({
            'expiry': expiry,
            'tenor': tenor,
            'implied_vol_ann_current': current_vol,
            'implied_vol_ann_1d_chg': change_1d,
            'implied_vol_ann_1w_chg': change_1w,
            'implied_vol_ann_1m_chg': change_1m,
            'implied_vol_ann_20d_high': high_20d,
            'implied_vol_ann_20d_low': low_20d,
        })
    
    return pd.DataFrame(results)


def compute_realized_vol(swap_rates, as_of_date, windows=[10, 20, 60, 90, 120, 180]):
    """Compute realized volatility from swap rates"""
    swap_rates = swap_rates[swap_rates['date'] <= as_of_date].copy()
    swap_rates = swap_rates.sort_values(['date', 'tenor'])
    
    results = []
    
    for tenor, group in swap_rates.groupby('tenor'):
        if len(group) < max(windows):
            continue
        
        rate_series = group.set_index('date')['swap_rate'].sort_index()
        
        # Daily changes in bp (assuming rates are in percentage)
        daily_changes_bp = (rate_series - rate_series.shift(1)) * 100
        
        row = {'tenor': tenor}
        for window in windows:
            if len(daily_changes_bp) >= window:
                rolling_std = daily_changes_bp.rolling(window=window, min_periods=window//2).std()
                realized_vol = rolling_std.iloc[-1] * np.sqrt(252)
                row[f'realized_vol_{window}d'] = realized_vol
            else:
                row[f'realized_vol_{window}d'] = np.nan
        
        results.append(row)
    
    return pd.DataFrame(results)


def build_swaption_vol_table(vol_data, swap_rates, as_of_date):
    """Build complete Swaption Vol Table"""
    implied_df = compute_implied_vol_changes(vol_data, as_of_date)
    realized_df = compute_realized_vol(swap_rates, as_of_date)
    
    # Add daily implied vol columns
    implied_df['implied_vol_daily_current'] = implied_df['implied_vol_ann_current'] / np.sqrt(252)
    implied_df['implied_vol_daily_1d_chg'] = implied_df['implied_vol_ann_1d_chg'] / np.sqrt(252)
    implied_df['implied_vol_daily_1w_chg'] = implied_df['implied_vol_ann_1w_chg'] / np.sqrt(252)
    implied_df['implied_vol_daily_1m_chg'] = implied_df['implied_vol_ann_1m_chg'] / np.sqrt(252)
    implied_df['implied_vol_daily_20d_high'] = implied_df['implied_vol_ann_20d_high'] / np.sqrt(252)
    implied_df['implied_vol_daily_20d_low'] = implied_df['implied_vol_ann_20d_low'] / np.sqrt(252)
    
    result = implied_df.merge(realized_df, on='tenor', how='left')
    result['term_tenor'] = result['expiry'].astype(str) + ' × ' + result['tenor'].astype(str) + 'Y'
    
    # Filter to key grid
    result = result[result['expiry'].isin(OPTION_TENORS)]
    result = result[result['tenor'].isin(SWAP_TENORS)]
    
    # Reorder columns
    cols = [
        'expiry', 'tenor', 'term_tenor',
        'implied_vol_ann_current', 'implied_vol_ann_1d_chg', 'implied_vol_ann_1w_chg', 
        'implied_vol_ann_1m_chg', 'implied_vol_ann_20d_high', 'implied_vol_ann_20d_low',
        'implied_vol_daily_current', 'implied_vol_daily_1d_chg', 'implied_vol_daily_1w_chg',
        'implied_vol_daily_1m_chg', 'implied_vol_daily_20d_high', 'implied_vol_daily_20d_low',
        'realized_vol_10d', 'realized_vol_20d', 'realized_vol_60d',
        'realized_vol_90d', 'realized_vol_120d', 'realized_vol_180d'
    ]
    cols = [c for c in cols if c in result.columns]
    result = result[cols]
    
    result = add_highlighting_flags(result, vol_data, as_of_date)
    
    # Sort by expiry then tenor
    expiry_order = {exp: i for i, exp in enumerate(OPTION_TENORS)}
    result['expiry_order'] = result['expiry'].map(expiry_order)
    result = result.sort_values(['expiry_order', 'tenor']).reset_index(drop=True)
    result = result.drop(columns=['expiry_order'])
    
    return result


def add_highlighting_flags(table, vol_data, as_of_date):
    """Add flags for largest movers"""
    table = table.copy()
    vol_data = vol_data[vol_data['date'] <= as_of_date].copy()
    vol_data = vol_data.sort_values(['date', 'expiry', 'tenor'])
    
    table['is_largest_1d_mover'] = False
    table['is_largest_1w_mover'] = False
    table['is_largest_1m_mover'] = False
    
    for (expiry, tenor), group in vol_data.groupby(['expiry', 'tenor']):
        if len(group) < 21:
            continue
        
        vol_series = group.set_index('date')['implied_bpvol_annualized'].sort_index()
        
        row_idx = table[(table['expiry'] == expiry) & (table['tenor'] == tenor)].index
        if len(row_idx) == 0:
            continue
        row_idx = row_idx[0]
        
        # 1d movers: largest 1d change in last 10 days
        if len(vol_series) >= 11:
            last_10d_1d_changes = []
            for i in range(len(vol_series) - 10, len(vol_series)):
                if i >= 1:
                    change = vol_series.iloc[i] - vol_series.iloc[i-1]
                    last_10d_1d_changes.append(abs(change))
            
            if last_10d_1d_changes:
                max_1d_change = max(last_10d_1d_changes)
                current_1d_change = abs(table.loc[row_idx, 'implied_vol_ann_1d_chg'])
                if not pd.isna(current_1d_change) and current_1d_change == max_1d_change:
                    table.loc[row_idx, 'is_largest_1d_mover'] = True
        
        # 1w movers: largest 1w change in last 20 days
        if len(vol_series) >= 26:
            last_20d_1w_changes = []
            for i in range(len(vol_series) - 20, len(vol_series)):
                if i >= 5:
                    change = vol_series.iloc[i] - vol_series.iloc[i-5]
                    last_20d_1w_changes.append(abs(change))
            
            if last_20d_1w_changes:
                max_1w_change = max(last_20d_1w_changes)
                current_1w_change = abs(table.loc[row_idx, 'implied_vol_ann_1w_chg'])
                if not pd.isna(current_1w_change) and current_1w_change == max_1w_change:
                    table.loc[row_idx, 'is_largest_1w_mover'] = True
        
        # 1m movers: largest 1m change in last 120 days
        if len(vol_series) >= 141:
            last_120d_1m_changes = []
            for i in range(len(vol_series) - 120, len(vol_series)):
                if i >= 20:
                    change = vol_series.iloc[i] - vol_series.iloc[i-20]
                    last_120d_1m_changes.append(abs(change))
            
            if last_120d_1m_changes:
                max_1m_change = max(last_120d_1m_changes)
                current_1m_change = abs(table.loc[row_idx, 'implied_vol_ann_1m_chg'])
                if not pd.isna(current_1m_change) and current_1m_change == max_1m_change:
                    table.loc[row_idx, 'is_largest_1m_mover'] = True
    
    return table
