*This .do file imports the Household Dashboard data for the variable: Real Household gross disposable income per capita
*Countries included (2007-2021, quarterly): Norway, United Kingdom, Germany, Denmark, Sweden, Netherlands, France, United States, Finland, and Canada

import delimited raw_data/HH_DASH_01032022203306653.csv, clear

*Verify the variables included in the downloaded data
levelsof v4, local(vars)

*Create a time variable in Stata, quarterly
gen year = usubstr(time, 1, 4)
gen quarter = usubstr(time, -1, 2)
gen time2 = year+"q"+quarter
destring year, replace
destring quarter, replace
gen qdate = yq(year, quarter)
format qdate %tq
rename value RDIPC

keep country qdate RDIPC

save data/RDIPC.dta, replace
