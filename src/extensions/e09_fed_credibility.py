"""Extension 9: did the Fed's 2020 framework or its 2021 messages raise inflation expectations directly?
Market measures, daily (FRED): T5YIE (5-year breakeven), T10YIE (10-year breakeven), T5YIFR (5-year, 5-year forward
breakeven: expected inflation 5-10 years ahead, the usual gauge of long-run anchoring).
Events: August 27, 2020, the FOMC's revised Statement on Longer-Run Goals and Monetary Policy Strategy (average
inflation targeting; Fed press release of that date); the eight 2021 FOMC statement days (Jan 27, Mar 17, Apr 28,
Jun 16, Jul 28, Sep 22, Nov 3, Dec 15; Fed meeting calendar).
Measure: 2-day change (close of the day before to close of the day after). Benchmark: all 2-day changes 2015-2019,
whose 5th-95th percentile shows what an ordinary move looks like. Also: the level of the 5y5y forward in 2021-22
against its 2015-2019 range (anchoring).
Writes output/ext/e09_fed_credibility.csv; log = stdout."""
import numpy as np
import pandas as pd

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
EVENTS = {"2020-08-27": "New framework (average inflation targeting)", "2021-01-27": "FOMC", "2021-03-17": "FOMC",
          "2021-04-28": "FOMC", "2021-06-16": "FOMC", "2021-07-28": "FOMC", "2021-09-22": "FOMC", "2021-11-03": "FOMC",
          "2021-12-15": "FOMC"}
S = {k: pd.to_numeric(pd.read_csv(ROOT + f"data/raw/ext/fred/{k}.csv", index_col=0, parse_dates=True).iloc[:, 0], errors="coerce").dropna()
     for k in ["T5YIE", "T10YIE", "T5YIFR"]}
rows = []
for k, s in S.items():
    ch2 = (s.shift(-1) - s.shift(1)).dropna()
    bench = ch2["2015":"2019"]
    lo, hi = np.percentile(bench, [5, 95])
    for d, what in EVENTS.items():
        t = pd.Timestamp(d)
        i = s.index.get_indexer([t])[0]
        if i < 1:
            continue
        rows.append(dict(series=k, date=d, event=what, change_2day=float(s.iloc[i + 1] - s.iloc[i - 1]), ordinary_p5=lo, ordinary_p95=hi))
out = pd.DataFrame(rows)
out["outside_ordinary_range"] = (out.change_2day < out.ordinary_p5) | (out.change_2day > out.ordinary_p95)
f = S["T5YIFR"]
lvl = pd.DataFrame({"T5YIFR_2015_19_min": [f["2015":"2019"].min()], "T5YIFR_2015_19_max": [f["2015":"2019"].max()],
                    "T5YIFR_2015_19_mean": [f["2015":"2019"].mean()], "T5YIFR_2021_22_max": [f["2021":"2022"].max()],
                    "T5YIFR_2021_22_mean": [f["2021":"2022"].mean()], "T5YIFR_2020_08_26": [f[:"2020-08-26"].iloc[-1]],
                    "T5YIFR_2021_12_31": [f[:"2021-12-31"].iloc[-1]]})
out.round(3).to_csv(ROOT + "output/ext/e09_fed_credibility.csv", index=False)
lvl.round(3).to_csv(ROOT + "output/ext/e09_fed_credibility_levels.csv", index=False)
pd.set_option("display.width", 200)
print(out.round(3).to_string()); print(lvl.round(2).T.to_string())
