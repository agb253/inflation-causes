"""Pull US import charges (freight + insurance to the US port) from the Census
international trade API, monthly 2018-2024.

GEN_CHA_MO = general imports charges, GEN_VAL_MO = general imports customs value.
Total = sum over HS2 chapters (COMM_LVL=HS2), which covers every import.
Key is read from ~/.config/census.env (CENSUS_API_KEY=...).
Writes data/raw/census/import_charges_monthly.csv.
"""
import json
import os
import pathlib
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data/raw/census/import_charges_monthly.csv"
URL = "https://api.census.gov/data/timeseries/intltrade/imports/hs"


def key():
    for line in open(os.path.expanduser("~/.config/census.env")):
        if line.startswith("CENSUS_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no CENSUS_API_KEY in ~/.config/census.env")


def get(year, k):
    q = (f"{URL}?get=GEN_VAL_MO,GEN_CHA_MO,I_COMMODITY&COMM_LVL=HS2"
         f"&time=from+{year}-01+to+{year}-12&key={k}")
    for attempt in range(4):
        try:
            with urllib.request.urlopen(q, timeout=180) as r:
                if "invalid_key" in r.geturl():
                    raise SystemExit("Census rejected the key")
                return json.load(r)
        except (OSError, json.JSONDecodeError) as e:
            print(f"  {year} attempt {attempt + 1} failed: {e}")
            time.sleep(10)
    raise SystemExit(f"could not fetch {year}")


def main():
    k = key()
    totals = {}
    for year in range(2018, 2025):
        rows = get(year, k)
        h = rows[0]
        iv, ic, it = h.index("GEN_VAL_MO"), h.index("GEN_CHA_MO"), h.index("time")
        n = 0
        for r in rows[1:]:
            t = totals.setdefault(r[it], [0, 0, 0])
            t[0] += int(r[iv])
            t[1] += int(r[ic])
            t[2] += 1
            n += 1
        print(f"{year}: {n} chapter-month rows")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        f.write("month,customs_value_usd,charges_usd,hs2_chapters\n")
        for m in sorted(totals):
            v, c, n = totals[m]
            f.write(f"{m},{v},{c},{n}\n")
    print(f"wrote {OUT} ({len(totals)} months)")


if __name__ == "__main__":
    main()
