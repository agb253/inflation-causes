*This .do file builds the master_dataset
*imports the Household Dashboard data and creates a .dta dataset with Gross Real Disposable Income per capita index per country
do programs/import_hh_final.do

*imports the CPI database and creates the inflation expectations measures for QoQ and YoY; saves the result in data/cpiqoq.dta
do programs/construct_expectations_qtr_final.do

use data/cpiqoq_final.dta, clear

*Merge the Household Dashboard Data
merge 1:1 country qdate using data/RDIPC.dta

*RDIPC4 is an index, normalized to 2007Q1 disp income

**Change the base year
*1. determine new base
local base_yr = yq(2019,04)
*Identify countries in sample and store them in a local
gen country2 = subinstr(country, " ", "", 2)
levelsof country2, local(countries)

*Loop through each country, dividing the values for that country by that country's  chosen base value (as identified above)
local num_countries: word count `countries'
forval i = 1/`num_countries' {
	local c: word `i' of `countries'
	summ RDIPC if qdate == `base_yr' & country2 == "`c'"
	local base_val = r(mean)
	di "`base_val'"
	replace RDIPC = RDIPC/`base_val' if country2 == "`c'"
}
replace RDIPC = RDIPC* 100

*Recall Household Dashboard data only available 2007Q1 onwards
drop if qdate < yq(2007,01)

*Generate log of Real Household gross income
gen RDI = 100*log(RDIPC)
label var RDI "100*log(RDIPC)"
keep if country == "United States" | country == "Canada" | country == "Denmark" | country == "Finland" | country == "France" | country == "Germany" | country == "Netherlands" | country == "Norway" | country == "Sweden" | country == "United Kingdom"

xtset c1 qdate, quarterly
* Generate trend of log RDI
tsfilter hp gap_RDI = RDI if qdate <= yq(2019,04) & RDI != . , smooth(1600)
*Generate linear trend
reg RDI qdate if qdate <= yq(2019,04) & qdate >= yq(2015,01)
predict linear_trend
*Use linear trend to construct gap from 2020Q1 onwards inclusive
replace gap_RDI = RDI - linear_trend if qdate >= yq(2020,01)

*Generate the start of the pandemic as immediately after 2020Q1
gen pandemic = 0
replace pandemic = 1 if qdate > yq(2020,01) & gap_RDI != .

*Generate treat variable for chosen countries
gen treat = 0
replace treat = 1 if country == "United States" | country == "Canada" | country == "Norway" | country == "Denmark" | country == "Netherlands"
replace treat = 0 if pandemic == 0


gen rolling_avg_rdi = .
*Create a rolling average variable that calculates the average of RDI including the previous 4 periods
levelsof country2, local(countries)
local num_countries: word count `countries'
forval i = 1/`num_countries' {
	local country: word `i' of `countries'
	summ qdate if country2 == "`country'"
	local min_date_aux = r(min)
	local max_date = r(max)
	local min_date = `min_date_aux' + 3
	forval j = `min_date'/`max_date' {
		local min_thresh = `j'-3
		summ gap_RDI if qdate >= `min_thresh' & qdate <= `j' & country2 == "`country'"
		replace rolling_avg_rdi = r(mean) if qdate == `j' & country2 == "`country'" & gap_RDI != .
	}
}

xtset c1 qdate, quarterly

*Generate interaction terms that allow the coefficient to change on the regressors once we enter the pandemic period.
gen treat_pandemic_roll_rdi_1_1 = rolling_avg_rdi*treat*pandemic
* Only includes rolling averages when treat = 1 and pandemic = 1
gen treat_pandemic_roll_exp_1_1_YoY = treat*pandemic*expect_cpi_core_YoY 
* Only includes expectations when treat = 1 and pandemic = 1
gen treat_pandemic_infYoY_lag_1_1 = treat*pandemic*L1.cpi_core_chngYoY

save data/master_EL_final.dta, replace

