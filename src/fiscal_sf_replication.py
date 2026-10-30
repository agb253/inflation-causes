"""Python port of the SF Fed fiscal local-projection (Jorda-Liu-Nechio-Rivera-Reyes, FRBSF EL 2022-07).
Mirrors programs/do3_fig_3_final.do from the authors' replication zip (data/raw/sf_fed_fiscal/). Point estimates should match Stata's xtreg, fe;
standard errors use statsmodels cluster-robust with the usual small-sample correction (Stata's differs slightly)."""
import pathlib; ROOT = str(pathlib.Path(__file__).resolve().parent.parent)
import pandas as pd, numpy as np, statsmodels.formula.api as smf
R=ROOT + "/data/raw/sf_fed_fiscal/x/replication_final/"
def load():
    d=pd.read_stata(R+"data/master_EL_final.dta")
    d=d.sort_values(["country","qdate"]).reset_index(drop=True)
    d["q"]=d.qdate.dt.year.astype(str)+"Q"+d.qdate.dt.quarter.astype(str)
    return d
def coefs(d):
    d=d.copy(); g=d.groupby("country")
    d["L1infl"]=g.cpi_core_chngYoY.shift(1)
    d["treat_pandemic_infYoY_lag_1_1"]=d.treat*d.pandemic*d.L1infl   # as in do1: treat*pandemic*L1.inflation
    out={}
    for h in range(4):
        d["y"]=g.cpi_core_chngYoY.shift(-h)
        m=d.dropna(subset=["y","expect_cpi_core_YoY","rolling_avg_rdi","L1infl"]).copy()
        f="y ~ C(country)+C(q)+expect_cpi_core_YoY+rolling_avg_rdi+L1infl+treat_pandemic_infYoY_lag_1_1+treat_pandemic_roll_exp_1_1_YoY+treat_pandemic_roll_rdi_1_1"
        r=smf.ols(f,data=m).fit(cov_type="cluster",cov_kwds={"groups":pd.factorize(m.country)[0]})
        out[h]=(r.params["treat_pandemic_roll_rdi_1_1"],r.bse["treat_pandemic_roll_rdi_1_1"],int(r.nobs))
    return out
def effect(us,c,rdi_col="rolling_avg_rdi"):
    """sum_effect_t = sum_h c_h * rolling_avg_rdi_{t-h};  90% band = 1.645*se (as the authors' do-file)."""
    x=us[rdi_col].fillna(0).values; n=len(x); e=np.full(n,np.nan); u=np.full(n,np.nan)
    for t in range(3,n):
        e[t]=sum(c[h][0]*x[t-h] for h in range(4)); u[t]=sum(1.645*c[h][1]*x[t-h] for h in range(4))
    return e,u
if __name__=="__main__":
    d=load(); c=coefs(d); print({h:(round(v[0],4),round(v[1],4),v[2]) for h,v in c.items()})
    us=d[d.country=="United States"].reset_index(drop=True); e,u=effect(us,c)
    us["effect"]=e; us["band"]=u
    print(us[us.qdate>="2020-01-01"][["q","cpi_core_chngYoY","effect","band"]].round(2).to_string())
