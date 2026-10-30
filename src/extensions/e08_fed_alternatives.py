"""Extension 8: the Fed lines under other ways of measuring the Fed's effect.
  svar_mps   the model's proxy SVAR, instrument = Bauer-Swanson MPS (baseline)
  svar_jk    same SVAR, instrument = Jarocinski-Karadi monetary-policy shock (MP_median: high-frequency surprise with
             the central-bank-information component removed by sign restrictions; data/raw/ext/jk/, 1990-2023)
  lp_mps     local projections (Jorda 2005), instrumented: for each horizon h, y_t+h on the 2-year yield at t,
             instrumented by the surprise, with 12 lags of all seven VAR variables as controls; the response of the
             proxy funds rate and unemployment per +1 point 2-year yield, h = 0..60 months (zero after 60)
  lp_jk      local projections with the Jarocinski-Karadi shock
Each impulse response replaces the SVAR's in unified_model.fed_effect (same episode windows and counterfactual
rule), then the full model gives the Fed lines (point estimates, 2021-24 totals, official % change).
Writes output/ext/e08_fed_alternatives.csv; log = stdout (first-stage F statistics, impulse responses at 12/24/36 m)."""
import sys
sys.path.insert(0, __file__.rsplit("/src/", 1)[0] + "/src")
import numpy as np
import pandas as pd
import unified_model as UM, fed_svar as S, bb_model as m, decompose as D, unified_data as U

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
H = 61


def jk_shock():
    j = pd.read_csv(ROOT + "data/raw/ext/jk/shocks_fed_jk_m.csv")
    j.index = pd.PeriodIndex([f"{y}-{mm:02d}" for y, mm in zip(j.year, j.month)], freq="M")
    return j.MP_median


def lp_iv(d, z, end="2019-12"):
    dd = d.loc[:end].dropna()
    Y = dd.values; T, n = Y.shape
    ctrl = np.column_stack([np.ones(T)] + [np.r_[np.full((k, n), np.nan), Y[:-k]] for k in range(1, S.P + 1)])
    zz = z.reindex(dd.index).values
    iy2 = S.VARS.index("y2")
    R = np.zeros((H, n)); F = None
    for h in range(H):
        lead = np.r_[Y[h:], np.full((h, n), np.nan)]
        ok = np.isfinite(ctrl).all(1) & np.isfinite(zz) & np.isfinite(lead).all(1)
        Xc, x, zi, yl = ctrl[ok], Y[ok, iy2], zz[ok], lead[ok]
        # partial out controls
        P_ = lambda v: v - Xc @ np.linalg.lstsq(Xc, v, rcond=None)[0]
        xr, zr, yr = P_(x), P_(zi), P_(yl)
        g = (zr @ xr) / (zr @ zr)
        if h == 0:
            e = xr - g * zr; F = g ** 2 / ((e @ e) / (len(e) - Xc.shape[1] - 1) / (zr @ zr))
        R[h] = (zr @ yr) / (zr @ xr)                      # IV: response per +1 point 2-year yield
    return R, F


def irf_padded(R, length):
    out = np.zeros((length, R.shape[1])); out[:len(R)] = R
    return out


def main():
    md, z_mps = S.data()
    z_jk = jk_shock()
    d = UM.quarterly(); x = m.build(d); D.PROD_LAG = 0; x, _ = UM.add_greed(x)
    est = UM.estimate_with_greed(x, m.estimate(x, D.PROD)); C = D.coefs(est)
    ok, _ = UM.okun(d); bev, _ = UM.beveridge(d)
    pi = U.nipa({"DPCERG"}).DPCERG; f = (100 * (pi / pi.shift(4) - 1)) / (100 * np.log(pi).diff(4))
    variants = {}
    B, b, Uu, idx, F, beta = S.estimate(md, z_mps); variants["svar_mps"] = (S.irf(B, b, 240), F, (B, b, beta))
    B2, b2, _, _, F2, beta2 = S.estimate(md, z_jk); variants["svar_jk"] = (S.irf(B2, b2, 240), F2, (B2, b2, beta2))
    R3, F3 = lp_iv(md, z_mps); variants["lp_mps"] = (irf_padded(R3, 240), F3, (B, b, beta))
    R4, F4 = lp_iv(md, z_jk); variants["lp_jk"] = (irf_padded(R4, 240), F4, (B, b, beta))
    orig_irf = S.irf
    rows = []
    for name, (R, Fs, sv) in variants.items():
        S.irf = (lambda RR: (lambda B_, b_, H_: RR[:H_]))(R)
        res, du, _ = UM.run_once(d, x, C, UM.FISCAL, sv, ok, bev.values)
        S.irf = orig_irf
        yy = UM.yoy(UM.tidy(res), x).mul(f.reindex(res.index), axis=0)
        q4 = [t.quarter == 4 and t.year >= 2021 for t in yy.index]
        iu, ip = S.VARS.index("unemp"), S.VARS.index("pfr")
        rows.append(dict(variant=name, first_stage_F=Fs, unemp_irf_12=R[12, iu], unemp_irf_24=R[24, iu], unemp_irf_36=R[36, iu],
                         pfr_irf_0=R[0, ip], pfr_irf_12=R[12, ip],
                         fed_easing_2021_24=yy.fed_easing[q4].sum(), fed_hikes_2021_24=yy.fed_hikes[q4].sum(),
                         fed_net_2021_24=yy[["fed_easing", "fed_hikes", "fed_pre2020"]][q4].sum().sum(),
                         hikes_unemp_2024Q4=du.fed_hikes.iloc[-1], easing_unemp_2021Q4=du.fed_easing.loc["2021-10-01"]))
        print(rows[-1], flush=True)
    out = pd.DataFrame(rows).set_index("variant")
    out.round(3).to_csv(ROOT + "output/ext/e08_fed_alternatives.csv")
    pd.set_option("display.width", 250); print(out.round(2).to_string())


if __name__ == "__main__":
    main()
