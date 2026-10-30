"""This project's numbers next to published estimates of the same thing. Writes output/COMPARISON.md.
Published numbers are copied from the sources quoted in output/CAUSES_SOURCES.md and output/REPORT.md; the SF Fed
supply/demand series is read from its data file (data/raw/sf_fed/). Run after src/unified_model.py and
src/fed_late_report.py."""
import pandas as pd

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
o = pd.read_csv(ROOT + "output/unified_causes_quarterly.csv", index_col=0)
fl = pd.read_csv(ROOT + "output/fed_late.csv").set_index(["scenario", "quarter"])
sf = pd.read_excel(ROOT + "data/raw/sf_fed/supply-demand-pce-inflation.xlsx", sheet_name="Data")
sf = sf.set_index(sf.time_month.str.strip())
sf.columns = [c.replace(" (headline, y/y)", "") for c in sf.columns]

DEMAND = ["trump", "biden", "fed_easing", "fed_hikes", "pentup"]
SUPPLY = ["shortage", "energy_war", "worker_shortage"]
o["demand"] = o[DEMAND].sum(axis=1)
o["covid_jobs"] = o.covid_other - o.memo_energy_covid          # the COVID drag on the labor market (demand side)
o["supply"] = o[SUPPLY].sum(axis=1) + o.memo_energy_covid

# SF Fed (Shapiro), headline PCE y/y: change from the 2019 average to June 2022 (our causes are changes since end-2019)
r0 = "2019 average"
base = sf.loc[[f"2019m{i}" for i in range(1, 13)]].mean(numeric_only=True)
sfd, sfs, sfa = [sf.loc["2022m6", c] - base[c] for c in ["Demand-driven Inflation", "Supply-driven Inflation", "Ambiguous"]]
p = lambda q, k: o.loc[q, k]
bl = fl.loc[("barnichon", "2022Q2")]
b4 = fl.loc[("barnichon", "2024Q4")]
rows = [
    ("Supply vs demand, mid-2022", "SF Fed, Shapiro (EL 2022-15 method, data file): change in headline PCE inflation from "
     f"{r0} to 2022m6: supply-driven {sfs:+.1f}, demand-driven {sfd:+.1f}, ambiguous {sfa:+.1f}",
     f"2022Q2: supply (supply chains + war + worker shortage + 2020-21 energy) {p('2022Q2','supply'):+.1f}; demand (relief + Fed + pent-up) "
     f"{p('2022Q2','demand'):+.1f}; COVID drag on jobs {p('2022Q2','covid_jobs'):+.1f}",
     "Different method (price-quantity signs by category). Both find supply larger than demand in mid-2022. Our demand is close "
     "to theirs, but here the COVID drag offsets it; their split has no separate COVID term."),
    ("Supply chains, peak", "Liu & Nguyen, FRBSF EL 2023-14: GSCPI shocks' contribution peaked at 2.5 points (headline inflation)",
     f"Peak {o.shortage.max():.1f} ({o.shortage.idxmax()})", "Same index (GSCPI); our estimate is somewhat lower."),
    ("Relief payments, end-2021", "Jordà, Liu, Nechio & Rivera-Reyes, FRBSF EL 2022-07: US transfers added about 3 points by 2021Q4 "
     "(core CPI; 'considerable uncertainty')", f"2021Q4 Trump + Biden relief {p('2021Q4','trump') + p('2021Q4','biden'):.1f} "
     f"[ranges {o.loc['2021Q4','trump_lo']:.1f}-{o.loc['2021Q4','trump_hi']:.1f} and {o.loc['2021Q4','biden_lo']:.1f}-{o.loc['2021Q4','biden_hi']:.1f}]; "
     f"at CBO's full 2020 scale about twice that (output/robustness_unified.csv)",
     "Ours counts relief only through the labor market; theirs is a cross-country comparison. Ours is lower."),
    ("All demand, 2022", "Beckworth & Horan, Mercatus WP 2025 (not peer reviewed): demand 4.40 of 2022 GDP-deflator inflation",
     f"2022Q4 relief + Fed + pent-up {p('2022Q4','demand'):+.1f}", "Ours is much lower. Theirs counts demand's effect on commodity "
     "and sectoral prices too; ours counts only demand through the labor market (see limits)."),
    ("Earlier Fed hikes", "Barnichon, FRBSF EL 2022-28: hikes from March 2021 to ~2% by early 2022 -> core inflation about 1 point lower "
     "by June 2022 (95%: 0.2-2), unemployment about 2 points higher (1-3)",
     f"Same path, 2022Q2: headline PCE {bl.infl_yoy:+.2f} [{bl.infl_lo:+.2f} to {bl.infl_hi:+.2f}], unemployment {bl.unemp:+.2f} "
     f"[{bl.unemp_lo:+.2f} to {bl.unemp_hi:+.2f}]; by 2024Q4 inflation {b4.infl_yoy:+.2f}, unemployment {b4.unemp:+.2f}",
     "Ours is much smaller and slower. Trade-off per point of inflation removed: theirs about 2 points of unemployment, ours "
     f"about {b4.unemp / -b4.infl_yoy:.0f} by 2024. Our model has no channel through Fed credibility or the dollar."),
    ("Markups / greed, 2021", "Glover, Mustre-del-Rio & von Ende-Becker, KC Fed 2023: markups grew 3.4% in 2021, 'could account for more than "
     "half' of 2021 PCE inflation (5.8)", f"Model greed line 2021Q4 {p('2021Q4','greed'):+.2f}; accounting: margin change alone raised "
     f"corporate prices {p('2021Q4','acct_margin_effect_on_corp_prices_yoy'):.1f}% in the year to 2021Q4",
     "Accounting agrees margins rose in 2021; the model finds margin moves beyond costs, shortages and demand don't predict PCE "
     "inflation (1990-2024). The authors themselves point to firms pricing in expected cost increases."),
    ("Supply-side shocks, the surge", "Bernanke & Blanchard (NBER w31417 / AEJ Macro): 'most of the inflation surge that began in "
     "2021 was the result of shocks to prices given wages'", f"2021Q4: supply {p('2021Q4','supply'):+.1f} vs labor-market demand "
     f"{p('2021Q4','demand'):+.1f}", "Same model family, so agreement is expected; it is not independent confirmation."),
]
md = ["# This project vs published estimates", "",
      "Each row compares like with like as closely as the sources allow. The measures differ (headline vs core, PCE vs "
      "CPI, GDP deflator), so a difference under about half a point is not meaningful.", "",
      "| Question | Published estimate | This project | Comment |", "|---|---|---|---|"]
md += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows]
open(ROOT + "output/COMPARISON.md", "w").write("\n".join(md) + "\n")
print("\n".join(md))
