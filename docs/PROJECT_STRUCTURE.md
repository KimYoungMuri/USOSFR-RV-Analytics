# Project Structure

```
US Vol RV Analytics/
│
├── README.md                    # Original comprehensive README
├── README_FOCUSED.md            # Focused project scope README
├── USAGE.md                     # Usage guide
├── UI_GUIDE.md                  # UI usage guide
├── LICENSE                       # MIT License
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
├── .gitattributes                # Git attributes
│
├── app.py                        # Streamlit UI application
├── export_table.py               # Excel export script
├── view_table.py                 # Table viewing script
├── plot_sofr_rates.py            # SOFR rates plotting script
├── run_ui.sh                     # UI launcher script
│
├── data/
│   ├── raw/                      # Raw data (VolCube420 cache)
│   ├── processed/                # Processed data
│   └── historical/               # SOFR swap rate Excel files
│       ├── SOFR 1yr.xlsx
│       ├── SOFR 2yr.xlsx
│       ├── SOFR 3yr.xlsx
│       ├── SOFR 5yr.xlsx
│       ├── SOFR 7yr.xlsx
│       ├── SOFR 10yr.xlsx
│       ├── SOFR 15yr.xlsx
│       ├── SOFR 20yr.xlsx
│       └── SOFR 30yr.xlsx
│
├── src/
│   ├── __init__.py
│   │
│   ├── data/
│   │   └── data_loader.py        # VolCube420 and SOFR loaders
│   │
│   ├── calculations/
│   │   └── volatility.py         # Volatility calculations (z-scores, realized vol, changes)
│   │
│   ├── modules/
│   │   ├── swaption_vol_table.py  # Core swaption vol table builder
│   │   └── get_swaption_table.py  # Convenience function with caching
│   │
│   ├── reporting/
│   │   ├── excel_formatter.py    # Excel export with Nomura-style formatting
│   │   └── html_table_formatter.py # HTML table formatter for UI
│   │
│   └── utils/
│       └── config.py              # Configuration and paths
│
├── tests/                        # Test files (to be added)
├── notebooks/                    # Jupyter notebooks (to be added)
└── venv/                         # Virtual environment (gitignored)
```

## Key Files

### Core Modules
- **`src/modules/swaption_vol_table.py`**: Main table builder with all calculations
- **`src/modules/get_swaption_table.py`**: User-facing function with data caching
- **`src/data/data_loader.py`**: Data loaders for VolCube420 and SOFR rates
- **`src/calculations/volatility.py`**: Statistical calculations (z-scores, realized vol, changes)

### UI & Reporting
- **`app.py`**: Streamlit web interface
- **`src/reporting/excel_formatter.py`**: Excel export with formatting
- **`src/reporting/html_table_formatter.py`**: HTML table formatter

### Scripts
- **`export_table.py`**: Export table to Excel
- **`view_table.py`**: View table in terminal
- **`plot_sofr_rates.py`**: Plot SOFR swap rates
