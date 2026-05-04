import numpy as np
import scipy.stats as stat
import matplotlib.pyplot as plt
from multiprocessing import Pool, cpu_count
from numpy.random import SeedSequence, default_rng

# =========================================================
# 1) PRODUCT SETUP
#    Mirae Asset ELS No.35682 (official schedule from notice PDF)
# =========================================================
SEED = 12345
PAR = 10000.0

# ---- valuation mode ----
# issue-date pricing  -> VALUATION_DATE = ISSUE_DATE, CURRENT_SPOT = INITIAL_REF
# mid-life MTM        -> set VALUATION_DATE to today, CURRENT_SPOT to current market spot,
#                        and past_knock_in_hit=True if KI was already touched historically.
ISSUE_DATE = np.datetime64("2024-11-14")
VALUATION_DATE = ISSUE_DATE
MATURITY_DATE = np.datetime64("2027-11-12")

# Official initial reference prices from the notice PDF
INITIAL_REF = np.array([138.8400, 146.7600, 5949.1700], dtype=float)  # [AMD, NVDA, S&P500]
CURRENT_SPOT = INITIAL_REF.copy()  # change this for MTM

# Official barriers from the notice PDF
EARLY_OBS_DATES = np.array([
    "2025-11-11",
    "2026-11-09",
    "2027-11-03",
], dtype="datetime64[D]")

# Settlement dates are not shown in the notice PDF.
# Approximation:
# - 1st and 2nd early redemption: use obs date as payment date
# - final redemption / maturity redemption: pay on maturity date
EARLY_PAY_DATES = np.array([
    "2025-11-11",
    "2026-11-09",
    "2027-11-12",
], dtype="datetime64[D]")

EARLY_BARRIERS = np.array([0.85, 0.85, 0.75], dtype=float)
KI_BARRIER = 0.45
MONTHLY_COUPON_BARRIER = 0.00

# Monthly coupon evaluation dates from the notice PDF
MONTHLY_COUPON_DATES = np.array([
    "2024-12-10", "2025-01-09", "2025-02-10", "2025-03-11", "2025-04-09", "2025-05-09",
    "2025-06-10", "2025-07-09", "2025-08-08", "2025-09-09", "2025-10-02", "2025-11-11",
    "2025-12-09", "2026-01-09", "2026-02-10", "2026-03-10", "2026-04-09", "2026-05-11",
    "2026-06-09", "2026-07-09", "2026-08-10", "2026-09-09", "2026-10-07", "2026-11-09",
    "2026-12-09", "2027-01-08", "2027-02-04", "2027-03-09", "2027-04-09", "2027-05-10",
    "2027-06-08", "2027-07-09", "2027-08-10", "2027-09-08", "2027-10-07", "2027-11-03",
], dtype="datetime64[D]")

FINAL_OBS_DATE = np.datetime64("2027-11-03")

# ---- market model inputs ----
# NOTE:
# r = discount rate
# q = dividend yield vector
# sigma = annualized vol vector
r = 0.03270
q = np.array([0.00, 0.00, 0.015], dtype=float)  # example only; verify / calibrate as needed
sigma = np.array([0.7222, 0.6092, 0.2520], dtype=float)  # [AMD, NVDA, S&P500]

corr_matrix = np.array([
    [1.0,    0.5804, 0.5883],
    [0.5804, 1.0,    0.6473],
    [0.5883, 0.6473, 1.0   ],
], dtype=float)

# Monthly coupon rate is NOT shown in the basis-price notice PDF.
# This default is inferred from your old 1Y payoff factor 1.1140 -> 11.4% total over 12 months.
# Please replace with the exact contractual monthly coupon rate from the prospectus.
MONTHLY_COUPON_RATE = 0.1140 / 12.0  # inferred placeholder = 0.95% per month

# KI monitoring options
USE_BROWNIAN_BRIDGE_FOR_KI = True

