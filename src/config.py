"""
Configuration
"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
HISTORICAL_DATA_DIR = DATA_DIR / "historical"

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

# Swaption grid
OPTION_TENORS = ["1M", "3M", "6M", "1Y", "2Y"]
SWAP_TENORS = [2, 5, 10, 30]

# Calculation parameters
Z_SCORE_WINDOW = 60
REALIZED_VOL_WINDOWS = [10, 20, 60, 90, 120, 180]
TRADING_DAYS_PER_YEAR = 252

# Z-score thresholds
Z_SCORE_RICH = 1.3
Z_SCORE_CHEAP = -1.3

# VolCube420 strike offsets (bp from ATMF)
STRIKE_OFFSETS_BP = [-200, -100, -50, -25, -10, 0, 10, 25, 50, 100, 200]

# VolCube420 daily cube (for skew/smile and SABR)
VOLCUBE420_DAILY_URL = "https://raw.githubusercontent.com/yieldcurvemonkey/VolCube420/main/{date}.json"

# SABR defaults (rates convention)
SABR_BETA = 0.5
