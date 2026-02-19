# Rates Vol Relative-Value Analytics Dashboard

A Python-based analytics system for non-linear rates options trading, replicating the functionality of institutional research reports (Nomura, JPMorgan, BofA) to identify rich/cheap volatility opportunities and generate actionable trade recommendations.

## 🎯 Project Goal

Build a trader-focused dashboard that answers:
- **Where is volatility rich/cheap?**
- **What structures should I trade?**

This is a **trader-decision tool**, not a theoretical modeling exercise.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Module Specifications](#module-specifications)
4. [Data Requirements](#data-requirements)
5. [Implementation Timeline](#implementation-timeline)
6. [Technical Stack](#technical-stack)
7. [Deliverables](#deliverables)

---

## 🏗️ Project Overview

### Core Philosophy

This system replicates the daily workflow of a non-linear rates options desk:

1. **Build Surface** - Understand current vol structure (from SABR cube)
2. **Compute Signals** - Identify rich/cheap opportunities
3. **Suggest Trades** - Generate actionable trade recommendations

### Key Principles

- ✅ **Trader-focused**: Actionable insights, not academic models
- ✅ **Relative Value**: Rich/cheap identification across products
- ✅ **Daily Workflow**: Morning dashboard for quick decision-making
- ✅ **Incremental Build**: MVP first, then enhancements

---

## 🧱 System Architecture

```
Rates Vol RV Analytics Dashboard
│
├── Module 1: Vol Surface Monitor (Core)
├── Module 1B: Strike Skew Monitor (Core)
├── Module 2: Conditional Curve Trade Screener (Core)
├── Module 3: Forward Vol Term Structure (High Impact)
├── Module 4: Midcurve RV Monitor (Advanced)
└── Module 5: YCSO Monitor (Advanced)
```

---

## 📊 Module Specifications

### **MODULE 1: Vol Surface Monitor** (Nomura-style)

**Purpose**: Daily monitoring of swaption volatility surface with rich/cheap identification

**Key Features**:
- **Daily Swaption Grid Table**
  - ATM swaption vols across tenors (1m, 3m, 6m, 1y, 2y) and underlying tenors (2y, 5y, 10y, 30y)
  - Annualized and daily basis point volatility
  - Changes: 1-day, 1-week, 1-month
  - 20-day max/min levels
  
- **Z-Score Analysis**
  - 60-day rolling z-scores for each swaption point
  - Color-coded heatmap (red = rich, green = cheap)
  - Statistical significance flags
  
- **Implied vs Realized Vol Analysis**
  - Implied vol (current market)
  - Realized vol over multiple horizons: 10d, 20d, 60d, 90d, 120d, 180d
  - Implied/Realized ratio
  - Z-scores for ratios
  
- **Rate/Vol Correlation**
  - Correlation heatmap between rates and volatility
  - Time series of correlation
  - Correlation regime identification
  
- **Mover Identification**
  - Largest daily/weekly/monthly movers
  - Highlighted in table with conditional formatting

**Outputs**:
- Formatted table (Excel/HTML)
- Heatmap visualizations
- Time series charts
- Rich/cheap signals with z-scores

**References**: Nomura US Vol RV Analytics Report

---

### **MODULE 1B: Strike Skew Monitor** (Nomura-style)

**Purpose**: Monitor strike skew in payer and receiver swaptions

**Key Features**:
- **Skew Metrics**
  - Payer vs receiver skew measures
  - 25-delta skew
  - Vol smile curvature
  
- **Skew Z-Scores**
  - Historical skew distribution
  - Current skew vs historical average
  - Statistical significance
  
- **Historical Time Series**
  - Skew evolution over time
  - Regime identification
  - Skew richness/cheapness signals
  
- **Skew Heatmap**
  - Skew across swaption grid
  - Relative skew levels

**Outputs**:
- Skew time series charts
- Skew heatmaps
- Rich/cheap skew signals

**References**: Nomura US Vol RV Analytics Report (Strike Skew section)

---

### **MODULE 2: Conditional Curve Trade Screener** (JPMorgan-style)

**Purpose**: Identify and construct zero-cost conditional curve trades

**Key Features**:
- **Directionality Analysis**
  - Implied directionality (from vol structure)
  - Delivered directionality (historical)
  - Mispricing signal (delivered - implied)
  - Historical success rate tracking
  
- **Curve Pairs Analysis**
  - 2s/10s, 5s/30s, 3s/20s, etc.
  - Directionality for each pair
  - Regime analysis (on-hold vs active CB)
  
- **Premium Neutrality Calculator**
  - **Weighted Curve Strategy**: Adjust notional based on vol ratio
  - **Strike Shift Strategy**: Shift strike OTM to achieve zero cost
  - Performance comparison (small moves vs large moves)
  - Mathematical formulas for both methods
  
- **Trade Recommendations**
  - Zero-cost trade structures
  - P&L scenarios (small move, large move)
  - Directional trigger identification
  - Historical performance metrics

**Outputs**:
- Trade recommendation table
- Premium-neutral trade structures
- P&L scenario analysis
- Directionality charts

**References**: JPMorgan "A primer on Conditional Trades" (May 2016)

---

### **MODULE 3: Forward Vol Term Structure** (BofA + JPMorgan-style)

**Purpose**: Analyze forward volatility term structure and calendar spread opportunities

**Key Features**:
- **Forward Vol Calculation**
  - Forward vol from spot vols
  - 3m → 1y → 2y forward vol
  - Term structure visualization
  
- **Roll-Down Analysis**
  - Vol roll-down over time
  - Carry analysis
  - Roll-down opportunities
  
- **Calendar Spreads**
  - Calendar spread identification
  - Forward vol dislocation
  - Rich/cheap forward vol
  
- **Term Structure Visualization**
  - Vol term structure charts
  - Forward vol curves
  - Historical comparison

**Outputs**:
- Forward vol term structure charts
- Calendar spread opportunities
- Roll-down analysis

**References**: BofA US Vol Primer, JPMorgan papers

---

### **MODULE 4: Midcurve RV Monitor** (JPMorgan-style) [Advanced]

**Purpose**: Identify rich/cheap midcurve options using fair value replication

**Key Features**:
- **Fair Value Calculation**
  - Replicate midcurve using two vanilla swaptions
  - Correlation dependency analysis
  - Fair value vs market price
  
- **Rich/Cheap Analysis**
  - Market midcurve vol vs fair value
  - Z-scores for midcurve richness
  - Historical comparison
  
- **Forward Vol Analysis**
  - Forward vol dislocation
  - Calendar spread opportunities
  - Forward vol term structure

**Outputs**:
- Midcurve rich/cheap table
- Fair value comparison
- Forward vol analysis

**References**: JPMorgan "Midcurve options primer" (May 2015)

**Data Dependency**: Requires correlation data between rates

---

### **MODULE 5: YCSO Monitor** (JPMorgan-style) [Advanced]

**Purpose**: Monitor Yield Curve Spread Options for relative value

**Key Features**:
- **Spread Volatility Calculation**
  - Spread vol from component vols and correlation
  - Formula: σ²_spread = σ²_r1 + σ²_r2 - 2ρσ_r1σ_r2
  
- **Correlation Analysis**
  - Implied correlation (from YCSO prices)
  - Realized correlation (historical)
  - Correlation matrix across curve
  
- **Convexity Adjustments**
  - CMS convexity adjustment calculation
  - Comparison: CMS vs swaption strikes
  
- **Trade Identification**
  - Correlation trades
  - Curve gamma trades
  - Conditional flies

**Outputs**:
- Spread vol analysis
- Correlation matrix
- YCSO rich/cheap signals

**References**: JPMorgan "Yield Curve Spread Options primer" (Nov 2015)

**Data Dependency**: Requires correlation data and YCSO market prices

---

## 📦 Data Requirements

### **Critical Data (Must Have)**

#### 1. **Swaption Market Data**
- **Source**: Bloomberg, Refinitiv, or internal data feed
- **Frequency**: Daily (end-of-day)
- **Required Fields**:
  - Option expiry: 1m, 3m, 6m, 1y, 2y
  - Underlying tenor: 2y, 5y, 10y, 30y
  - Strike: ATM (at minimum)
  - Implied volatility (basis point vol, annualized)
  - Option type: Payer, Receiver
  - Option price (optional, for validation)

- **Historical Data**: Minimum 1 year (preferably 2-3 years for z-scores)

#### 2. **Realized Volatility Data**
- **Source**: Calculate from swap rate time series
- **Frequency**: Daily
- **Required**:
  - Swap rates: 2y, 5y, 10y, 30y
  - Rolling windows: 10d, 20d, 60d, 90d, 120d, 180d
  - Historical time series: Minimum 1 year

#### 3. **Swap Rate Data**
- **Source**: Bloomberg, Refinitiv, or market data provider
- **Frequency**: Daily (end-of-day)
- **Required Tenors**: 2y, 5y, 10y, 30y
- **Historical**: Minimum 2-3 years

#### 4. **SABR Cube Parameters** (If Available)
- **Source**: Internal risk system or data provider
- **Frequency**: Daily
- **Required Parameters**:
  - α (initial vol)
  - β (skew parameter)
  - ν (vol-of-vol)
  - ρ (correlation)
- **Coverage**: Across swaption grid
- **Note**: If not available, can use implied vols directly

### **Important Data (Should Have)**

#### 5. **Strike Skew Data**
- **Source**: Swaption market data at different strikes
- **Required**:
  - OTM strikes (e.g., 25-delta, 10-delta)
  - Payer and receiver vols at each strike
  - Historical data for z-scores

#### 6. **Correlation Data**
- **Source**: Calculate from swap rate time series or market data
- **Required**:
  - Correlation between swap rates (2y, 5y, 10y, 30y)
  - Rolling window: 6 months
  - Historical: Minimum 1 year
- **Note**: Critical for Modules 4 and 5

### **Optional Data (Nice to Have)**

#### 7. **Midcurve Market Data**
- **Source**: OTC market data or internal system
- **Required**:
  - Midcurve swaption vols
  - Expiry and forward start dates
  - Historical data

#### 8. **YCSO Market Data**
- **Source**: OTC market data
- **Required**:
  - YCSO prices/vols
  - Curve pairs (2s/10s, 5s/30s, etc.)
  - Historical data

#### 9. **Rate/Vol Correlation Data**
- **Source**: Calculate from time series
- **Required**:
  - Correlation between swap rates and volatility
  - Rolling windows
  - Historical data

### **Data Access Strategy**

1. **Primary**: Check if BofA has internal data feeds
2. **Secondary**: Bloomberg/Refinitiv APIs (if available)
3. **Fallback**: Public data sources or synthetic data for development
4. **Validation**: Cross-check with published research reports

---

## ⏱️ Implementation Timeline

### **Phase 1: Foundation (Weeks 1-2)**

**Week 1: Setup & Data Pipeline**
- [ ] Set up Python environment and project structure
- [ ] Establish data pipeline (data ingestion, storage)
- [ ] Build data validation and cleaning functions
- [ ] Create database schema for historical data
- [ ] Test data access and quality

**Week 2: Core Calculations**
- [ ] Implement z-score calculations
- [ ] Build realized vol calculation engine (multiple horizons)
- [ ] Create vol surface data structures
- [ ] Implement basic vol surface visualization
- [ ] Test calculations against known values

**Deliverable**: Working data pipeline with basic calculations

---

### **Phase 2: Core Modules (Weeks 3-4)**

**Week 3: Module 1 - Vol Surface Monitor**
- [ ] Build daily swaption grid table
- [ ] Implement z-score analysis and heatmaps
- [ ] Create implied vs realized vol analysis
- [ ] Build rate/vol correlation calculations
- [ ] Implement mover identification
- [ ] Create formatted output (Excel/HTML)

**Week 4: Module 1B - Strike Skew Monitor**
- [ ] Implement skew metrics calculation
- [ ] Build skew z-score analysis
- [ ] Create skew time series charts
- [ ] Build skew heatmaps
- [ ] Integrate with Module 1

**Deliverable**: Complete Vol Surface Monitor with Skew analysis

---

### **Phase 3: Trade Screener (Weeks 5-6)**

**Week 5: Module 2 - Conditional Trades (Part 1)**
- [ ] Implement directionality calculation (implied)
- [ ] Build historical directionality tracking (delivered)
- [ ] Create mispricing signal calculation
- [ ] Build curve pair analysis framework

**Week 6: Module 2 - Conditional Trades (Part 2)**
- [ ] Implement weighted-curve strategy calculator
- [ ] Implement strike-shift strategy calculator
- [ ] Build premium neutrality solver
- [ ] Create trade recommendation engine
- [ ] Build P&L scenario analysis
- [ ] Create formatted trade output

**Deliverable**: Complete Conditional Curve Trade Screener

---

### **Phase 4: Enhancements (Weeks 7-8)**

**Week 7: Module 3 - Forward Vol Term Structure**
- [ ] Implement forward vol calculations
- [ ] Build roll-down analysis
- [ ] Create calendar spread identification
- [ ] Build term structure visualizations
- [ ] Integrate with main dashboard

**Week 8: Dashboard Integration & Polish**
- [ ] Create unified dashboard interface
- [ ] Integrate all modules
- [ ] Build automated daily report generation
- [ ] Create visualization improvements
- [ ] Add user documentation
- [ ] Performance optimization

**Deliverable**: Complete MVP with 3 core modules

---

### **Phase 5: Advanced Modules (Weeks 9-10)** [If Time Permits]

**Week 9: Module 4 - Midcurve RV Monitor**
- [ ] Implement fair value replication
- [ ] Build correlation dependency analysis
- [ ] Create midcurve rich/cheap screener
- [ ] Integrate with dashboard

**Week 10: Module 5 - YCSO Monitor**
- [ ] Implement spread vol calculations
- [ ] Build correlation analysis
- [ ] Create convexity adjustment calculator
- [ ] Build YCSO trade screener
- [ ] Final integration and testing

**Deliverable**: Complete system with all modules

---

## 🛠️ Technical Stack

### **Core Languages & Libraries**

**Python 3.9+**
- Primary development language

**Data Processing**
- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computations
- `scipy`: Statistical functions (z-scores, correlations)

**Visualization**
- `matplotlib`: Basic plotting
- `seaborn`: Statistical visualizations and heatmaps
- `plotly`: Interactive charts (optional, for dashboard)

**Database**
- `sqlite3` or `PostgreSQL`: Historical data storage
- `sqlalchemy`: Database ORM (optional)

**Reporting**
- `openpyxl`: Excel file generation
- `jinja2`: HTML report templating
- `streamlit` or `dash`: Interactive dashboard (optional)

**Data Access**
- `blpapi` (Bloomberg) or `eikon` (Refinitiv): Market data APIs
- `requests`: HTTP requests for data feeds

### **Project Structure**

```
rates_vol_rv_analytics/
│
├── README.md
├── requirements.txt
├── setup.py
│
├── data/
│   ├── raw/              # Raw market data
│   ├── processed/        # Cleaned data
│   └── historical/       # Historical database
│
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── data_loader.py
│   │   ├── data_validator.py
│   │   └── database.py
│   │
│   ├── calculations/
│   │   ├── volatility.py
│   │   ├── z_scores.py
│   │   ├── correlation.py
│   │   ├── directionality.py
│   │   └── fair_value.py
│   │
│   ├── modules/
│   │   ├── module1_vol_surface.py
│   │   ├── module1b_skew.py
│   │   ├── module2_conditional_trades.py
│   │   ├── module3_forward_vol.py
│   │   ├── module4_midcurve.py
│   │   └── module5_ycso.py
│   │
│   ├── visualization/
│   │   ├── heatmaps.py
│   │   ├── time_series.py
│   │   └── charts.py
│   │
│   ├── reporting/
│   │   ├── excel_report.py
│   │   ├── html_report.py
│   │   └── dashboard.py
│   │
│   └── utils/
│       ├── config.py
│       └── helpers.py
│
├── tests/
│   ├── test_calculations.py
│   ├── test_modules.py
│   └── test_data.py
│
├── notebooks/
│   ├── exploration.ipynb
│   └── validation.ipynb
│
└── docs/
    ├── user_guide.md
    └── technical_docs.md
```

---

## 📤 Deliverables

### **Core Deliverables**

1. **Working Python System**
   - Modular, well-documented code
   - Unit tests for key functions
   - Error handling and validation

2. **Daily Analytics Dashboard**
   - Automated daily report generation
   - Rich/cheap signals
   - Trade recommendations

3. **Documentation**
   - User guide (how to use the system)
   - Technical documentation (architecture, calculations)
   - Data requirements document

4. **Presentation**
   - Demo of system capabilities
   - Key findings and insights
   - Recommendations for desk usage

### **Output Formats**

- **Excel Reports**: Formatted tables (like Nomura report)
- **HTML Dashboard**: Interactive web interface
- **PDF Reports**: Daily summary reports
- **CSV Exports**: Raw data for further analysis

---

## 🎓 Key References

1. **Nomura**: "US Vol RV Analytics Report Primer" (March 2011)
2. **BofA**: "US Vol Primer: A Guide for the Perplexed" (March 2024)
3. **JPMorgan**: "Midcurve options primer" (May 2015)
4. **JPMorgan**: "A primer on Conditional Trades" (May 2016)
5. **JPMorgan**: "Yield Curve Spread Options primer" (November 2015)
6. **Hagan et al.**: "Managing Smile Risk" (SABR model)

---

## 🚀 Getting Started

### **Prerequisites**

- Python 3.9+
- Access to market data (Bloomberg, Refinitiv, or internal feeds)
- Understanding of rates options markets

### **Installation**

```bash
# Clone repository
git clone <repository-url>
cd rates_vol_rv_analytics

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **Configuration**

1. Set up data access credentials
2. Configure database connection
3. Set parameters (z-score windows, vol horizons, etc.)

### **Running the System**

```bash
# Generate daily report
python src/reporting/dashboard.py --date 2024-01-15

# Run specific module
python src/modules/module1_vol_surface.py

# Run all modules
python src/reporting/dashboard.py --all
```

---

## 📝 Notes

- **Data Access**: Confirm data availability early in the project
- **Incremental Build**: Start with MVP (Modules 1, 1B, 2), then expand
- **Validation**: Cross-check results with published research reports
- **Performance**: Optimize for daily batch processing
- **Maintainability**: Write clean, documented code for desk use

---

## 🤝 Contributing

This is an intern project for BofA non-linear rates options desk.

---

## 📄 License

Internal use only.

---

**Last Updated**: January 2024
**Author**: [Your Name]
**Contact**: [Your Email]