# Monte Carlo config
ITERATIONS = [1000, 5000, 10000, 50000]
PAIR_PRICE = 8185.04  # optional benchmark comparison


# =========================================================
# 2) UTILITIES
# =========================================================
def make_psd_corr(corr, eps=1e-12):
    corr = 0.5 * (corr + corr.T)
    eigval, eigvec = np.linalg.eigh(corr)
    eigval = np.clip(eigval, eps, None)
    corr_psd = eigvec @ np.diag(eigval) @ eigvec.T
    d = np.sqrt(np.diag(corr_psd))
    corr_psd = corr_psd / np.outer(d, d)
    corr_psd = 0.5 * (corr_psd + corr_psd.T)
    np.fill_diagonal(corr_psd, 1.0)
    return corr_psd


def split_work(total_n, n_workers):
    q_, r_ = divmod(total_n, n_workers)
    return [q_ + (1 if i < r_ else 0) for i in range(n_workers)]


def busday_count(start_date, end_date):
    return int(np.busday_count(start_date, end_date))


def yearfrac_bus252(start_date, end_date):
    return busday_count(start_date, end_date) / 252.0


def future_dates(dates, valuation_date):
    return dates[dates > valuation_date]


def discount_factor(payment_date):
    t = yearfrac_bus252(VALUATION_DATE, payment_date)
    return np.exp(-r * t)


def event_indices(event_dates, valuation_date):
    return np.array([busday_count(valuation_date, d) for d in event_dates], dtype=int)


# =========================================================
# 3) PRECOMPUTED SCHEDULE
# =========================================================
if not (VALUATION_DATE < MATURITY_DATE):
    raise ValueError("VALUATION_DATE must be earlier than MATURITY_DATE.")

corr_matrix = make_psd_corr(corr_matrix)
chol = np.linalg.cholesky(corr_matrix)

remaining_coupon_dates = future_dates(MONTHLY_COUPON_DATES, VALUATION_DATE)
remaining_early_obs_dates = future_dates(EARLY_OBS_DATES, VALUATION_DATE)

# Match remaining early payment dates / barriers with remaining early obs dates
early_mask = EARLY_OBS_DATES > VALUATION_DATE
remaining_early_pay_dates = EARLY_PAY_DATES[early_mask]
remaining_early_barriers = EARLY_BARRIERS[early_mask]

n_steps = busday_count(VALUATION_DATE, MATURITY_DATE)
if n_steps <= 0:
    raise ValueError("No remaining life. Check VALUATION_DATE / MATURITY_DATE.")

coupon_idx = event_indices(remaining_coupon_dates, VALUATION_DATE)
early_obs_idx = event_indices(remaining_early_obs_dates, VALUATION_DATE)
final_obs_idx = busday_count(VALUATION_DATE, FINAL_OBS_DATE)
maturity_idx = n_steps

coupon_df = np.array([discount_factor(d) for d in remaining_coupon_dates], dtype=float)
early_principal_df = np.array([discount_factor(d) for d in remaining_early_pay_dates], dtype=float)
maturity_principal_df = discount_factor(MATURITY_DATE)

# Prefix sum for coupon PVs
coupon_cash = PAR * MONTHLY_COUPON_RATE * coupon_df
coupon_prefix_pv = np.concatenate([[0.0], np.cumsum(coupon_cash)])


# =========================================================
# 4) PATH GENERATION
# =========================================================
def simulate_paths_gaussian(n_paths, rng):
    """
    Business-day Euler exact lognormal simulation with Gaussian dependence.
    Shape returned: (n_paths, n_steps + 1, 3)
    """
    z = rng.standard_normal((n_paths, n_steps, 3)) @ chol.T
    dt = 1.0 / 252.0

    drift = (r - q - 0.5 * sigma**2) * dt
    diff = sigma * np.sqrt(dt)

    log_increments = drift + diff * z
    log_path = np.cumsum(log_increments, axis=1)
    log_path = np.concatenate(
        [np.zeros((n_paths, 1, 3), dtype=float), log_path],
        axis=1
    )

    prices = CURRENT_SPOT * np.exp(log_path)
    return prices


