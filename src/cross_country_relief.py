"""Cross-country estimate of what US pandemic relief did to inflation: an outside check on the relief lines, from data
the model never uses (how much other countries spent).

excess_i = sum of annual inflation 2021-2024 - 4 x average annual inflation 2015-2019     (country i)
excess_i = a + b x F_i + e_i,   OLS, heteroskedasticity-robust (HC1) standard errors
F_i = above-the-line pandemic fiscal measures (additional spending + forgone revenue), % of GDP, IMF Fiscal Monitor
      database of country fiscal measures, October 2021, 'Summary Table' (data/raw/imf_fiscal/)
US relief effect = b x F_US (relief vs none, the same question the relief lines answer), in the units of the
dependent variable (CPI, annual averages).

Inflation: core = OECD CPI all items less food and energy (data/raw/oecd/cpi_annual.csv; OECD has no Japan data after
2020); headline = IMF World Economic Outlook, PCPIPCH (data/raw/imf_weo/pcpipch.json).
Writes output/cross_country_relief.csv (one row per specification) and output/cross_country_data.csv.
"""
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
ISO = {"Australia": "AUS", "Canada": "CAN", "France": "FRA", "Germany": "DEU", "Italy": "ITA", "Japan": "JPN",
       "Korea": "KOR", "Spain": "ESP", "United Kingdom": "GBR", "United States": "USA", "Belgium": "BEL",
       "Czech republic": "CZE", "Denmark": "DNK", "Finland": "FIN", "The Netherlands": "NLD", "New Zealand": "NZL",
       "Norway": "NOR", "Singapore": "SGP", "Sweden": "SWE", "Switzerland": "CHE",
       "Poland": "POL", "Chile": "CHL", "Colombia": "COL", "Mexico": "MEX"}
ADVANCED = ["AUS", "CAN", "FRA", "DEU", "ITA", "JPN", "KOR", "ESP", "GBR", "USA", "BEL", "CZE", "DNK", "FIN", "NLD",
            "NZL", "NOR", "SGP", "SWE", "CHE"]     # the IMF table's two advanced-economy groups
EURO = ["FRA", "DEU", "ITA", "ESP", "BEL", "FIN", "NLD"]


def fiscal():
    d = pd.read_excel(ROOT + "data/raw/imf_fiscal/oct-2021-country-fiscal-measures-database.xlsx", "Summary Table",
                      header=None).dropna(how="all").dropna(axis=1, how="all")
    hdr = [str(v) for v in d.iloc[3].tolist()]
    assert hdr[10] == "Above the line measures" and str(d.iloc[5, 10]) == "Subtotal" and str(d.iloc[2, 9]).startswith("Percent")
    s = d.iloc[6:, [0, 10]].dropna()
    s = s[s.iloc[:, 0].isin(ISO)]
    return pd.Series(s.iloc[:, 1].astype(float).values, index=s.iloc[:, 0].map(ISO), name="fiscal_pct_gdp")


def inflation():
    o = pd.read_csv(ROOT + "data/raw/oecd/cpi_annual.csv")
    core = o[o.EXPENDITURE == "_TXCP01_NRG"].pivot_table(index="REF_AREA", columns="TIME_PERIOD", values="OBS_VALUE")
    w = json.load(open(ROOT + "data/raw/imf_weo/pcpipch.json"))["values"]["PCPIPCH"]
    head = pd.DataFrame({c: {int(y): v for y, v in w[c].items()} for c in ISO.values() if c in w}).T
    return core, head


def excess(p, years=range(2021, 2025)):
    base = p[list(range(2015, 2020))].mean(axis=1)
    return (p[list(years)].sum(axis=1, min_count=len(years)) - len(years) * base)


SPECS = [  # name, inflation, countries, years, extra regressors
    ("core_advanced", "core", ADVANCED, range(2021, 2025), []),
    ("core_advanced_euro_dummy", "core", ADVANCED, range(2021, 2025), ["euro"]),
    ("core_advanced_2021_22", "core", ADVANCED, range(2021, 2023), []),
    ("core_advanced_2021_22_euro_dummy", "core", ADVANCED, range(2021, 2023), ["euro"]),
    ("core_advanced_2021_22_energy_control", "core", ADVANCED, range(2021, 2023), ["energy"]),
    ("core_plus_oecd_emerging_2021_22", "core", ADVANCED + ["POL", "CHL", "COL", "MEX"], range(2021, 2023), []),
    ("headline_advanced_incl_japan_2021_22", "headline", ADVANCED, range(2021, 2023), []),
    ("core_plus_oecd_emerging", "core", ADVANCED + ["POL", "CHL", "COL", "MEX"], range(2021, 2025), []),
    ("headline_advanced_incl_japan", "headline", ADVANCED, range(2021, 2025), []),
    ("headline_advanced_euro_dummy", "headline", ADVANCED, range(2021, 2025), ["euro"]),
]


def run():
    F = fiscal()
    core, head = inflation()
    data = pd.DataFrame({"fiscal_pct_gdp": F, "excess_core_2021_24": excess(core), "excess_headline_2021_24": excess(head)})
    rows = []
    for name, kind, ctry, yrs, extra in SPECS:
        y = excess(core if kind == "core" else head, yrs).reindex(ctry)
        X = pd.DataFrame({"fiscal": F.reindex(ctry)})
        if "energy" in extra:   # energy exposure: headline minus core inflation, 2022 (OECD)
            hd = pd.read_csv(ROOT + "data/raw/oecd/cpi_annual.csv").pivot_table(index="REF_AREA", columns=["EXPENDITURE", "TIME_PERIOD"], values="OBS_VALUE")
            X["energy"] = (hd[("_T", 2022)] - hd[("_TXCP01_NRG", 2022)]).reindex(ctry)
        if "euro" in extra:
            X["euro"] = X.index.isin(EURO).astype(float)
        ok = y.notna() & X.notna().all(axis=1)
        r = sm.OLS(y[ok], sm.add_constant(X[ok])).fit(cov_type="HC1")
        us = F["USA"]
        rows.append(dict(spec=name, inflation=kind, years=f"{yrs[0]}-{yrs[-1]}", n=int(ok.sum()),
                         countries=" ".join(y[ok].index), b=r.params.fiscal, se=r.bse.fiscal, r2=r.rsquared,
                         us_fiscal=us, us_effect=r.params.fiscal * us, us_effect_se=r.bse.fiscal * us,
                         us_actual_excess=y.get("USA", np.nan), us_resid=r.resid.get("USA", np.nan)))
    out = pd.DataFrame(rows).set_index("spec")
    out.round(4).to_csv(ROOT + "output/cross_country_relief.csv")
    data.round(3).to_csv(ROOT + "output/cross_country_data.csv")
    return out, data


if __name__ == "__main__":
    out, data = run()
    pd.set_option("display.width", 250)
    print(data.dropna(subset=["fiscal_pct_gdp"]).round(2).to_string())
    print(out.drop(columns="countries").round(3).to_string())
