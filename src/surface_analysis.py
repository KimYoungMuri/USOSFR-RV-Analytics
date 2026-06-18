"""
Vol surface analysis: PCA/HPCA, movers, curve spreads, skew/smile
"""
import numpy as np
import pandas as pd

from src.config import OPTION_TENORS, SWAP_TENORS, Z_SCORE_WINDOW


def swaption_label(option_tenor, swap_tenor):
  return f"{option_tenor}x{swap_tenor}Y"


def build_atm_panel(vol_data):
  """Pivot ATM vol data to dates x swaption grid"""
  df = vol_data.copy()
  
  if "implied_bpvol_annualized" in df.columns:
    vol_col = "implied_bpvol_annualized"
    opt_col = "expiry"
  else:
    vol_col = "normal_vol"
    opt_col = "option_tenor"
  
  tenor_col = "tenor" if "tenor" in df.columns else "swap_tenor"
  df = df[df[opt_col].isin(OPTION_TENORS) & df[tenor_col].isin(SWAP_TENORS)]
  
  df["label"] = df.apply(
    lambda r: swaption_label(r[opt_col], r[tenor_col]), axis=1
  )
  
  panel = df.pivot_table(
    index="date", columns="label", values=vol_col, aggfunc="last"
  )
  
  col_order = [swaption_label(o, t) for o in OPTION_TENORS for t in SWAP_TENORS]
  col_order = [c for c in col_order if c in panel.columns]
  panel = panel[col_order].dropna(how="all")
  
  return panel


def run_pca(panel, n_components=3):
  """Standard PCA on ATM vol surface panel"""
  clean = panel.dropna()
  if len(clean) < n_components + 5:
    raise ValueError("Not enough data for PCA")
  
  X = clean.values
  means = X.mean(axis=0)
  stds = X.std(axis=0)
  stds[stds == 0] = 1.0
  X_std = (X - means) / stds
  
  U, s, Vt = np.linalg.svd(X_std, full_matrices=False)
  components = Vt[:n_components]
  scores = X_std @ components.T
  
  explained = (s ** 2) / (s ** 2).sum()
  
  loadings = pd.DataFrame(
    components.T,
    index=clean.columns,
    columns=[f"PC{i+1}" for i in range(n_components)],
  )
  
  scores_df = pd.DataFrame(
    scores,
    index=clean.index,
    columns=[f"PC{i+1}" for i in range(n_components)],
  )
  
  return {
    "scores": scores_df,
    "loadings": loadings,
    "explained_variance_ratio": explained[:n_components],
    "mean": means,
    "std": stds,
  }


def run_hpca(panel):
  """
  Hierarchical PCA: PCA within each option expiry bucket,
  then PCA on the first PC scores across expiries.
  """
  clean = panel.dropna()
  within_scores = {}
  within_loadings = {}
  
  for opt in OPTION_TENORS:
    cols = [c for c in clean.columns if c.startswith(f"{opt}x")]
    if len(cols) < 2:
      continue
    
    sub = clean[cols].dropna()
    if len(sub) < 5:
      continue
    
    X = sub.values
    std = X.std(axis=0)
    std[std == 0] = 1.0
    X_std = (X - X.mean(axis=0)) / std
    _, s, Vt = np.linalg.svd(X_std, full_matrices=False)
    
    pc1 = Vt[0]
    score = X_std @ pc1
    within_scores[opt] = pd.Series(score, index=sub.index, name=opt)
    within_loadings[opt] = pd.Series(pc1, index=cols, name=opt)
  
  if not within_scores:
    raise ValueError("Not enough data for HPCA")
  
  score_panel = pd.DataFrame(within_scores).dropna()
  
  X = score_panel.values
  std = X.std(axis=0)
  std[std == 0] = 1.0
  X_std = (X - X.mean(axis=0)) / std
  _, s, Vt = np.linalg.svd(X_std, full_matrices=False)
  
  n_comp = min(3, len(OPTION_TENORS))
  cross_loadings = pd.DataFrame(
    Vt[:n_comp].T,
    index=score_panel.columns,
    columns=[f"HPC{i+1}" for i in range(n_comp)],
  )
  cross_scores = pd.DataFrame(
    X_std @ Vt[:n_comp].T,
    index=score_panel.index,
    columns=[f"HPC{i+1}" for i in range(n_comp)],
  )
  
  explained = (s ** 2) / (s ** 2).sum()
  
  return {
    "within_scores": score_panel,
    "within_loadings": within_loadings,
    "cross_scores": cross_scores,
    "cross_loadings": cross_loadings,
    "explained_variance_ratio": explained[:n_comp],
  }


