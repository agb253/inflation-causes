"""One bar per published estimate, grouped by the user's causes. Numbers are copied from the cited sources (see output/CAUSES_SOURCES.md);
B&B rows are this project's own decomposition (output/decomp_point.csv). Nothing is summed across studies: they use different measures."""
import pathlib; ROOT = str(pathlib.Path(__file__).resolve().parent.parent)
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, pandas as pd
R=ROOT + "/"
d=pd.read_csv(R+"output/decomp_point.csv",index_col=0); d.index=pd.to_datetime(d.index)
yr=lambda y,c: d[d.index.year==y][c].mean()
ef=lambda y: yr(y,"energy")+yr(y,"food")
S,D,M,G="#2a78d6","#eb6834","#1baf7a","#7d7c75"
rows=[ # (group, label, value, color, note)
("Fiscal stimulus","SF Fed (Jordà et al. 2022): US transfers, core CPI, by 2021Q4",3.0,D,"'considerable uncertainty'"),
("Demand policy overall\n(fiscal + Fed together)","Mercatus (Beckworth & Horan 2025): demand shock, 2021, GDP deflator",1.61,D,""),
("","same, 2022",4.40,D,"60%+ / 85%+ of excess inflation"),
("Supply chains","SF Fed (Liu & Nguyen 2023): supply-chain shocks at mid-2022 peak, PCE",2.5,S,"~60% of above-trend run-up"),
("","This project, B&B 'shortages', 2021, CPI",yr(2021,"shortages"),S,""),
("","This project, B&B 'shortages', 2022, CPI",yr(2022,"shortages"),S,""),
("","Mercatus: all supply shocks, 2021 / 2022, GDP deflator",0.98,S,"2022 = 0.64"),
("Ukraine war / energy / food","This project, B&B energy + food, 2021, CPI",ef(2021),S,"mostly pre-invasion"),
("","This project, B&B energy + food, 2022, CPI",ef(2022),S,"invasion 2/24/22 not separable"),
("International pressures","SF Fed (Bell et al. 2024): international factor, 2021Q1–2022Q4",2.0,G,"1–2 pp max, per authors"),
("Greedflation (markups)","KC Fed (Glover et al. 2023): markup growth 2021 vs PCE inflation of 5.8 (authors' rough comparison)",3.4,M,"'more than half'; fell in 2022"),
]
fig,ax=plt.subplots(figsize=(14,9.5)); y=0; ticks=[]; labs=[]; gy=[]
for g,l,v,c,n in rows[::-1]:
    ax.barh(y,v,color=c,height=.65); ax.text(v+.05,y,"%.1f"%v+("  "+n if n else ""),va="center",fontsize=8.5)
    ticks.append(y); labs.append(l); 
    if g: gy.append((y,g))
    y+=1
ax.set_yticks(ticks); ax.set_yticklabels(labs,fontsize=8.5); ax.set_xlim(0,10.8)
for yy,g in gy: ax.text(10.75,yy,g,ha="right",va="center",fontsize=10.5,fontweight="bold",color="#222",bbox=dict(fc="white",ec="none",alpha=.85))
for yy in [t-.5 for t,_ in gy]: ax.axhline(yy,color="#ccc",lw=.8)
ax.set_xlabel("Percentage points of US inflation (window and price index differ by row; rows are NOT additive)")
fig.suptitle("What published studies say each cause added to the 2021–22 US inflation surge",x=.01,ha="left",fontsize=14,fontweight="bold")
fig.text(.01,.01,"NOT FOUND (no ex-post percentage-point estimate located): Fed policy alone · pent-up demand / excess savings alone · Ukraine war alone · Trump-era vs Biden-era policy.\n"
 "Studies disagree on the big split: SF Fed (Shapiro 2022) and B&B find supply the larger part; Mercatus (not peer reviewed) finds demand 60%+ of 2021 and 85%+ of 2022 excess inflation.\n"
 "Sources and exact quotes: output/CAUSES_SOURCES.md",fontsize=8.5,color="#333",va="bottom")
plt.tight_layout(rect=(0,.07,1,.96)); fig.savefig(R+"output/fig5_causes_by_study.png",dpi=150)
print([(l[:30],round(v,2)) for _,l,v,_,_ in rows])
