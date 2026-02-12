# Rates Vol Relative-Value Analytics Dashboard

A Python-based analytics system for non-linear rates options trading, focused on identifying rich/cheap volatility opportunities and generating actionable trade recommendations using available market data.

## 🎯 Project Goal

Build a trader-focused dashboard that answers:
- **Where is volatility rich/cheap?**
- **What structures should I trade?**
- **How does implied vol compare to realized?**

This is a **trader-decision tool** built with **available data sources**.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Available Data Sources](#available-data-sources)
3. [Module Specifications](#module-specifications)
4. [Implementation Priority](#implementation-priority)
5. [Technical Stack](#technical-stack)
6. [Project Structure](#project-structure)

---

## 🏗️ Project Overview

### Core Philosophy

This system replicates the daily workflow of a non-linear rates options desk using **real, accessible data**:

1. **Monitor Surface** - Track vol levels and changes
2. **Compute Signals** - Identify rich/cheap opportunities
3. **Suggest Trades** - Generate actionable recommendations

### Key Principles

- ✅ **Trader-focused**: Actionable insights, not academic models
- ✅ **Data-driven**: Built with available market data
- ✅ **Incremental**: Start with core, add enhancements
- ✅ **Practical**: Daily workflow tool

---

## 📊 Available Data Sources

### 1. **VolCube420 - Swaption Volatility Data**
- **Source**: [GitHub - yieldcurvemonkey/VolCube420](https://github.com/yieldcurvemonkey/VolCube420)
- **Content**: SOFR OIS Swaption Volatility Cube Data
- **Format**: Daily JSON files (NY EOD marks)
- **Coverage**: 
  - Option Tenors: 1M, 3M, 6M, 1Y, 2Y, etc.
  - Swap Tenors: 1Y, 2Y, 3Y, 4Y, 5Y, 6Y, 7Y, 8Y, 9Y, 10Y, 15Y, 20Y, 25Y, 30Y
  - Strike Offsets: -200, -100, -50, -25, -10, 0, 10, 25, 50, 100, 200 bps
- **Vol Type**: Normal Vol (annualized)
- **Historical**: Daily data from 2024 onwards
- **Note**: Includes SABR-calibrated data with bilinear interpolation

### 2. **SOFR Swap Rate History**
- **Source**: Market data provider (Bloomberg, Refinitiv, or internal)
- **Content**: SOFR swap rates
- **Tenors**: 1Y, 2Y, 3Y, 4Y, 5Y, 6Y, 7Y, 8Y, 9Y, 10Y, 15Y, 20Y, 25Y, 30Y
- **Frequency**: Daily
- **Use Cases**: 
  - Realized volatility calculation
  - Rate/vol correlation
  - Directionality analysis

### 3. **MOVE Index**
- **Source**: Market data provider
- **Content**: ICE BofA MOVE Index (Treasury volatility index)
- **Frequency**: Daily
- **Use Case**: Macro regime context, MOVE vs swaption vol comparison

---

## 🧱 Module Specifications

### **MODULE 1: Vol Surface Monitor** (Nomura-style) ⭐ **CORE**

**Priority**: **HIGHEST** - This is the foundation of the entire system

**Purpose**: Daily monitoring of swaption volatility surface with rich/cheap identification

**Key Features**:

1. **Daily Swaption Grid Table**
   - ATM swaption vols from VolCube420
   - Option tenors: 1M, 3M, 6M, 1Y, 2Y
   - Swap tenors: 2Y, 5Y, 10Y, 30Y (key points)
   - Annualized normal vol
   - Daily basis point vol (divide by √252)

2. **Change Analysis**
   - **1-day change**: Today vs yesterday
   - **1-week change**: Today vs 5 business days ago
   - **1-month change**: Today vs 20 business days ago
   - Highlight largest movers

3. **Z-Score Analysis**
   - 60-day rolling z-scores for each swaption point
   - Formula: `z = (current - mean) / std`
   - Color-coded heatmap (red = rich, green = cheap)
   - Statistical significance flags (|z| > 2)

4. **Implied vs Realized Vol**
   - **Implied vol**: Current market vol from VolCube420
   - **Realized vol**: Calculate from SOFR swap rate history
   - **Horizons**: 10d, 20d, 60d, 90d, 120d, 180d
   - **Ratio**: Implied / Realized
   - **Z-scores**: For implied/realized ratios

5. **Mover Table**
   - Largest daily/weekly/monthly movers
   - Highlighted with conditional formatting
   - Ranked by absolute change

**Outputs**:
- Formatted Excel table (Nomura-style)
- Heatmap visualizations
- Time series charts
- Rich/cheap signals

**Data Requirements**:
- ✅ VolCube420 (ATM vols)
- ✅ SOFR swap rate history (for realized vol)

**References**: Nomura US Vol RV Analytics Report

---

### **MODULE 2: Conditional Curve Trade Screener** (JPMorgan-style) ⭐ **CORE**

**Priority**: **HIGHEST** - Very desk-relevant, traders love this

**Purpose**: Identify and construct zero-cost conditional curve trades

**Key Features**:

1. **Curve Pairs Focus**
   - **2s/10s**: Primary focus
   - **5s/30s**: Secondary focus
   - Additional pairs as data allows

2. **Directionality Analysis**
   - **Implied directionality**: Extract from vol structure
     - Compare long-end vol vs short-end vol
     - Higher long-end vol → bear-steepening implied
   - **Delivered directionality**: Historical analysis
     - Calculate: When rates move, does curve steepen or flatten?
     - Track: Bear-steepen vs bull-flatten patterns
   - **Mispricing signal**: Delivered - Implied
   - **Success rate**: Historical performance tracking

3. **Conditional Trade Construction**
   - **Bear Steepener**: Buy payer on long end (10Y/30Y) vs sell payer on short end (2Y/5Y)
   - **Bull Flattener**: Buy receiver on long end vs sell receiver on short end
   - **Premium neutrality**: Calculate zero-cost structures
   - **Trade recommendations**: With P&L scenarios

4. **Regime Analysis**
   - **On-hold CB regime**: Back-end driven (bear-steepen/bull-flatten)
   - **Active CB regime**: Front-end driven (bear-flatten/bull-steepen)
   - **Current regime identification**

**Outputs**:
- Trade recommendation table
- Directionality charts
- Premium-neutral trade structures
- P&L scenario analysis

**Data Requirements**:
- ✅ VolCube420 (for vol structure)
- ✅ SOFR swap rate history (for directionality)

**References**: JPMorgan "A primer on Conditional Trades" (May 2016)

---

### **MODULE 3: Implied vs Realized Module** ⭐ **CRITICAL**

**Priority**: **HIGH** - Critical for gamma decisions, used daily on desks

**Purpose**: Compare implied volatility to realized volatility distributions

**Key Features**:

1. **Implied Move Distribution**
   - Extract from current vol surface
   - Calculate expected move distribution
   - Percentile analysis (1-day, 1-week, 1-month)

2. **Realized Distribution**
   - Historical realized moves
   - Rolling windows: 10d, 20d, 60d, 90d
   - Percentile analysis
   - Distribution shape (normal, fat tails, etc.)

3. **Comparison Analysis**
   - **Implied vs Realized**: Overlay distributions
   - **Percentile comparison**: 50th, 75th, 90th, 95th, 99th
   - **Tail analysis**: Extreme moves
   - **Z-scores**: For current implied vs historical realized

4. **Gamma Decision Support**
   - **Rich vol**: Implied > Realized → Sell gamma
   - **Cheap vol**: Implied < Realized → Buy gamma
   - **Signal strength**: Statistical significance

**Outputs**:
- Distribution comparison charts
- Percentile tables
- Rich/cheap signals
- Gamma trade recommendations

**Data Requirements**:
- ✅ VolCube420 (implied vols)
- ✅ SOFR swap rate history (realized moves)

---

### **MODULE 4: Vol Surface Structure** ⭐ **IMPORTANT**

**Priority**: **MEDIUM** - Important but fast to add

**Purpose**: Analyze vol surface structure and term structure dynamics

**Key Features**:

1. **Term Structure Analysis**
   - **Vol term structure**: Vol vs expiry (1M → 2Y)
   - **Slope**: Short-dated vs long-dated vol
   - **Curvature**: Term structure shape
   - **Roll-down**: Vol decay over time

2. **Curve Vol Spreads**
   - **Front vs Long Gamma**: 1M/3M vs 1Y/2Y vol
   - **Vol spread analysis**: Compare across expiries
   - **Relative value**: Rich/cheap across term structure

3. **Surface Shape Analysis**
   - **Skew**: From strike offsets in VolCube420
   - **Smile**: Vol curvature across strikes
   - **Surface visualization**: 3D surface plots

4. **Historical Comparison**
   - Term structure evolution
   - Surface shape changes
   - Regime identification

**Outputs**:
- Term structure charts
- Vol spread tables
- Surface visualizations
- Rich/cheap signals

**Data Requirements**:
- ✅ VolCube420 (full strike structure)

---

### **MODULE 5: MOVE vs Swaption Vol** ⭐ **EASY ADD**

**Priority**: **LOW** - Easy add, macro context

**Purpose**: Compare MOVE index (Treasury vol) to swaption vol for macro regime context

**Key Features**:

1. **MOVE Index Tracking**
   - Daily MOVE index levels
   - Historical comparison
   - Z-scores

2. **Swaption Vol Comparison**
   - **Key points**: 1Y10Y, 2Y10Y (most liquid)
   - **Ratio**: MOVE / Swaption Vol
   - **Historical relationship**: Correlation and spread

3. **Regime Analysis**
   - **High MOVE / Low Swaption**: Macro stress, rates vol cheap
   - **Low MOVE / High Swaption**: Idiosyncratic rates vol rich
   - **Regime identification**: Current state

4. **Macro Context**
   - **Treasury vol vs Rates vol**: Different drivers
   - **Cross-asset signals**: What MOVE tells us about rates vol

**Outputs**:
- MOVE vs Swaption vol chart
- Ratio analysis
- Regime signals

**Data Requirements**:
- ✅ MOVE Index (daily)
- ✅ VolCube420 (swaption vols)

---

### **MODULE 6: Midcurve RV Monitor** (Simplified) ⭐ **PARTIAL**

**Priority**: **MEDIUM** - Simplified version, no full pricing engine

**Purpose**: Identify relative value in forward-starting structures

**Key Features**:

1. **Forward Starting Implied Vols** (Approximate)
   - **1Y10Y vs 3M10Y**: Compare forward-starting to spot-starting
   - **1M5Y vs 6M5Y**: Similar comparisons
   - **Approximation**: Use term structure interpolation
   - **No full pricing**: Skip correlation-dependent fair value

2. **Term Structure Comparisons**
   - **Calendar spreads**: Compare expiries
   - **Forward vol**: Extract from term structure
   - **Dislocations**: Identify rich/cheap forward vol

3. **Gamma vs Vega Comparisons**
   - **Short expiry**: More gamma, less vega
   - **Long expiry**: Less gamma, more vega
   - **Relative value**: Compare across expiries

4. **Implied vs Realized by Expiry**
   - **1M realized**: Short-term realized vol
   - **1Y realized**: Longer-term realized vol
   - **Comparison**: Implied vs realized by expiry

5. **Vol Curve Dislocations**
   - **1Y10Y vs 3M10Y**: Forward-starting rich/cheap
   - **1M5Y vs 6M5Y**: Similar analysis
   - **Simplified RV**: Without full correlation pricing

**Outputs**:
- Forward vol comparison table
- Term structure dislocation signals
- Simplified RV signals

**Data Requirements**:
- ✅ VolCube420 (multiple expiries)
- ✅ SOFR swap rate history (for realized by expiry)

**Note**: This is a **simplified** version. Full midcurve pricing requires correlation data which we don't have. This module focuses on term structure and forward vol analysis.

---

## 🎯 Implementation Priority

### **Phase 1: Core Foundation (Weeks 1-3)**

**Week 1: Data Pipeline & Module 1 (Part 1)**
- [ ] Set up data pipeline (VolCube420, SOFR rates, MOVE)
- [ ] Build data loader and validator
- [ ] Implement basic vol surface table
- [ ] Calculate daily/weekly/monthly changes

**Week 2: Module 1 (Part 2)**
- [ ] Implement z-score calculations
- [ ] Build implied vs realized vol analysis
- [ ] Create heatmaps and visualizations
- [ ] Build mover identification

**Week 3: Module 3 - Implied vs Realized**
- [ ] Implement implied move distribution
- [ ] Build realized distribution analysis
- [ ] Create comparison charts
- [ ] Generate gamma signals

**Deliverable**: Working Vol Surface Monitor + Implied vs Realized

---

### **Phase 2: Trade Screener (Weeks 4-5)**

**Week 4: Module 2 (Part 1)**
- [ ] Implement directionality calculation (implied)
- [ ] Build historical directionality tracking
- [ ] Create mispricing signal
- [ ] Analyze 2s/10s and 5s/30s

**Week 5: Module 2 (Part 2)**
- [ ] Build conditional trade construction
- [ ] Implement premium neutrality calculator
- [ ] Create trade recommendations
- [ ] Build P&L scenarios

**Deliverable**: Complete Conditional Curve Trade Screener

---

### **Phase 3: Enhancements (Weeks 6-7)**

**Week 6: Module 4 - Vol Surface Structure**
- [ ] Implement term structure analysis
- [ ] Build vol spread calculations
- [ ] Create surface visualizations
- [ ] Add historical comparison

**Week 7: Module 5 & 6**
- [ ] Implement MOVE vs Swaption vol
- [ ] Build simplified Midcurve RV monitor
- [ ] Create forward vol analysis
- [ ] Dashboard integration

**Deliverable**: Complete system with all modules

---

## 🛠️ Technical Stack

### **Core Libraries**

```python
# Data Processing
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0

# Visualization
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.14.0  # Optional, for interactive charts

# Data Access
requests>=2.31.0  # For GitHub API (VolCube420)
gitpython>=3.1.0  # For cloning VolCube420 repo

# Reporting
openpyxl>=3.1.0  # Excel output
jinja2>=3.1.0    # HTML templates

# Database (optional)
sqlite3  # Built-in, for historical data storage
```

### **Data Access Strategy**

1. **VolCube420**: Clone GitHub repo or download JSON files
2. **SOFR Rates**: API access or CSV files
3. **MOVE Index**: API access or CSV files

---

## 📁 Project Structure

```
rates_vol_rv_analytics/
│
├── README_FOCUSED.md          # This file
├── requirements.txt
│
├── data/
│   ├── raw/
│   │   ├── volcube420/        # Cloned or downloaded VolCube420 data
│   │   ├── sofr_rates/        # SOFR swap rate history
│   │   └── move_index/       # MOVE index data
│   ├── processed/            # Cleaned and processed data
│   └── historical/           # Historical database (SQLite)
│
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── data_loader.py    # Load VolCube420, SOFR, MOVE
│   │   ├── data_validator.py
│   │   └── database.py       # Historical data storage
│   │
│   ├── calculations/
│   │   ├── volatility.py     # Realized vol calculations
│   │   ├── z_scores.py       # Z-score calculations
│   │   ├── directionality.py # Directionality analysis
│   │   └── distributions.py  # Implied vs realized distributions
│   │
│   ├── modules/
│   │   ├── module1_vol_surface.py      # Vol Surface Monitor
│   │   ├── module2_conditional_trades.py # Conditional Trade Screener
│   │   ├── module3_implied_realized.py  # Implied vs Realized
│   │   ├── module4_vol_structure.py     # Vol Surface Structure
│   │   ├── module5_move_comparison.py  # MOVE vs Swaption
│   │   └── module6_midcurve_rv.py      # Simplified Midcurve RV
│   │
│   ├── visualization/
│   │   ├── heatmaps.py
│   │   ├── time_series.py
│   │   └── distributions.py
│   │
│   ├── reporting/
│   │   ├── excel_report.py   # Nomura-style Excel output
│   │   ├── html_report.py    # HTML dashboard
│   │   └── dashboard.py      # Main dashboard
│   │
│   └── utils/
│       ├── config.py
│       └── helpers.py
│
├── tests/
│   ├── test_calculations.py
│   └── test_modules.py
│
└── notebooks/
    ├── data_exploration.ipynb
    └── validation.ipynb
```

---

## 📊 Key Calculations

### **1. Realized Volatility**
```python
# Annualized realized vol from daily returns
realized_vol = returns.std() * np.sqrt(252)

# Rolling windows
for window in [10, 20, 60, 90, 120, 180]:
    rolling_vol = returns.rolling(window).std() * np.sqrt(252)
```

### **2. Z-Scores**
```python
# 60-day rolling z-score
mean_60d = data.rolling(60).mean()
std_60d = data.rolling(60).std()
z_score = (current - mean_60d) / std_60d
```

### **3. Directionality**
```python
# Implied: Compare long-end vol vs short-end vol
implied_directionality = long_end_vol / short_end_vol

# Delivered: Historical correlation
# When rates move, does curve steepen or flatten?
delivered_directionality = calculate_historical_correlation(
    rate_changes, curve_changes
)
```

### **4. Implied vs Realized Distribution**
```python
# Implied: From vol surface
implied_dist = extract_from_vol_surface(current_vol)

# Realized: Historical moves
realized_dist = calculate_historical_moves(swap_rates, window=60)
```

---

## 🎓 Key References

1. **Nomura**: "US Vol RV Analytics Report Primer" (March 2011)
2. **JPMorgan**: "A primer on Conditional Trades" (May 2016)
3. **BofA**: "US Vol Primer: A Guide for the Perplexed" (March 2024)
4. **VolCube420**: [GitHub Repository](https://github.com/yieldcurvemonkey/VolCube420)

---

## 🚀 Getting Started

### **Step 1: Clone VolCube420 Data**

```bash
# Option 1: Clone the repo
git clone https://github.com/yieldcurvemonkey/VolCube420.git data/raw/volcube420

# Option 2: Download specific date files via GitHub API
```

### **Step 2: Set Up Environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### **Step 3: Configure Data Sources**

1. Set up SOFR swap rate data source
2. Set up MOVE index data source
3. Configure data paths in `src/utils/config.py`

### **Step 4: Run Daily Report**

```bash
python src/reporting/dashboard.py --date 2024-01-15
```

---

## 📝 Notes

- **Data Availability**: Confirm SOFR rates and MOVE index access early
- **Incremental Build**: Start with Module 1, then add others
- **Validation**: Cross-check calculations with known values
- **Performance**: Optimize for daily batch processing
- **Maintainability**: Write clean, documented code

---

## ✅ Success Criteria

A successful project will:
1. ✅ Generate daily vol surface monitor (Module 1)
2. ✅ Identify conditional curve trade opportunities (Module 2)
3. ✅ Compare implied vs realized distributions (Module 3)
4. ✅ Analyze vol surface structure (Module 4)
5. ✅ Provide MOVE context (Module 5)
6. ✅ Identify simplified midcurve RV (Module 6)
7. ✅ Produce trader-friendly outputs (Excel, HTML)

---

**Last Updated**: January 2024
**Status**: Focused MVP Scope
**Data Sources**: VolCube420, SOFR Rates, MOVE Index
