"""Python port of the Bernanke-Blanchard (2025, AEJ:Macro) model, following Lorenzoni's
R replication package (github.com/luigilor/bernanke-blanchard23, empirics/code/bl_be_us.R).

Equation structure, sample windows and restrictions are copied from that script.
Nothing here is hand-chosen: every coefficient comes from OLS on the data in data/raw/.
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm

RAW = "data/raw/"
# Wage-equation variant (extension, not in Bernanke-Blanchard): "bb" = the original (V/U linear, estimated 1990-2019);
# "linear2024" = same, estimated 1990-2024; "kink2024" = adds max(V/U - TAU, 0) (Benigno-Eggertsson's inverse-L idea:
# steeper above the threshold), estimated 1990-2024. TAU = 1 (their estimated threshold is near unity).
WAGE = "bb"
TAU = 1.0


def load(path):
    d = pd.read_csv(path, sep=";", decimal=",", encoding="utf-8-sig")
    d = d.rename(columns={d.columns[0]: "date"})
    d["date"] = pd.to_datetime(d["date"])
    return d.set_index("date").astype(float)


def build(d):
    """Construct growth rates, lags and catch-up exactly as in bl_be_us.R lines 21-80."""
    x = d.copy()
    x["logcpi"] = np.log(x.cpi)
    x["gp"] = 400 * x.logcpi.diff()
    x["gw"] = 400 * np.log(x.lci).diff()
    x["grpf"] = 400 * np.log(x.food_cpi / x.lci).diff()
    x["grpe"] = 400 * np.log(x.energy_cpi / x.lci).diff()
    g = 400 * np.log(x.productivity).diff()
    x["gpty"] = 0.125 * sum(g.shift(k) for k in range(8))  # 8-quarter moving average
    x["vuk"] = (x.vu - TAU).clip(lower=0)
    for v in ["gp", "grpf", "grpe", "gpty", "gw", "vu", "vuk", "exp1", "exp10", "shortage"]:
        for i in range(1, 5):
            x[f"{v}_l{i}"] = x[v].shift(i)
    x["catch_up"] = 0.25 * (x.gp + x.gp_l1 + x.gp_l2 + x.gp_l3) - x.exp1_l4
    for i in range(1, 5):
        x[f"catch_up_l{i}"] = x.catch_up.shift(i)
    return x.loc["1990-01-01":]


def L(v, n=4, cur=True):
    return ([v] if cur else []) + [f"{v}_l{i}" for i in range(1, n + 1)]


# regressors in the same order as the R formulas / published coefficient tables
def wage_X():
    k = L("vuk", cur=False) if WAGE == "kink2024" else []
    return L("gw", cur=False) + L("vu", cur=False) + L("exp1", cur=False) + L("catch_up", cur=False) + ["gpty_l1"] + k


def price_X(prod="gpty_l1"):
    return L("gp", cur=False) + L("gw") + L("grpe") + L("grpf") + [prod] + L("shortage")


def exp10_X():
    return L("gp") + L("exp10", cur=False)


def exp1_X():
    return L("exp1", cur=False) + L("exp10") + L("gp")


class _Rls:
    """Restricted least squares: min |y-Xb|^2  s.t.  R b = q.  Closed form:
       b_r = b - A R'(R A R')^-1 (R b - q),  A = (X'X)^-1.
       Cov = s2 * (A - A R'(R A R')^-1 R A), s2 = RSS_r / (n - k + rank(R))."""

    def __init__(self, y, X, R, q, cols):
        A = np.linalg.inv(X.T @ X)
        b = A @ X.T @ y
        M = A @ R.T @ np.linalg.inv(R @ A @ R.T)
        br = b - M @ (R @ b - q)
        self.resid = y - X @ br
        n, k = X.shape
        self.s2 = float(self.resid @ self.resid) / (n - k + R.shape[0])
        self._cov = self.s2 * (A - M @ R @ A)
        self.params = pd.Series(br, index=cols)
        self.nobs = n

    def cov_params(self):
        return pd.DataFrame(self._cov, index=self.params.index, columns=self.params.index)


def rls(df, y, X, const, n_sum):
    """OLS with the first `n_sum` regressors' coefficients restricted to sum to 1.
    (Same restriction as restrict.matrix / restrict.rhs=1 in systemfit.)
    Returns params and covariance matrix."""
    Xm = df[X].copy()
    if const:
        Xm.insert(0, "const", 1.0)
    cols = list(Xm.columns)
    ok = df[[y] + X].notna().all(axis=1)
    Xm, yy = Xm[ok], df.loc[ok, y]
    R = np.zeros((1, len(cols)))
    idx = [cols.index(c) for c in n_sum]
    R[0, idx] = 1.0
    res = _Rls(yy.values, Xm.values, R, np.array([1.0]), cols)
    return res, cols, int(ok.sum())


def estimate(x, prod="gpty_l1"):
    pre = x.loc[:"2019-10-01"]  # R: tsdata[1:120] = 1990Q1..2019Q4
    out = {}
    out["gw"] = rls(pre if WAGE == "bb" else x, "gw", wage_X(), True, L("gw", cur=False) + L("exp1", cur=False))
    out["gp"] = rls(x, "gp", price_X(prod), True, L("gp", cur=False) + L("gw"))
    out["exp10"] = rls(pre, "exp10", exp10_X(), False, exp10_X())
    out["exp1"] = rls(pre, "exp1", exp1_X(), False, exp1_X())
    return out