# =========================================================
# 5) KNOCK-IN CHECK
# =========================================================
def knock_in_hit(prices, rng, past_knock_in_hit=False, use_bridge=True):
    """
    KI if ANY underlying breaches 45% of initial reference level during the life.

    prices shape: (n_paths, n_steps + 1, 3)
    """
    if past_knock_in_hit:
        return np.ones(prices.shape[0], dtype=bool)

    n_paths = prices.shape[0]
    ki_any = np.zeros(n_paths, dtype=bool)

    for j in range(3):
        barrier = KI_BARRIER * INITIAL_REF[j]
        s0 = prices[:, :-1, j]
        s1 = prices[:, 1:, j]

        hit = (s0 <= barrier) | (s1 <= barrier)

        if use_bridge:
            mask = ~hit
            if np.any(mask):
                x = np.log(s0[mask] / barrier)
                y = np.log(s1[mask] / barrier)

                # GBM lower barrier bridge approximation in log space
                p_hit = np.exp(-2.0 * x * y / (sigma[j]**2 * (1.0 / 252.0)))
                p_hit = np.clip(p_hit, 0.0, 1.0)

                u = rng.random(p_hit.shape)
                bridge_hit = u < p_hit
                hit[mask] = bridge_hit

        ki_asset = np.any(hit, axis=1)
        ki_any |= ki_asset

    return ki_any


# =========================================================
# 6) PAYOFF ENGINE
# =========================================================
def price_from_paths(prices, rng, past_knock_in_hit=False):
    """
    Cashflow logic:
    - Monthly coupon barrier = 0% -> remaining monthly coupons are paid while note is alive.
    - If early redemption occurs on the first satisfied early obs date:
        principal paid on the corresponding early pay date
        + coupons up to and including that coupon date
    - If no early redemption:
        principal paid at maturity
        and based on final obs:
            * if KI never hit: principal repayment = PAR
            * if KI hit: principal repayment = PAR * min(S_T / InitialRef)
        + all remaining coupons (coupon barrier 0%)

    NOTE:
    - Early settlement dates are approximated because they are not shown in the basis-price notice.
    - Final principal is discounted to MATURITY_DATE.
    """
    n_paths = prices.shape[0]
    pv = np.zeros(n_paths, dtype=float)

    # -----------------------------------------------------
    # 1) Early redemption check
    # -----------------------------------------------------
    autocalled = np.zeros(n_paths, dtype=bool)
    autocall_k = np.full(n_paths, -1, dtype=int)

    for k, step_idx in enumerate(early_obs_idx):
        cond = np.all(prices[:, step_idx, :] >= remaining_early_barriers[k] * INITIAL_REF, axis=1)
        newly = (~autocalled) & cond
        autocall_k[newly] = k
        autocalled[newly] = True

    # -----------------------------------------------------
    # 2) Coupons for autocalled paths
    # -----------------------------------------------------
    if np.any(autocalled):
        idx_ac = autocall_k[autocalled]

        # number of remaining coupon dates paid until (and including) autocall obs date
        coupon_count = np.array([
            np.searchsorted(coupon_idx, early_obs_idx[k], side="right")
            for k in idx_ac
        ], dtype=int)

        coupon_pv = coupon_prefix_pv[coupon_count]
        principal_pv = PAR * early_principal_df[idx_ac]

        pv[autocalled] = coupon_pv + principal_pv

    # -----------------------------------------------------
    # 3) Non-autocalled paths -> maturity payoff
    # -----------------------------------------------------
    alive = ~autocalled
    if np.any(alive):
        prices_alive = prices[alive]

        ki = knock_in_hit(
            prices_alive,
            rng=rng,
            past_knock_in_hit=past_knock_in_hit,
            use_bridge=USE_BROWNIAN_BRIDGE_FOR_KI
        )

        final_ratio = np.min(prices_alive[:, final_obs_idx, :] / INITIAL_REF, axis=1)

        principal_at_maturity = np.where(
            ki,
            PAR * final_ratio,
            PAR
        )

        all_remaining_coupon_pv = coupon_prefix_pv[len(coupon_idx)]
        pv[alive] = all_remaining_coupon_pv + principal_at_maturity * maturity_principal_df

    return pv


