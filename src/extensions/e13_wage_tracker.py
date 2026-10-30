"""Extension 13: did wages slow in 2020, as the model's wage equation says the job-market collapse should have made
them? Atlanta Fed Wage Growth Tracker (median 12-month wage growth of the same workers a year apart, so not distorted
by low-wage layoffs; FRED FRBATLWGT12MMUMHGO) next to the employment cost index used by the model (ECI, B&B data
file), and the model's own prediction for ECI wage growth given actual V/U (wage equation estimated 1990-2019,
simulated from 2020Q1). Writes output/ext/e13_wage_tracker.csv; log = stdout."""
import sys
sys.path.insert(0, __file__.rsplit("/src/", 1)[0] + "/src")
import numpy as np
import pandas as pd
import unified_model as UM, bb_model as m, decompose as D

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
d = UM.quarterly(); x = m.build(d); D.PROD_LAG = 0; x, _ = UM.add_greed(x)
est = UM.estimate_with_greed(x, m.estimate(x, D.PROD)); C = D.coefs(est)
pos = x.index.get_loc(UM.START); n = len(x)
a = {c: x[c].values.copy() for c in ["gp", "gw", "exp1", "exp10", "catch_up", "vu", "gpty"]}
gw = a["gw"].copy(); Cw = C["gw"]
for t in range(pos, n):   # wage equation alone, actual prices/expectations/V/U (one-equation dynamic prediction)
    gw[t] = (Cw[0] + Cw[1:5] @ gw[t-1:t-5:-1] + Cw[5:9] @ a["vu"][t-1:t-5:-1] + Cw[9:13] @ a["exp1"][t-1:t-5:-1]
             + Cw[13:17] @ a["catch_up"][t-1:t-5:-1] + Cw[17] * a["gpty"][t-1])
w = pd.read_csv(ROOT + "data/raw/ext/fred/FRBATLWGT12MMUMHGO.csv", index_col=0, parse_dates=True).iloc[:, 0].resample("QS").mean()
out = pd.DataFrame({"eci_actual_4q": pd.Series(a["gw"], index=x.index).rolling(4).mean(),
                    "eci_predicted_4q": pd.Series(gw, index=x.index).rolling(4).mean(),
                    "atlanta_fed_tracker": w.reindex(x.index)}).loc["2019-01-01":"2022-10-01"]
out.round(2).to_csv(ROOT + "output/ext/e13_wage_tracker.csv")
print(out.round(2).to_string())
