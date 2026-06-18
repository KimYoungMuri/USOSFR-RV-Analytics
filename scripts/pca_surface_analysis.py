"""
PCA/HPCA vol surface analysis

Decomposes the ATM swaption vol surface, ranks largest movers,
computes front vs long gamma curve vol spreads, and extracts
skew/smile from strike offsets.

Usage:
    python scripts/pca_surface_analysis.py 2024-12-31
    python scripts/pca_surface_analysis.py              # latest date
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from src.data_loader import VolCube420Loader
from src.surface_analysis import (
  build_atm_panel,
  run_pca,
  run_hpca,
  rank_largest_movers,
  curve_vol_spreads,
  compute_skew_smile,
  pc_zscores,
)
from src.config import OPTION_TENORS, SWAP_TENORS


def load_vol_history():
  loader = VolCube420Loader()
  vol_data = loader.load_all_atm_timeseries()
  vol_data = vol_data.rename(columns={
    "option_tenor": "expiry",
    "swap_tenor": "tenor",
    "normal_vol": "implied_bpvol_annualized",
  })
  return vol_data


def plot_pca_loadings(loadings, out_file):
  fig, axes = plt.subplots(1, 3, figsize=(14, 5))
  
  for i, ax in enumerate(axes):
    pc = f"PC{i+1}"
    if pc not in loadings.columns:
      continue
    colors = ["steelblue" if c.endswith("Y") and int(c.split("x")[1][:-1]) <= 10 else "coral"
              for c in loadings.index]
    ax.bar(range(len(loadings)), loadings[pc], color=colors, alpha=0.8)
    ax.set_xticks(range(len(loadings)))
    ax.set_xticklabels(loadings.index, rotation=90, fontsize=7)
    ax.set_title(f"{pc} loadings")
    ax.axhline(0, color="black", linewidth=0.5)
    ax.grid(True, alpha=0.3)
  
  fig.tight_layout()
  fig.savefig(out_file, dpi=150, bbox_inches="tight")
  plt.close()


def plot_pc_scores(scores, out_file):
  fig, ax = plt.subplots(figsize=(10, 5))
  for col in scores.columns[:3]:
    ax.plot(scores.index, scores[col], label=col, linewidth=1)
  ax.set_title("PCA factor scores")
  ax.set_xlabel("Date")
  ax.legend()
  ax.grid(True, alpha=0.3)
  fig.savefig(out_file, dpi=150, bbox_inches="tight")
  plt.close()


def main(as_of_date):
  print("Loading ATM vol history (2017-2024)...")
  vol_data = load_vol_history()
  
  out_dir = Path(__file__).parent.parent / "outputs" / "tables"
  out_dir.mkdir(parents=True, exist_ok=True)
  plot_dir = Path(__file__).parent.parent / "outputs" / "plots"
  plot_dir.mkdir(parents=True, exist_ok=True)
  
  # --- PCA ---
  print("\nRunning PCA on ATM vol surface...")
  panel = build_atm_panel(vol_data)
  pca = run_pca(panel, n_components=3)
  
  loadings = pca["loadings"]
  scores = pca["scores"]
  explained = pca["explained_variance_ratio"]
  
  loadings_file = out_dir / f"pca_loadings_{as_of_date}.csv"
  loadings.to_csv(loadings_file)
  
  scores_file = out_dir / f"pca_scores_{as_of_date}.csv"
  scores.to_csv(scores_file)
  
  print(f"\nPCA explained variance: PC1={explained[0]:.1%}, PC2={explained[1]:.1%}, PC3={explained[2]:.1%}")
  print(f"Loadings saved to {loadings_file}")
  
  plot_pca_loadings(loadings, plot_dir / f"pca_loadings_{as_of_date}.png")
  plot_pc_scores(scores, plot_dir / f"pca_scores_{as_of_date}.png")
  
  # PC z-scores as of date
  zscores = pc_zscores(scores)
  if as_of_date in zscores.index:
    latest_z = zscores.loc[as_of_date]
    print(f"\nPCA z-scores as of {as_of_date}:")
    for col in latest_z.index:
      print(f"  {col}: {latest_z[col]:.2f}")
  
  # --- HPCA ---
  print("\nRunning hierarchical PCA...")
  hpca = run_hpca(panel)
  
  hpca_scores = hpca["cross_scores"]
  hpca_loadings = hpca["cross_loadings"]
  
  hpca_scores.to_csv(out_dir / f"hpca_scores_{as_of_date}.csv")
  hpca_loadings.to_csv(out_dir / f"hpca_loadings_{as_of_date}.csv")
  
  h_explained = hpca["explained_variance_ratio"]
  print(f"HPCA explained variance: {', '.join(f'HPC{i+1}={v:.1%}' for i, v in enumerate(h_explained))}")
  
  # --- Largest movers ---
  print(f"\nLargest movers as of {as_of_date}...")
  movers = rank_largest_movers(vol_data, as_of_date)
  movers_file = out_dir / f"largest_movers_{as_of_date}.csv"
  movers.to_csv(movers_file, index=False)
  
  for period in ["1d", "1w", "1m"]:
    col = f"abs_change_{period}"
    rank_col = f"rank_{period}"
    if col not in movers.columns:
      continue
    top = movers.nsmallest(3, rank_col)[["label", f"change_{period}", col, rank_col]]
    print(f"\n  Top {period} movers:")
    print(top.to_string(index=False, float_format=lambda x: f"{x:.2f}"))
  
  # --- Curve vol spreads ---
  print(f"\nFront vs long gamma curve vol spreads ({as_of_date})...")
  spreads = curve_vol_spreads(vol_data, as_of_date)
  spreads_file = out_dir / f"curve_vol_spreads_{as_of_date}.csv"
  spreads.to_csv(spreads_file, index=False)
  print(spreads.to_string(index=False, float_format=lambda x: f"{x:.2f}"))
  
  # --- Skew / smile from strike offsets ---
  print(f"\nSkew and smile from strike offsets ({as_of_date})...")
  loader = VolCube420Loader()
  try:
    strike_surface = loader.load_strike_surface(as_of_date)
    skew_smile = compute_skew_smile(strike_surface)
    skew_file = out_dir / f"skew_smile_{as_of_date}.csv"
    skew_smile.to_csv(skew_file, index=False)
    print(skew_smile.to_string(index=False, float_format=lambda x: f"{x:.2f}"))
    print(f"\nSaved to {skew_file}")
    
    # Skew heatmap
    pivot = skew_smile.pivot(index="option_tenor", columns="swap_tenor", values="skew_25bp")
    expiry_order = {e: i for i, e in enumerate(OPTION_TENORS)}
    pivot = pivot.reindex(sorted(pivot.index, key=lambda x: expiry_order.get(x, 99)))
    
    fig, ax = plt.subplots(figsize=(7, 5))
    im = ax.imshow(pivot.values, aspect="auto", cmap="RdYlGn_r")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([f"{t}Y" for t in pivot.columns])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_title(f"25bp Skew (receiver - payer) — {as_of_date}")
    plt.colorbar(im, ax=ax, label="bp vol")
    fig.savefig(plot_dir / f"skew_25bp_heatmap_{as_of_date}.png", dpi=150, bbox_inches="tight")
    plt.close()
    
  except FileNotFoundError as e:
    print(f"  Skew/smile skipped: {e}")
    print("  (Daily strike cube will be downloaded on first run)")
  
  print(f"\n{'='*70}")
  print("Analysis complete.")
  print(f"Outputs in {out_dir} and {plot_dir}")


if __name__ == "__main__":
  if len(sys.argv) > 1:
    as_of_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
  else:
    vol_data = load_vol_history()
    as_of_date = vol_data["date"].max()
    print(f"No date provided, using latest: {as_of_date}")
  
  main(as_of_date)
