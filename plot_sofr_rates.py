"""
Plot all SOFR swap rates from 2017 to current
"""
import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from src.data.data_loader import SOFRLoader

print("Loading SOFR swap rates...")
loader = SOFRLoader()

# Load all tenors
all_data = []
tenors = [1, 2, 3, 5, 7, 10, 15, 20, 30]

for tenor in tenors:
    try:
        df = loader.load_sofr_rates(tenor)
        all_data.append(df)
        print(f"  ✓ Loaded {tenor}yr: {len(df)} rows")
    except Exception as e:
        print(f"  ✗ Failed to load {tenor}yr: {e}")

if not all_data:
    print("No data loaded!")
    sys.exit(1)

# Combine all data
combined = pd.concat(all_data, ignore_index=True)

# Filter to 2017 onwards
combined = combined[combined['date'] >= pd.Timestamp('2017-01-01').date()]

print(f"\nTotal data points: {len(combined)}")
print(f"Date range: {combined['date'].min()} to {combined['date'].max()}")

# Create the plot
fig, ax = plt.subplots(figsize=(14, 8))

# Color palette for different tenors
colors = plt.cm.tab20(range(len(tenors)))

# Plot each tenor
for i, tenor in enumerate(tenors):
    tenor_data = combined[combined['tenor'] == tenor].sort_values('date')
    if len(tenor_data) > 0:
        ax.plot(
            tenor_data['date'],
            tenor_data['rate'],
            label=f'{tenor}Y',
            linewidth=1.5,
            color=colors[i],
            alpha=0.8
        )

# Formatting
ax.set_xlabel('Date', fontsize=12, fontweight='bold')
ax.set_ylabel('SOFR Swap Rate (%)', fontsize=12, fontweight='bold')
ax.set_title('SOFR Swap Rates: 2017 - Current', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--')
ax.legend(loc='best', ncol=3, fontsize=10, framealpha=0.9)

# Format x-axis dates
fig.autofmt_xdate()

# Add some styling
plt.tight_layout()

# Save the plot
output_file = 'sofr_rates_plot.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\n✓ Plot saved to: {output_file}")

# Close the figure to free memory
plt.close()

print("\nDone!")
