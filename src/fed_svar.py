"""Effect of Fed policy on unemployment: proxy SVAR in the style of Bauer & Swanson (2023, NBER Macro Annual).

VAR (monthly, 12 lags, constant), data from the "Monthly (original)" sheet of the SF Fed's monetary-policy-surprises
file (data/raw/mps/monetary-policy-surprises-data.xlsx; the sheet is the authors' SVAR dataset):
   log IP, unemployment rate, log CPI, log commodity prices (CRB), excess bond premium (EBP), 2-year Treasury yield,
plus the SF Fed proxy funds rate (data/raw/shadow/proxy-funds-rate-data.xlsx, "Monthly"), so the shock's effect on the
proxy funds rate is measured too. Sample: 1977-06 (proxy funds rate starts 1976-06, plus 12 lags) to 2019-12.
Identification: external instrument = a Bauer-Swanson monetary-policy surprise (1988-02 to 2019-12), INSTR below.
  Default MPS (the raw surprise): first-stage F = 9.5 (heteroskedasticity-robust 8.2), near the usual threshold of 10.
  MPS_ORTH (purged of predictable variation; the SF Fed data page calls it a better measure of new policy information) gives F = 3.6, a weak
  instrument, and implausibly large counterfactual effects (the 2022-23 hikes raising 2024 unemployment ~4 points);
  it is kept as a robustness variant (src/robustness.py). The impact
vector is the covariance of the VAR residuals with the instrument, scaled so the 2-year yield rises 1 point on impact.

The rule-based counterfactual tried first (Sims-Zha shock sequence to make the proxy funds rate follow the Fed
Board's Taylor / balanced-approach / inertial rules) was unstable and is not used: see output/METHOD_UNIFIED.md.
"""
import numpy as np
import pandas as pd

RAW = "data/raw/"
P = 12
INSTR = "MPS"
VARS = ["lip", "unemp", "lcpi", "lcrb", "ebp", "y2", "pfr"]


def data(instr=None):
    m = pd.read_excel(RAW + "mps/monetary-policy-surprises-data.xlsx", sheet_name="Monthly (original)", header=0)
    m = m.rename(columns={m.columns[0]: "date"}).set_index("date")
    m.index = pd.to_datetime(m.index).to_period("M")
    p = pd.read_excel(RAW + "shadow/proxy-funds-rate-data.xlsx", sheet_name="Monthly", header=0)
    p.index = pd.to_datetime(p.Date).dt.to_period("M")
    d = pd.DataFrame({"lip": 100 * np.log(m.IP), "unemp": m.unemp, "lcpi": 100 * np.log(m.CPI),
                      "lcrb": 100 * np.log(m["CRB Pcomm"]), "ebp": m.EBP, "y2": m["2y Treas"],
                      "pfr": p["Proxy funds rate"].astype(float)})
    return d, m[instr or INSTR]


def estimate(d, z, end="2019-12"):
    d = d.loc[:end].dropna()
    Y = d.values; T, n = Y.shape
    X = np.column_stack([np.ones(T - P)] + [Y[P - k:T - k] for k in range(1, P + 1)])
    B, *_ = np.linalg.lstsq(X, Y[P:], rcond=None)
    U = Y[P:] - X @ B
    idx = d.index[P:]
    zz = z.reindex(idx)
    ok = zz.notna().values
    cov = U[ok].T @ (zz.values[ok] - zz.values[ok].mean()) / ok.sum()
    b = cov / cov[VARS.index("y2")]                       # 2-year yield +1 on impact
    # first stage strength: regress y2 residual on instrument
    u2 = U[ok, VARS.index("y2")]; zc = zz.values[ok] - zz.values[ok].mean()
    beta = (zc @ u2) / (zc @ zc); e = u2 - beta * zc
    F = beta ** 2 / ((e @ e) / (len(e) - 2) / (zc @ zc))
    return B, b, U, idx, F, beta


def irf(B, b, H):
    n = len(b); A = [B[1 + (k - 1) * n:1 + k * n].T for k in range(1, P + 1)]
    out = np.zeros((H, n)); out[0] = b
    for h in range(1, H):
        out[h] = sum(A[k - 1] @ out[h - k] for k in range(1, min(h, P) + 1))
    return out


def bootstrap(d, z, n, seed, end="2019-12"):
    """Wild (Rademacher) residual bootstrap of VAR and instrument together (Mertens & Ravn 2013 style):
    Y*_t = B'X*_t + eta_t u_t,  z*_t = eta_t z_t. Returns a list of (B*, b*, beta*)."""
    rng = np.random.default_rng(seed)
    dd = d.loc[:end].dropna(); Y = dd.values; T, k = Y.shape
    B, b, U, idx, F, beta = estimate(d, z, end)
    zz = z.reindex(idx)
    out = []
    for _ in range(n):
        eta = rng.choice([-1.0, 1.0], size=T - P)
        Ys = Y.copy()
        for t in range(P, T):
            x = np.r_[1.0, np.concatenate([Ys[t - j] for j in range(1, P + 1)])]
            Ys[t] = x @ B + eta[t - P] * U[t - P]
        ds = pd.DataFrame(Ys, index=dd.index, columns=dd.columns)
        zs = pd.Series(zz.values * eta, index=idx)
        Bs, bs, _, _, _, betas = estimate(ds, zs, end)
        out.append((Bs, bs, betas))
    return out
