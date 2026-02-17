# Swaption Vol Table - Usage Guide

## Quick Start

### Option 1: Command Line

```bash
# Get table for specific date
python view_table.py 2024-12-31

# Or use the module directly
python src/modules/get_swaption_table.py 2024-12-31

# Use latest available date (no argument)
python view_table.py
```

### Option 2: Python Function

```python
from src.modules.get_swaption_table import get_swaption_table, get_swaption_table_latest
from datetime import date

# Get table for specific date
table = get_swaption_table(date(2024, 12, 31))

# Or get latest available date
table = get_swaption_table_latest()

# View it
print(table)

# Filter to specific swaption
print(table[table['term_tenor'] == '1M × 2Y'])

# Export
table.to_csv('my_table.csv', index=False)
table.to_excel('my_table.xlsx', index=False)
```

## What Date Range is Available?

- **Vol Data**: 2017-01-03 to 2024-12-31
- **SOFR Data**: 2017-01-03 to 2026-02-11

You can use any date between 2017-01-03 and 2024-12-31 (limited by vol data).

## Table Structure

The table contains 72 rows (all expiry × tenor combinations) with:

### Section 1: Implied Vol (Annualized BP Vol)
- Current
- 1d change
- 1w change  
- 1m change
- 20d high
- 20d low

### Section 2: Implied Vol (Daily BP Vol)
- Current (converted: annualized / sqrt(252))
- 1d change
- 1w change
- 1m change
- 20d high
- 20d low

### Section 3: Realized Vol (BP Vol)
- 10d, 20d, 60d, 90d, 120d, 180d windows

### Highlighting Flags
- `is_largest_1d_mover`: Largest 1d move in last 10 days
- `is_largest_1w_mover`: Largest 1w move in last 20 days
- `is_largest_1m_mover`: Largest 1m move in last 120 days

## Examples

```python
# Get table for specific date
from src.modules.get_swaption_table import get_swaption_table
from datetime import date

table = get_swaption_table(date(2024, 6, 15))
print(f"Table for 2024-06-15: {len(table)} rows")

# Filter to specific swaptions
short_term = table[table['expiry'].isin(['1M', '3M', '6M'])]
print(f"Short-term swaptions: {len(short_term)} rows")

# Find largest movers
movers = table[table['is_largest_1d_mover'] | table['is_largest_1w_mover']]
print(f"Largest movers: {len(movers)} rows")
```

## Data Caching

The function caches data after the first call, so subsequent calls with different dates are fast!
