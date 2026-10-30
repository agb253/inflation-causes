"""Simple supply-vs-demand chart from SF Fed's published split of headline PCE inflation.
Source data: data/raw/sf_fed/supply-demand-pce-inflation.xlsx (FRBSF, Shapiro 2022, EL 2022-15).
Units: percentage points of annualized monthly headline PCE inflation, averaged by quarter.
No constants estimated here; the only arithmetic is quarterly means, a 2019 mean baseline, and a running sum / 4."""
import pathlib; ROOT = str(pathlib.Path(__file__).resolve().parent.parent)
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
R = ROOT + "/"
d = pd.read_excel(R+"data/raw/sf_fed/supply-demand-pce-inflation.xlsx", sheet_name="Data")
d["t"] = d.time_month.astype(str).str.strip()
d = d[d.t.str.match(r"20(19|2[0-4])m")].copy()
m = d.t.str.split("m").str[1].astype(int)
d["q"] = d.t.str[:4] + "Q" + ((m-1)//3+1).astype(str)
cols = {"Supply-driven Inflation (headline, m/m)":"Supply-driven","Demand-driven Inflation (headline, m/m)":"Demand-driven","Ambiguous (headline, m/m)":"Ambiguous"}
g = d.groupby("q")[list(cols)].mean().rename(columns=cols)
base = g.loc["2019Q1":"2019Q4"].mean()
g = g.loc["2020Q1":"2024Q4"]
g["Total"] = g.sum(axis=1)
ex = g[list(cols.values())] - base
cum = ex.cumsum()/4
g.round(3).to_csv(R+"output/simple_quarterly_supply_demand.csv"); cum.round(3).to_csv(R+"output/simple_cumulative_excess.csv")
C = {"Supply-driven":"#2a78d6","Demand-driven":"#eb6834","Ambiguous":"#b9b8b0"}
x = np.arange(len(g)); lab = [q[2:4]+" "+q[4:] if q[4:]!="Q1" else q[:4]+"\nQ1" for q in g.index]
fig, ax = plt.subplots(2,1,figsize=(13,11),gridspec_kw={"height_ratios":[1.15,1]})
a = ax[0]; pos = np.zeros(len(g)); neg = np.zeros(len(g))
for k in C:
    v = g[k].values; b = np.where(v>=0,pos,neg)
    a.bar(x,v,bottom=b,color=C[k],width=.8,label=k,edgecolor="white",lw=.6)
    pos += np.where(v>=0,v,0); neg += np.where(v<0,v,0)
a.plot(x,g.Total,color="black",lw=2.2,marker="o",ms=4,label="Total headline PCE inflation")
a.axhline(0,color="#444",lw=.8); a.axhline(base.sum(),color="#444",ls=":",lw=1); a.text(-.45,base.sum()+.2,"2019 average (%.1f)"%base.sum(),ha="left",fontsize=9,color="#444")
iq = list(g.index).index
for q,t in [("2020Q1","COVID lockdowns;\nCARES Act signed 3/27/20"),("2021Q1","American Rescue Plan\nsigned 3/11/21"),("2022Q1","Russia invades Ukraine 2/24/22;\nFed first rate hike 3/16/22")]:
    i = iq(q); a.annotate(t,(i,g.Total.iloc[i]),xytext=(i+.3,10.6 if q!="2022Q1" else 11.4),fontsize=8.5,arrowprops=dict(arrowstyle="-",color="#666"),va="top")
a.axvspan(-.5,3.5,color="#d8504d",alpha=.07,zorder=0); a.axvspan(3.5,len(g)-.5,color="#3a6fd8",alpha=.06,zorder=0)
a.text(1.5,12.4,"Trump administration",ha="center",fontsize=10,color="#a02c2a"); a.text(11.5,12.4,"Biden administration (from Jan 20, 2021)",ha="center",fontsize=10,color="#244f9e")
a.set_ylim(-4.5,13); a.set_xlim(-.5,len(g)-.5); a.set_xticks(x); a.set_xticklabels(lab,fontsize=8)
a.set_ylabel("Percentage points of annualized inflation"); a.set_title("What was pushing prices up each quarter: supply shocks vs demand",loc="left",fontsize=13,fontweight="bold")
a.legend(loc="lower left",ncol=4,fontsize=9,frameon=False,bbox_to_anchor=(0,-.02))
b = ax[1]
for k in C: b.plot(x,cum[k],color=C[k],lw=2.6,label=k)
b.plot(x,cum.sum(axis=1),color="black",lw=2.6,label="Total excess over 2019 pace")
b.axhline(0,color="#444",lw=.8); b.axvspan(-.5,3.5,color="#d8504d",alpha=.07); b.axvspan(3.5,len(g)-.5,color="#3a6fd8",alpha=.06)
for k in list(C)+["Total"]:
    y = cum.sum(axis=1).iloc[-1] if k=="Total" else cum[k].iloc[-1]
    b.text(len(g)-.4,y+{"Demand-driven":.25,"Ambiguous":-.25}.get(k,0),"%.1f"%y,va="center",fontsize=10,fontweight="bold")
b.set_xlim(-.5,len(g)+.3); b.set_xticks(x); b.set_xticklabels(lab,fontsize=8)
b.set_ylabel("Cumulative price level above 2019 pace\n(percent)"); b.set_title("Running total: how much of the price jump each force added beyond 2019's normal pace",loc="left",fontsize=13,fontweight="bold")
b.legend(loc="upper left",fontsize=9,frameon=False)
fig.text(.01,.005,"Data: SF Fed, Shapiro (2022) supply- and demand-driven PCE inflation, headline m/m (frbsf.org/indicators-data/supply-and-demand-driven-pce-inflation/), file SHA-256 52eeefe6…; quarterly mean of monthly annualized contributions.\n"
 "Bottom panel = running sum of (quarter − 2019 mean of that category)/4. 'Ambiguous' = cannot be labeled supply or demand. Shading = party in office, not causation. No error bands: SF Fed does not publish any.",fontsize=7.5,color="#444")
plt.tight_layout(rect=(0,.04,1,1)); fig.savefig(R+"output/fig4_supply_vs_demand_simple.png",dpi=150)
print(g.round(2).to_string()); print(cum.round(2).iloc[[3,7,11,15,19]].to_string()); print("base",base.round(2).to_dict())
print("Trump-era excess (2020):",ex.loc["2020Q1":"2020Q4"].sum().div(4).round(2).to_dict())
print("Biden-era excess (2021-24):",ex.loc["2021Q1":"2024Q4"].sum().div(4).round(2).to_dict())
