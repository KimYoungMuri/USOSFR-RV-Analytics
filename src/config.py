"""
Configuration file for data paths and parameters
"""
import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
HISTORICAL_DATA_DIR = DATA_DIR / "historical"

# VolCube420 data (loaded from local cache in data/raw/volcube420/)

# SOFR swap rate files
SOFR_FILES = {
    1: HISTORICAL_DATA_DIR / "SOFR 1yr.xlsx",
    2: HISTORICAL_DATA_DIR / "SOFR 2yr.xlsx",
    3: HISTORICAL_DATA_DIR / "SOFR 3yr.xlsx",
    5: HISTORICAL_DATA_DIR / "SOFR 5yr.xlsx",
    7: HISTORICAL_DATA_DIR / "SOFR 7yr.xlsx",
    10: HISTORICAL_DATA_DIR / "SOFR 10yr.xlsx",
    15: HISTORICAL_DATA_DIR / "SOFR 15yr.xlsx",
    20: HISTORICAL_DATA_DIR / "SOFR 20yr.xlsx",
    30: HISTORICAL_DATA_DIR / "SOFR 30yr.xlsx",
}

# Swaption grid configuration
OPTION_TENORS = ["1M", "3M", "6M", "1Y", "2Y"]
SWAP_TENORS = [2, 5, 10, 30]  # Years

# Calculation parameters
Z_SCORE_WINDOW = 60  # Days for z-score calculation
REALIZED_VOL_WINDOWS = [10, 20, 60, 90, 120, 180]  # Days
TRADING_DAYS_PER_YEAR = 252

# Z-score thresholds for color coding
Z_SCORE_RICH = 1.3  # Red: z-score > 1.3
Z_SCORE_CHEAP = -1.3  # Green: z-score < -1.3
