# Rates Volatility Relative-Value Analytics

Python-based analytics system for identifying rich/cheap volatility opportunities in US rates swaptions using implied and realized volatility analysis.

## Overview

The system processes daily swaption volatility data and SOFR swap rates to compute:
- Implied vs realized volatility comparisons
- Z-score based rich/cheap identification
- Volatility surface structure analysis
- Conditional curve trade opportunities

## Data Sources

### VolCube420
- **Source**: [GitHub - yieldcurvemonkey/VolCube420](https://github.com/yieldcurvemonkey/VolCube420)
- **Content**: SOFR OIS swaption volatility cube
- **Format**: Daily JSON files (NY EOD marks)
- **Coverage**: 
  - Option tenors: 1M, 3M, 6M, 1Y, 2Y
  - Swap tenors: 1Y, 2Y, 3Y, 4Y, 5Y, 6Y, 7Y, 8Y, 9Y, 10Y, 15Y, 20Y, 25Y, 30Y
  - Strike offsets: -200, -100, -50, -25, -10, 0, 10, 25, 50, 100, 200 bps
- **Vol Type**: Normal volatility (annualized)
- **Historical**: Daily data from 2017 onwards

### SOFR Swap Rates
- **Tenors**: 1Y, 2Y, 3Y, 4Y, 5Y, 6Y, 7Y, 8Y, 9Y, 10Y, 15Y, 20Y, 25Y, 30Y
- **Frequency**: Daily
- **Use Cases**: 
  - Realized volatility calculation
  - Rate/vol correlation analysis
  - Directionality analysis

### MOVE Index
- **Content**: ICE BofA MOVE Index (Treasury volatility index)
- **Frequency**: Daily
- **Use Case**: Macro regime context, MOVE vs swaption vol comparison

## Module Specifications

### MODULE 1: Vol Surface Monitor

**Status**: Implemented

**Features**:

1. **Daily Swaption Grid Table**
   - ATM swaption vols from VolCube420
   - Option tenors: 1M, 3M, 6M, 1Y, 2Y
   - Swap tenors: 2Y, 5Y, 10Y, 30Y
   - Annualized normal vol and daily basis point vol (annualized / √252)

2. **Change Analysis**
   - 1-day change: Today vs yesterday
   - 1-week change: Today vs 5 business days ago
   - 1-month change: Today vs 20 business days ago
   - Largest movers identification

3. **Z-Score Analysis**
   - 60-day rolling z-scores: `z = (current - mean) / std`
   - Rich/cheap flags: z > 1.3 (rich), z < -1.3 (cheap)
   - 20-day rolling high/low levels

4. **Implied vs Realized Vol**
   - Implied vol: Current market vol from VolCube420
   - Realized vol: Calculated from SOFR swap rate history using basis point changes
   - Horizons: 10d, 20d, 60d, 90d, 120d, 180d
   - Ratio: Implied / Realized

5. **Mover Table**
   - Largest daily/weekly/monthly movers
   - Ranked by absolute change

**Outputs**:
- Formatted Excel table with conditional formatting
- HTML table for web interface
- CSV export

**Implementation**: `src/modules/swaption_vol_table.py`

---

### MODULE 2: Conditional Curve Trade Screener

**Status**: Planned

**Features**:

1. **Curve Pairs**
   - Primary: 2s/10s
   - Secondary: 5s/30s

2. **Directionality Analysis**
   - Implied directionality: Extract from vol structure (long-end vol vs short-end vol)
   - Delivered directionality: Historical correlation between rate moves and curve changes
   - Mispricing signal: Delivered - Implied
   - Success rate: Historical performance tracking

3. **Conditional Trade Construction**
   - Bear steepener: Buy payer on long end vs sell payer on short end
   - Bull flattener: Buy receiver on long end vs sell receiver on short end
   - Premium neutrality: Zero-cost structure calculation

4. **Regime Analysis**
   - On-hold CB regime: Back-end driven (bear-steepen/bull-flatten)
   - Active CB regime: Front-end driven (bear-flatten/bull-steepen)

**Outputs**:
- Trade recommendation table
- Directionality charts
- Premium-neutral trade structures

**References**: 
- JPMorgan: "A primer on Conditional Trades" (May 2016)

---

### MODULE 3: Implied vs Realized Module

**Status**: Planned

**Features**:

1. **Implied Move Distribution**
   - Extract from current vol surface
   - Expected move distribution
   - Percentile analysis (1-day, 1-week, 1-month)

2. **Realized Distribution**
   - Historical realized moves
   - Rolling windows: 10d, 20d, 60d, 90d
   - Percentile analysis: 50th, 75th, 90th, 95th, 99th
   - Distribution shape analysis

3. **Comparison Analysis**
   - Implied vs realized distribution overlay
   - Percentile comparison
   - Tail analysis for extreme moves
   - Z-scores for current implied vs historical realized

4. **Gamma Decision Support**
   - Rich vol: Implied > Realized → Sell gamma signal
   - Cheap vol: Implied < Realized → Buy gamma signal

**Outputs**:
- Distribution comparison charts
- Percentile tables
- Rich/cheap signals

---

### MODULE 4: Vol Surface Structure

**Status**: Planned

**Features**:

1. **Term Structure Analysis**
   - Vol term structure: Vol vs expiry (1M → 2Y)
   - Slope: Short-dated vs long-dated vol
   - Curvature: Term structure shape
   - Roll-down: Vol decay over time

2. **Curve Vol Spreads**
   - Front vs long gamma: 1M/3M vs 1Y/2Y vol
   - Vol spread analysis across expiries
   - Relative value identification

3. **Surface Shape Analysis**
   - Skew: From strike offsets in VolCube420
   - Smile: Vol curvature across strikes
   - Surface visualization: 3D surface plots

4. **Historical Comparison**
   - Term structure evolution
   - Surface shape changes
   - Regime identification

**Outputs**:
- Term structure charts
- Vol spread tables
- Surface visualizations

---

### MODULE 5: MOVE vs Swaption Vol

**Status**: Planned

**Features**:

1. **MOVE Index Tracking**
   - Daily MOVE index levels
   - Historical comparison
   - Z-scores

2. **Swaption Vol Comparison**
   - Key points: 1Y10Y, 2Y10Y
   - Ratio: MOVE / Swaption Vol
   - Historical relationship: Correlation and spread

3. **Regime Analysis**
   - High MOVE / Low Swaption: Macro stress, rates vol cheap
   - Low MOVE / High Swaption: Idiosyncratic rates vol rich

**Outputs**:
- MOVE vs Swaption vol chart
- Ratio analysis
- Regime signals

---

### MODULE 6: Midcurve RV Monitor (Simplified)

**Status**: Planned

**Features**:

1. **Forward Starting Implied Vols** (Approximate)
   - 1Y10Y vs 3M10Y: Compare forward-starting to spot-starting
   - 1M5Y vs 6M5Y: Similar comparisons
   - Approximation using term structure interpolation

2. **Term Structure Comparisons**
   - Calendar spreads: Compare expiries
   - Forward vol: Extract from term structure
   - Dislocations: Identify rich/cheap forward vol

3. **Gamma vs Vega Comparisons**
   - Short expiry: More gamma, less vega
   - Long expiry: Less gamma, more vega

4. **Implied vs Realized by Expiry**
   - 1M realized: Short-term realized vol
   - 1Y realized: Longer-term realized vol

5. **Vol Curve Dislocations**
   - 1Y10Y vs 3M10Y: Forward-starting rich/cheap
   - 1M5Y vs 6M5Y: Similar analysis

**Note**: Simplified version without full correlation-dependent pricing.

**Outputs**:
- Forward vol comparison table
- Term structure dislocation signals

---

## Technical Stack

### Core Libraries

```python
# Data Processing
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0

# Visualization
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.14.0

# Data Access
requests>=2.31.0
openpyxl>=3.1.0

# UI
streamlit>=1.28.0
```

## Project Structure

```
US Vol RV Analytics/
├── src/
│   ├── data/
│   │   └── data_loader.py        # VolCube420 and SOFR loaders
│   ├── calculations/
│   │   └── volatility.py         # Volatility calculations
│   ├── modules/
│   │   ├── swaption_vol_table.py  # Core swaption vol table
│   │   └── get_swaption_table.py  # Convenience functions
│   ├── reporting/
│   │   ├── excel_formatter.py    # Excel export
│   │   └── html_table_formatter.py # HTML formatter
│   └── utils/
│       └── config.py              # Configuration
├── data/
│   ├── raw/volcube420/            # Cached VolCube420 data
│   └── historical/               # SOFR Excel files
├── app.py                         # Streamlit UI
├── export_table.py                # Excel export script
└── view_table.py                  # Table viewer
```

## Key Calculations

### Realized Volatility

```python
# Basis point volatility from daily rate changes
rate_changes = rates.diff()
realized_vol_bp = rate_changes.rolling(window).std() * np.sqrt(252)
```

### Z-Scores

```python
# 60-day rolling z-score
mean_60d = data.rolling(60).mean()
std_60d = data.rolling(60).std()
z_score = (current - mean_60d) / std_60d

# Rich/cheap flags
rich = z_score > 1.3
cheap = z_score < -1.3
```

### Directionality

```python
# Implied: Compare long-end vol vs short-end vol
implied_directionality = long_end_vol / short_end_vol

# Delivered: Historical correlation
delivered_directionality = calculate_historical_correlation(
    rate_changes, curve_changes
)
```

## Usage

### View Table

```bash
python view_table.py --date 2024-12-31
```

### Export to Excel

```bash
python export_table.py --date 2024-12-31
```

### Run UI

```bash
streamlit run app.py
```

Or use the shell script:

```bash
./run_ui.sh
```

## References

1. **VolCube420**: [GitHub Repository](https://github.com/yieldcurvemonkey/VolCube420) - SOFR OIS swaption volatility cube data
2. **Nomura**: "US Vol RV Analytics Report Primer" (March 2011) - Vol surface monitoring and strike skew analysis
3. **BofA**: "US Rates US Vol Primer: A Guide for the Perplexed" (March 2024) - Rates volatility basics, swaption grid dynamics, and macro views
4. **JPMorgan**: "Midcurve options primer: Mechanics, fair value analysis, typical trades, and JPM analytics" (May 2015) - Midcurve options pricing and fair value estimation
5. **JPMorgan**: "A primer on Conditional Trades: Setting the curve or spread exposure as a function of market direction" (May 2016) - Conditional trades and premium neutrality
6. **JPMorgan**: "Yield Curve Spread Options primer: Mechanics, fair value analysis, typical trades, and JPM analytics" (November 2015) - YCSO pricing and correlation dependency
7. **Hagan et al.**: "Managing Smile Risk" (SABR model) - Stochastic volatility model for volatility smile/skew
8. **Hagan & Konikov**: "Volatility Cube Construction" - Volatility cube interpolation and arbitrage-free surface construction

---

**Last Updated**: January 2025