# =========================================================
# 7) PARALLEL MONTE CARLO
# =========================================================
def worker_sum_price(args):
    n_paths, child_ss, past_knock_in_hit = args
    rng = default_rng(child_ss)

    prices = simulate_paths_gaussian(n_paths, rng)
    pv = price_from_paths(prices, rng, past_knock_in_hit=past_knock_in_hit)

    return pv.sum(), np.sum(pv * pv), n_paths


def price_els_mc(path_counts, seed=SEED, past_knock_in_hit=False):
    predicted_prices = []
    stderrs = []

    max_workers = cpu_count()

    for N in path_counts:
        n_workers = min(max_workers, N)
        chunk_sizes = split_work(N, n_workers)

        iter_ss = SeedSequence([seed, N, int(VALUATION_DATE.astype("datetime64[D]").astype(int))])
        child_seqs = iter_ss.spawn(n_workers)

        with Pool(processes=n_workers) as pool:
            results = pool.map(
                worker_sum_price,
                [(chunk_sizes[i], child_seqs[i], past_knock_in_hit) for i in range(n_workers)]
            )

        sum_x = sum(r[0] for r in results)
        sum_x2 = sum(r[1] for r in results)
        total_n = sum(r[2] for r in results)

        mean = sum_x / total_n
        var = max(sum_x2 / total_n - mean**2, 0.0)
        se = np.sqrt(var / total_n)

        predicted_prices.append(mean)
        stderrs.append(se)

    return predicted_prices, stderrs


# =========================================================
# 8) RUN
# =========================================================
if __name__ == "__main__":
    # If pricing today, update these:
    # VALUATION_DATE = np.datetime64("2026-03-09")
    # CURRENT_SPOT = np.array([..., ..., ...], dtype=float)
    # and set past_knock_in_hit=True if historically KI already happened.
    past_knock_in_hit = False

    print("VALUATION_DATE:", VALUATION_DATE)
    print("CURRENT_SPOT:", CURRENT_SPOT)
    print("INITIAL_REF:", INITIAL_REF)
    print("Remaining coupon dates:", len(remaining_coupon_dates))
    print("Remaining early obs dates:", remaining_early_obs_dates)
    print("Monthly coupon rate (placeholder unless verified):", MONTHLY_COUPON_RATE)

    predicted_prices, stderrs = price_els_mc(
        path_counts=ITERATIONS,
        seed=SEED,
        past_knock_in_hit=past_knock_in_hit
    )

    print("\nPredicted Prices:", predicted_prices)
    print("Std Errors:", stderrs)

    if PAIR_PRICE is not None:
        error_list = [abs(p - PAIR_PRICE) for p in predicted_prices]
        error_rate = [abs(p - PAIR_PRICE) / PAIR_PRICE * 100 for p in predicted_prices]
        print("Errors:", error_list)
        print("Error Rates (%):", error_rate)

    plt.figure(figsize=(8, 4))
    plt.plot(ITERATIONS, predicted_prices, marker='o', label='MC Price')
    if PAIR_PRICE is not None:
        plt.axhline(PAIR_PRICE, linestyle='--', label='Benchmark / Pair Price')
    plt.xscale('log')
    plt.xlabel('Number of paths')
    plt.ylabel('Price')
    plt.title('ELS 35682 Monte Carlo Pricing (Corrected Product Structure)')
    plt.legend()
    plt.tight_layout()
    plt.show()