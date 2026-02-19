"""
Volatility calculations
"""
import pandas as pd
import numpy as np

from src.config import TRADING_DAYS_PER_YEAR, REALIZED_VOL_WINDOWS


def calculate_realized_vol(rates, window, annualize=True, rates_in_percent=True):
    """Calculate realized vol from swap rates in basis points"""
    rates_clean = rates[rates > 0].copy()
    
    if len(rates_clean) < 2:
        return pd.Series(index=rates.index, dtype=float)
    
    # Daily changes in bp
    if rates_in_percent: daily_changes_bp = (rates_clean - rates_clean.shift(1)) * 100
    else: daily_changes_bp = (rates_clean - rates_clean.shift(1)) * 10000
    
    daily_changes_bp = daily_changes_bp.replace([np.inf, -np.inf], np.nan)
    rolling_std_bp = daily_changes_bp.rolling(window=window, min_periods=min(5, window//2)).std()
    
    if annualize: realized_vol = rolling_std_bp * np.sqrt(TRADING_DAYS_PER_YEAR)
    else: realized_vol = rolling_std_bp
    
    return realized_vol.reindex(rates.index)


def calculate_realized_vol_multiple_windows(rates, windows=None, rates_in_percent=True, annualize=True):
    """Calculate realized vol for multiple windows"""
    if windows is None:
        windows = REALIZED_VOL_WINDOWS
    
    result = pd.DataFrame(index=rates.index)
    
    for window in windows:
        result[f"realized_vol_{window}d"] = calculate_realized_vol(rates, window, rates_in_percent=rates_in_percent, annualize=annualize)
    
    return result


def calculate_changes(data, periods=[1, 5, 20]):
    """Calculate changes over different periods (1d, 1w, 1m)"""
    result = pd.DataFrame(index=data.index)
    for period in periods:
        result[f"change_{period}d"] = data - data.shift(period)
    return result


def calculate_rolling_stats(data, window=20):
    """Calculate rolling mean, std, min, max"""
    result = pd.DataFrame(index=data.index)
    result["mean"] = data.rolling(window=window, min_periods=window//2).mean()
    result["std"] = data.rolling(window=window, min_periods=window//2).std()
    result["min"] = data.rolling(window=window, min_periods=window//2).min()
    result["max"] = data.rolling(window=window, min_periods=window//2).max()
    return result


def calculate_z_score(current_value, historical_series, window=60):
    """Calculate z-score relative to historical distribution"""
    if len(historical_series) < window:
        return np.nan
    
    recent = historical_series.tail(window)
    mean = recent.mean()
    std = recent.std()
    
    if std == 0 or np.isnan(std):
        return np.nan
    
    return (current_value - mean) / std


def calculate_z_scores(data, window=60):
    """Calculate rolling z-scores"""
    rolling_mean = data.rolling(window=window, min_periods=window//2).mean()
    rolling_std = data.rolling(window=window, min_periods=window//2).std()
    return (data - rolling_mean) / rolling_std


def convert_normal_vol_to_daily_bp_vol(normal_vol_annualized):
    """Convert annualized normal vol to daily bp vol"""
    return normal_vol_annualized / np.sqrt(TRADING_DAYS_PER_YEAR)


def convert_daily_bp_vol_to_annualized(daily_bp_vol):
    """Convert daily bp vol to annualized"""
    return daily_bp_vol * np.sqrt(TRADING_DAYS_PER_YEAR)