def rank_largest_movers(vol_data, as_of_date, periods=None):
  """Rank swaptions by absolute vol change"""
  if periods is None:
    periods = {"1d": 1, "1w": 5, "1m": 20}
  
  if "implied_bpvol_annualized" in vol_data.columns:
    vol_col = "implied_bpvol_annualized"
    opt_col = "expiry"
    tenor_col = "tenor"
  else:
    vol_col = "normal_vol"
    opt_col = "option_tenor"
    tenor_col = "swap_tenor"
  
  hist = vol_data[vol_data["date"] <= as_of_date].copy()
  hist = hist.sort_values("date")
  
  rows = []
  for (opt, tenor), group in hist.groupby([opt_col, tenor_col]):
    if opt not in OPTION_TENORS or tenor not in SWAP_TENORS:
      continue
    
    series = group.set_index("date")[vol_col]
    if len(series) < 2:
      continue
    
    row = {
      "option_tenor": opt,
      "swap_tenor": tenor,
      "label": swaption_label(opt, tenor),
      "current_vol": series.iloc[-1],
    }
    
    for name, lag in periods.items():
      if len(series) > lag:
        row[f"change_{name}"] = series.iloc[-1] - series.iloc[-1 - lag]
        row[f"abs_change_{name}"] = abs(row[f"change_{name}"])
      else:
        row[f"change_{name}"] = np.nan
        row[f"abs_change_{name}"] = np.nan
    
    rows.append(row)
  
  movers = pd.DataFrame(rows)
  
  for name in periods:
    col = f"abs_change_{name}"
    if col in movers.columns:
      movers[f"rank_{name}"] = movers[col].rank(ascending=False, method="min")
  
  return movers.sort_values(["option_tenor", "swap_tenor"])


def curve_vol_spreads(vol_data, as_of_date):
  """
  Front vs long gamma curve vol spreads.
  Front = 1M/3M, Long = 1Y/2Y. Spread = front - long per swap tenor.
  """
  if "implied_bpvol_annualized" in vol_data.columns:
    vol_col = "implied_bpvol_annualized"
    opt_col = "expiry"
    tenor_col = "tenor"
  else:
    vol_col = "normal_vol"
    opt_col = "option_tenor"
    tenor_col = "swap_tenor"
  
  snap = vol_data[vol_data["date"] == as_of_date].copy()
  if snap.empty:
    snap = vol_data[vol_data["date"] <= as_of_date]
    snap = snap[snap["date"] == snap["date"].max()]
  
  front_opts = ["1M", "3M"]
  long_opts = ["1Y", "2Y"]
  
  rows = []
  for tenor in SWAP_TENORS:
    sub = snap[snap[tenor_col] == tenor]
    
    front = sub[sub[opt_col].isin(front_opts)][vol_col].mean()
    long = sub[sub[opt_col].isin(long_opts)][vol_col].mean()
    
    row = {
      "swap_tenor": tenor,
      "front_gamma_vol": front,
      "long_gamma_vol": long,
      "front_minus_long": front - long,
    }
    
    for opt in front_opts + long_opts:
      v = sub[sub[opt_col] == opt][vol_col]
      row[f"vol_{opt}"] = v.iloc[0] if len(v) else np.nan
    
    rows.append(row)
  
  return pd.DataFrame(rows)


def compute_skew_smile(strike_surface):
  """
  Skew and smile from strike offsets.
  skew_25 = vol(+25) - vol(-25)
  smile = vol(-25) + vol(+25) - 2*vol(0)
  wing_skew = vol(+100) - vol(-100)
  """
  rows = []
  
  for (opt, tenor), group in strike_surface.groupby(["option_tenor", "swap_tenor"]):
    vols = dict(zip(group["strike_offset_bp"], group["normal_vol"]))
    
    atm = vols.get(0, np.nan)
    m25 = vols.get(-25, np.nan)
    p25 = vols.get(25, np.nan)
    m100 = vols.get(-100, np.nan)
    p100 = vols.get(100, np.nan)
    m50 = vols.get(-50, np.nan)
    p50 = vols.get(50, np.nan)
    
    rows.append({
      "option_tenor": opt,
      "swap_tenor": tenor,
      "label": swaption_label(opt, tenor),
      "atm_vol": atm,
      "skew_25bp": p25 - m25 if np.isfinite(p25) and np.isfinite(m25) else np.nan,
      "smile_25bp": m25 + p25 - 2 * atm if all(np.isfinite(x) for x in [m25, p25, atm]) else np.nan,
      "wing_skew_100bp": p100 - m100 if np.isfinite(p100) and np.isfinite(m100) else np.nan,
      "skew_50bp": p50 - m50 if np.isfinite(p50) and np.isfinite(m50) else np.nan,
    })
  
  return pd.DataFrame(rows).sort_values(["option_tenor", "swap_tenor"])


def pc_zscores(scores, window=None):
  """Rolling z-scores on PCA factor scores"""
  if window is None:
    window = Z_SCORE_WINDOW
  
  z = pd.DataFrame(index=scores.index)
  for col in scores.columns:
    roll_mean = scores[col].rolling(window, min_periods=window // 2).mean()
    roll_std = scores[col].rolling(window, min_periods=window // 2).std()
    z[f"{col}_zscore"] = (scores[col] - roll_mean) / roll_std
  
  return z
