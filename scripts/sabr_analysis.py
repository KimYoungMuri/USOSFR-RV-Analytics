"""
SABR calibration on VolCube420 strike surfaces

Usage:
    python scripts/sabr_analysis.py 2024-12-31
    python scripts/sabr_analysis.py              # latest date
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from src.data_loader import VolCube420Loader, SOFRLoader
from src.sabr import calibrate_sabr, calibrate_sabr_surface, option_tenor_to_years, hagan_normal_vol
from src.config import OPTION_TENORS, SWAP_TENORS, SABR_BETA


def get_forward_rates(sofr_loader, as_of_date):
  """Use SOFR par rates as forward proxy for each swap tenor"""
  forwards = {}
  for tenor in SWAP_TENORS:
    try:
      rates = sofr_loader.load_sofr_rates(tenor)
      snap = rates[rates["date"] <= as_of_date]
      if len(snap):
        forwards[tenor] = snap.iloc[-1]["rate"]
    except Exception:
      pass
  return forwards


def main(as_of_date):
  vol_loader = VolCube420Loader()
  sofr_loader = SOFRLoader()
  
  print(f"Loading strike cube for {as_of_date}...")
  strike_surface = vol_loader.load_strike_surface(as_of_date)
  
  fwd_by_tenor = get_forward_rates(sofr_loader, as_of_date)
  forward_map = {
    (opt, tenor): fwd_by_tenor.get(tenor)
    for opt in OPTION_TENORS
    for tenor in SWAP_TENORS
  }
  
  print(f"Calibrating SABR (beta={SABR_BETA}) across grid...")
  sabr_params = calibrate_sabr_surface(strike_surface, forward_map, beta=SABR_BETA)
  
  out_dir = Path(__file__).parent.parent / "outputs" / "tables"
  out_dir.mkdir(parents=True, exist_ok=True)
  plot_dir = Path(__file__).parent.parent / "outputs" / "plots"
  plot_dir.mkdir(parents=True, exist_ok=True)
  
  params_file = out_dir / f"sabr_params_{as_of_date}.csv"
  sabr_params.to_csv(params_file, index=False)
  print(f"\nSABR parameters saved to {params_file}")
  
  print(f"\n{'='*70}")
  print(f"SABR Calibration Summary — {as_of_date}")
  print(f"{'='*70}")
  print(sabr_params.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
  
  # Fit details for a few key points
  fit_rows = []
  key_swaptions = [("1Y", 10), ("3M", 5), ("6M", 10), ("2Y", 30)]
  
  for opt, tenor in key_swaptions:
    sub = strike_surface[
      (strike_surface["option_tenor"] == opt) &
      (strike_surface["swap_tenor"] == tenor)
    ]
    params = sabr_params[
      (sabr_params["option_tenor"] == opt) &
      (sabr_params["swap_tenor"] == tenor)
    ]
    if sub.empty or params.empty:
      continue
    
    fwd = params.iloc[0]["forward"]
    expiry = option_tenor_to_years(opt)
    alpha = params.iloc[0]["alpha"]
    rho = params.iloc[0]["rho"]
    nu = params.iloc[0]["nu"]
    
    for _, row in sub.iterrows():
      k = fwd + row["strike_offset_bp"] / 100.0
      model = hagan_normal_vol(fwd, k, expiry, alpha, SABR_BETA, rho, nu)
      fit_rows.append({
        "option_tenor": opt,
        "swap_tenor": tenor,
        "strike_offset_bp": row["strike_offset_bp"],
        "market_vol": row["normal_vol"],
        "sabr_vol": model,
        "residual": model - row["normal_vol"],
      })
  
  fit_df = pd.DataFrame(fit_rows)
  fit_file = out_dir / f"sabr_fit_{as_of_date}.csv"
  fit_df.to_csv(fit_file, index=False)
  print(f"\nFit details saved to {fit_file}")
  
  # Smile plot for 1Yx10Y
  sub = strike_surface[
    (strike_surface["option_tenor"] == "1Y") &
    (strike_surface["swap_tenor"] == 10)
  ]
  params = sabr_params[
    (sabr_params["option_tenor"] == "1Y") &
    (sabr_params["swap_tenor"] == 10)
  ]
  
  if not sub.empty and not params.empty:
    fwd = params.iloc[0]["forward"]
    expiry = option_tenor_to_years("1Y")
    alpha = params.iloc[0]["alpha"]
    rho = params.iloc[0]["rho"]
    nu = params.iloc[0]["nu"]
    
    offsets = sub["strike_offset_bp"].values
    market = sub["normal_vol"].values
    strikes = fwd + offsets / 100.0
    model = np.array([
      hagan_normal_vol(fwd, k, expiry, alpha, SABR_BETA, rho, nu)
      for k in strikes
    ])
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(offsets, market, "o-", label="Market", color="steelblue")
    ax.plot(offsets, model, "s--", label="SABR fit", color="coral")
    ax.set_xlabel("Strike offset (bp from ATMF)")
    ax.set_ylabel("Normal vol (annualized bp)")
    ax.set_title(f"SABR Smile — 1Yx10Y — {as_of_date}")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plot_file = plot_dir / f"sabr_smile_1Y10Y_{as_of_date}.png"
    fig.savefig(plot_file, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Smile plot saved to {plot_file}")
  
  print(f"\nAvg RMSE: {sabr_params['rmse'].mean():.3f} bp")
  print(f"Median rho: {sabr_params['rho'].median():.3f}")
  print(f"Median nu:  {sabr_params['nu'].median():.3f}")


if __name__ == "__main__":
  if len(sys.argv) > 1:
    as_of_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
  else:
    loader = VolCube420Loader()
    vol_data = loader.load_all_atm_timeseries()
    as_of_date = vol_data["date"].max()
    print(f"No date provided, using latest: {as_of_date}")
  
  main(as_of_date)
