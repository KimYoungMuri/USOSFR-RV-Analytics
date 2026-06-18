"""
SABR model calibration (Hagan normal vol approximation)
"""
import numpy as np
import pandas as pd
from scipy.optimize import least_squares

from src.config import SABR_BETA


def option_tenor_to_years(tenor):
    """Convert option tenor string to years"""
    tenor = tenor.upper().strip()
    if tenor.endswith("M"):
        return int(tenor[:-1]) / 12.0
    if tenor.endswith("Y"):
        return float(tenor[:-1])
    raise ValueError(f"Unknown option tenor: {tenor}")


def hagan_normal_vol(forward, strike, expiry, alpha, beta, rho, nu):
  """
  Hagan et al. normal vol approximation under SABR.
  forward/strike in rate terms (e.g. 4.25 = 4.25%).
  expiry in years, vol output in same units as market (annualized bp).
  """
  alpha = max(alpha, 1e-8)
  nu = max(nu, 1e-8)
  forward = max(forward, 1e-6)
  strike = max(strike, 1e-6)
  
  f_beta = forward ** beta
  
  if abs(forward - strike) < 1e-8:
    term1 = ((2.0 - 3.0 * rho ** 2) / 24.0) * nu ** 2 * expiry
    term2 = rho * beta * alpha * nu * expiry / (4.0 * f_beta)
    term3 = (2.0 - 3.0 * rho ** 2) * beta ** 2 * alpha ** 2 * expiry / (24.0 * f_beta ** 2)
    return alpha / f_beta * (1.0 + term1 + term2 + term3)
  
  fk_beta = (forward * strike) ** (beta / 2.0)
  log_fk = np.log(forward / strike)
  z = nu / alpha * fk_beta * log_fk
  
  if abs(z) < 1e-10:
    return hagan_normal_vol(forward, forward, expiry, alpha, beta, rho, nu)
  
  x_z = np.log((np.sqrt(1.0 - 2.0 * rho * z + z ** 2) + z - rho) / (1.0 - rho))
  
  prefix = alpha / (
    fk_beta * (
      1.0
      + (1.0 - beta) ** 2 / 24.0 * log_fk ** 2
      + (1.0 - beta) ** 4 / 1920.0 * log_fk ** 4
    )
  )
  
  correction = 1.0 + (
    ((2.0 - 3.0 * rho ** 2) / 24.0) * nu ** 2 * expiry
    + rho * beta * nu * alpha * expiry / (4.0 * fk_beta)
    + (2.0 - 3.0 * rho ** 2) * beta ** 2 * alpha ** 2 * expiry / (24.0 * fk_beta ** 2)
  )
  
  return prefix * z / x_z * correction


def calibrate_sabr(strikes, market_vols, forward, expiry, beta=None):
  """
  Calibrate alpha, rho, nu to market normal vols at given strikes.
  strikes: rate levels (same units as forward)
  market_vols: annualized normal vol in bp
  """
  if beta is None:
    beta = SABR_BETA
  
  strikes = np.asarray(strikes, dtype=float)
  market_vols = np.asarray(market_vols, dtype=float)
  
  mask = np.isfinite(strikes) & np.isfinite(market_vols) & (market_vols > 0)
  strikes = strikes[mask]
  market_vols = market_vols[mask]
  
  if len(strikes) < 3:
    return None
  
  atm_idx = np.argmin(np.abs(strikes - forward))
  alpha0 = market_vols[atm_idx] * (forward ** beta)
  x0 = np.array([alpha0, -0.2, 0.3])
  
  def residuals(params):
    alpha, rho, nu = params
    model = np.array([
      hagan_normal_vol(forward, k, expiry, alpha, beta, rho, nu)
      for k in strikes
    ])
    return model - market_vols
  
  result = least_squares(
    residuals,
    x0,
    bounds=([1e-4, -0.999, 1e-4], [500.0, 0.999, 5.0]),
    max_nfev=2000,
  )
  
  alpha, rho, nu = result.x
  fitted = np.array([
    hagan_normal_vol(forward, k, expiry, alpha, beta, rho, nu)
    for k in strikes
  ])
  rmse = np.sqrt(np.mean((fitted - market_vols) ** 2))
  
  return {
    "alpha": alpha,
    "beta": beta,
    "rho": rho,
    "nu": nu,
    "rmse": rmse,
    "fitted_vols": fitted,
    "market_vols": market_vols,
    "strikes": strikes,
    "success": result.success,
  }


def calibrate_sabr_surface(strike_surface, forward_rates, beta=None):
  """
  Calibrate SABR across the swaption grid.
  strike_surface: DataFrame with option_tenor, swap_tenor, strike_offset_bp, normal_vol
  forward_rates: dict {(option_tenor, swap_tenor): forward_rate} or DataFrame
  """
  results = []
  
  for (opt, tenor), group in strike_surface.groupby(["option_tenor", "swap_tenor"]):
    fwd = None
    if isinstance(forward_rates, dict):
      fwd = forward_rates.get((opt, tenor))
    else:
      row = forward_rates[
        (forward_rates["option_tenor"] == opt) & (forward_rates["swap_tenor"] == tenor)
      ]
      if len(row):
        fwd = row.iloc[0]["forward"]
    
    if fwd is None or not np.isfinite(fwd):
      continue
    
    expiry = option_tenor_to_years(opt)
    strikes = fwd + group["strike_offset_bp"].values / 100.0
    vols = group["normal_vol"].values
    
    fit = calibrate_sabr(strikes, vols, fwd, expiry, beta=beta)
    if fit is None:
      continue
    
    results.append({
      "option_tenor": opt,
      "swap_tenor": tenor,
      "forward": fwd,
      "expiry_years": expiry,
      "alpha": fit["alpha"],
      "beta": fit["beta"],
      "rho": fit["rho"],
      "nu": fit["nu"],
      "rmse": fit["rmse"],
      "success": fit["success"],
    })
  
  return pd.DataFrame(results)
