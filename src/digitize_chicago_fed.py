"""Digitize Chicago Fed Letter 483 (D'Amico & King 2023) Figure 2 panel F: effect of holding the policy rate at the ELB (2021Q4-2023Q3 counterfactual)
on the CPI inflation rate, annual rate in percent (a negative number = the tightening lowered inflation). The letter publishes no data file, so values are read from the
published PNG (data/raw/chicago_fed/fig2f.png). Axis calibration is detected from tick pixels; precision is about +/-0.1 pp of the axis (1 px = 0.025 pp), but the
chart itself is a median with an interquartile band of the model's estimation uncertainty."""
import pathlib; ROOT = str(pathlib.Path(__file__).resolve().parent.parent)
import numpy as np, pandas as pd
from PIL import Image
im=np.array(Image.open(ROOT + "/data/raw/chicago_fed/fig2f.png").convert("RGB")).astype(int)
S=im.sum(axis=2); H,W=S.shape
Y0,PX=157.5,40.0                      # zero line row; px per percentage point (ticks at -4,-6,-8 = 317.5,397.5,477.5)
X22,PXQ=144.5,171.3/4                 # x tick for 2022 (start of year); px per quarter (ticks 2022..2025 at 144.5,315.5,486.5,658.5)
def xq(y,q): return X22+171.3*(y-2022)+PXQ*(q-1)+PXQ/2
rows=[]
for y,q in [(2021,3)]+[(yy,qq) for yy in (2021,2022,2023,2024,2025) for qq in (1,2,3,4) if (yy,qq)>(2021,3)]:
    x=int(round(xq(y,q)))
    if x>=W-5: break
    win=S[100:513,max(x-2,0):x+3]                      # plot area only (excludes title text and axis labels), +/-2 px window
    blk=[100+r for r in range(win.shape[0]) if (win[r]<150).any() and not (55<=r<=61)]   # black pixels except zero-line rows 155-161
    line_rows=blk or [157.5]
    g=[100+r for r in range(win.shape[0]) if ((win[r]<700)&(win[r]>=150)).any() and not (153<=100+r<=162)]   # drop zero-line antialias rows
    lo,hi=(min(g),max(g)) if g else (np.nan,np.nan)
    f=lambda r:(Y0-r)/PX
    rows.append(dict(q=f"{y}Q{q}",x=x,median=round(f(np.mean(line_rows)),2),band_hi=round(f(lo),2),band_lo=round(f(hi),2)))
df=pd.DataFrame(rows); print(df.to_string(index=False))
df.to_csv(ROOT + "/output/fed_policy_effect_digitized.csv",index=False)
sub=df[(df.q>="2021Q4")&(df.q<="2023Q3")]; print("cum level effect through 2023Q3 (sum/4 from 2021Q4):",round(sub["median"].sum()/4,2),"(letter text: -7.1)")
