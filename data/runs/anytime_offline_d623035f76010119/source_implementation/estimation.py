"""Exploratory structural beta fitting; identification flags are retained."""
import numpy as np
from scipy.optimize import least_squares

def predicted_orders(params, demands, net_inventory, supply_line, order_limit=None):
    theta, alpha, beta, target = params
    forecast = 4.0
    expected = []
    for demand in demands:
        forecast = theta * demand + (1 - theta) * forecast
        expected.append(forecast)
    prediction = np.maximum(0, np.asarray(expected) + alpha * (target - net_inventory - beta * supply_line))
    return np.minimum(order_limit, prediction) if order_limit is not None else prediction

def estimate_beta(frame, beta_upper=2.0):
    frame = frame.sort_values("week")
    y = frame.order.to_numpy(float)
    order_limit = None
    if 'order_limit' in frame:
        limits = frame.order_limit.unique()
        if len(limits) != 1 or not np.isfinite(limits[0]) or limits[0] <= 0:
            raise ValueError('One positive constant order limit is required per trajectory.')
        order_limit = float(limits[0])
        if ((y < 0) | (y > order_limit)).any():
            raise ValueError('Observed orders violate the declared game limit.')
    d = frame.demand.to_numpy(float)
    ni = frame.net_inventory.to_numpy(float)
    sl = frame.supply_line.to_numpy(float)
    blank = dict(theta=np.nan, alpha=np.nan, beta=np.nan, target=np.nan,
                 rmse=np.nan, r2=np.nan, jac_condition=np.nan, usable=False,
                 fit_flag="insufficient_variation", n=len(y), order_limit=order_limit,
                 cap_hit_rate=float(np.mean(y==order_limit)) if order_limit is not None else 0.)
    if len(y) < 16 or np.std(y) < 1e-8 or np.std(ni) < 1e-8 or np.std(sl) < 1e-8:
        return blank
    lo = np.array([0, 0, 0, 0.0])
    hi = np.array([1, 1, beta_upper, 10000.0])
    fits = []
    for theta in (.2, .8):
        for beta in (.15, min(.85, beta_upper * .85)):
            target = np.clip(np.median(ni + beta * sl), 1, 9999)
            fit = least_squares(lambda p: predicted_orders(p, d, ni, sl, order_limit) - y,
                                [theta, .3, beta, target], bounds=(lo, hi),
                                x_scale="jac", max_nfev=3000)
            fits.append(fit)
    fit = min(fits, key=lambda f: np.sum(f.fun ** 2))
    theta, alpha, beta, target = fit.x
    norms = np.linalg.norm(fit.jac, axis=0)
    scaled = fit.jac / np.maximum(norms, 1e-12)
    jac_condition = float(np.linalg.cond(scaled))
    r2 = 1 - np.sum(fit.fun ** 2) / np.sum((y - y.mean()) ** 2)
    flags = []
    if not fit.success: flags.append("optimizer_failed")
    if alpha < .02: flags.append("weak_inventory_response")
    if np.linalg.matrix_rank(scaled) < 4 or jac_condition > 1e6:
        flags.append("weak_identification")
    # θ endpoints are allowed; α/β/target boundary fits get flagged.
    if any(np.isclose(fit.x[1:], lo[1:], atol=1e-5)) or any(np.isclose(fit.x[1:], hi[1:], atol=1e-5)):
        flags.append("parameter_boundary")
    if np.isclose(beta, beta_upper, atol=1e-5) or np.isclose(target, 10000, atol=1e-5):
        flags.append("upper_parameter_limit")
    if r2 < 0: flags.append("poor_fit")
    if order_limit is not None and np.sum((y>0) & (y<order_limit)) < 8:
        flags.append('too_few_interior_orders')
    fatal_flags = set(flags) - {"parameter_boundary"}
    return dict(theta=theta, alpha=alpha, beta=beta, target=target,
                rmse=float(np.sqrt(np.mean(fit.fun ** 2))), r2=float(r2),
                jac_condition=jac_condition, usable=not fatal_flags,
                fit_flag=";".join(flags) or "ok", n=len(y), order_limit=order_limit,
                cap_hit_rate=float(np.mean(y==order_limit)) if order_limit is not None else 0.)
