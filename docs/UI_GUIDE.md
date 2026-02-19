# Swaption Vol Table UI Guide

## 🚀 Quick Start

### Run the UI:

```bash
streamlit run app.py
```

Or use the helper script:

```bash
./run_ui.sh
```

The UI will open in your browser automatically (usually at `http://localhost:8501`)

## 📊 Features

### 1. **Date Selection**
- **Sidebar**: Select any date from 2017-01-03 to 2024-12-31
- **Quick buttons**: "Latest" and "1 Week Ago" for quick navigation
- **Date range**: Shows available date range

### 2. **Formatted Table Display**
- **Three sections**:
  - Implied Basis Point Volatility (Annualized)
  - Implied Basis Point Volatility (Daily)
  - Realized Basis Point Volatility (Daily)
- **Color coding**:
  - **Dark gray cells** = Largest movers (highlighted)
  - Negative values shown in **parentheses**
- **20 swaption combinations**: 1M, 3M, 6M, 1Y, 2Y × 2Y, 5Y, 10Y, 30Y

### 3. **Export Options**
- **Download CSV**: Direct download button
- **Export to Excel**: Creates formatted Excel file with Nomura-style formatting

### 4. **Largest Movers Summary**
- Shows which swaptions had the largest moves
- Identifies 1d, 1w, or 1m movers

## 🎨 Visual Features

- **Clean, professional layout**
- **Color-coded cells** for largest movers
- **Responsive design** (works on different screen sizes)
- **Hover effects** on table rows
- **Alternating row colors** for readability

## 📝 Notes

The table matches the Nomura report format:
- Negative values in parentheses
- Dark gray highlighting for largest movers
- All three volatility sections displayed
- Professional formatting

## 🔧 Troubleshooting

If the UI doesn't start:
1. Make sure Streamlit is installed: `pip install streamlit`
2. Check that data files are in the correct locations
3. Verify date is within available range (2017-2024)
