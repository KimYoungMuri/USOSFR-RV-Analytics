"""
Volatility calculations: realized volatility, changes, z-scores
"""
import pandas as pd
import numpy as np
from typing import List, Optional
from datetime import date, timedelta

from src.config import TRADING_DAYS_PER_YEAR, REALIZED_VOL_WINDOWS


def calculate_realized_vol(
    rates: pd.Series,
    window: int,
    annualize: bool = True,
    rates_in_percent: bool = True
) -> pd.Series:
    """
    Calculate realized volatility from swap rates in basis points
    
    For rates volatility, we calculate the standard deviation of daily rate changes
    in basis points, then annualize.
    
    Args:
        rates: Series of swap rates (indexed by date)
        window: Rolling window in days
        annualize: If True, annualize to basis point vol
        rates_in_percent: If True, rates are in percentage (e.g., 4.5 for 4.5%)
                         If False, rates are in decimal (e.g., 0.045 for 4.5%)
        
    Returns:
        Series of realized volatility in basis points (daily if annualize=False)
    """
    # Filter out zero or negative rates
    rates_clean = rates[rates > 0].copy()
    
    if len(rates_clean) < 2:
        return pd.Series(index=rates.index, dtype=float)
    
    # Calculate daily changes in basis points
    # If rates are in percentage (e.g., 4.5 for 4.5%), convert to bp: (4.5 - 4.4) * 100 = 10 bp
    # If rates are in decimal (e.g., 0.045 for 4.5%), convert to bp: (0.045 - 0.044) * 10000 = 10 bp
    if rates_in_percent:
        # Rates are in percentage, so 1% = 100 bp
        daily_changes_bp = (rates_clean - rates_clean.shift(1)) * 100
    else:
        # Rates are in decimal, so 0.01 = 100 bp
        daily_changes_bp = (rates_clean - rates_clean.shift(1)) * 10000
    
    # Remove infinite or NaN values
    daily_changes_bp = daily_changes_bp.replace([np.inf, -np.inf], np.nan)
    
    # Rolling standard deviation of daily changes (in basis points)
    rolling_std_bp = daily_changes_bp.rolling(window=window, min_periods=min(5, window//2)).std()
    
    if annualize:
        # Annualize: multiply by sqrt(252) for daily data
        # This gives us annualized realized vol in basis points
        realized_vol = rolling_std_bp * np.sqrt(TRADING_DAYS_PER_YEAR)
    else:
        # Daily vol in basis points (no annualization)
        realized_vol = rolling_std_bp
    
    # Reindex to original index
    realized_vol = realized_vol.reindex(rates.index)
    
    return realized_vol


def calculate_realized_vol_multiple_windows(
    rates: pd.Series,
    windows: List[int] = None,
    rates_in_percent: bool = True,
    annualize: bool = True
) -> pd.DataFrame:
    """
    Calculate realized volatility for multiple windows
    
    Args:
        rates: Series of swap rates
        windows: List of window sizes in days
        rates_in_percent: If True, rates are in percentage format
        annualize: If True, annualize the volatility
        
    Returns:
        DataFrame with columns for each window
    """
    if windows is None:
        windows = REALIZED_VOL_WINDOWS
    
    result = pd.DataFrame(index=rates.index)
    
    for window in windows:
        result[f"realized_vol_{window}d"] = calculate_realized_vol(
            rates, window, rates_in_percent=rates_in_percent, annualize=annualize
        )
    
    return result


def calculate_changes(
    data: pd.Series,
    periods: List[int] = [1, 5, 20]
) -> pd.DataFrame:
    """
    Calculate changes over different periods
    
    Args:
        data: Series of values (indexed by date)
        periods: List of periods in days [1d, 1w (5d), 1m (20d)]
        
    Returns:
        DataFrame with change columns
    """
    result = pd.DataFrame(index=data.index)
    
    for period in periods:
        result[f"change_{period}d"] = data - data.shift(period)
    
    return result


def calculate_rolling_stats(
    data: pd.Series,
    window: int = 20
) -> pd.DataFrame:
    """
    Calculate rolling statistics (mean, std, min, max)
    
    Args:
        data: Series of values
        window: Rolling window in days
        
    Returns:
        DataFrame with rolling stats
    """
    result = pd.DataFrame(index=data.index)
    result["mean"] = data.rolling(window=window, min_periods=window//2).mean()
    result["std"] = data.rolling(window=window, min_periods=window//2).std()
    result["min"] = data.rolling(window=window, min_periods=window//2).min()
    result["max"] = data.rolling(window=window, min_periods=window//2).max()
    
    return result


def calculate_z_score(
    current_value: float,
    historical_series: pd.Series,
    window: int = 60
) -> float:
    """
    Calculate z-score for a value relative to historical distribution
    
    Args:
        current_value: Current value
        historical_series: Historical series of values
        window: Window for rolling statistics
        
    Returns:
        Z-score
    """
    if len(historical_series) < window:
        return np.nan
    
    # Get recent window
    recent = historical_series.tail(window)
    mean = recent.mean()
    std = recent.std()
    
    if std == 0 or np.isnan(std):
        return np.nan
    
    z_score = (current_value - mean) / std
    return z_score


def calculate_z_scores(
    data: pd.Series,
    window: int = 60
) -> pd.Series:
    """
    Calculate rolling z-scores for a series
    
    Args:
        data: Series of values
        window: Window for rolling statistics
        
    Returns:
        Series of z-scores
    """
    rolling_mean = data.rolling(window=window, min_periods=window//2).mean()
    rolling_std = data.rolling(window=window, min_periods=window//2).std()
    
    z_scores = (data - rolling_mean) / rolling_std
    return z_scores


def convert_normal_vol_to_daily_bp_vol(normal_vol_annualized: float) -> float:
    """
    Convert annualized normal vol to daily basis point vol
    
    Args:
        normal_vol_annualized: Annualized normal vol
        
    Returns:
        Daily basis point vol
    """
    return normal_vol_annualized / np.sqrt(TRADING_DAYS_PER_YEAR)


def convert_daily_bp_vol_to_annualized(daily_bp_vol: float) -> float:
    """
    Convert daily basis point vol to annualized
    
    Args:
        daily_bp_vol: Daily basis point vol
        
    Returns:
        Annualized normal vol
    """
    return daily_bp_vol * np.sqrt(TRADING_DAYS_PER_YEAR)
