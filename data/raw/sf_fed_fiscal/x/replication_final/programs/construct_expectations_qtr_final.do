*This .do file imports the CPI Complete Database and computes inflation expectations
import delimited raw_data/PRICES_CPI_01032022204359187.csv, clear


***************
*Generate a quarterly date variable in Stata
gen quarter = usubstr(time,7,1)
gen year = usubstr(time,1,4)
destring quarter, replace
destring year, replace
gen qdate = yq(year, quarter)
format qdate %tq
rename value cpi

replace v4 = "_core" if v4 == "CPI: All items non-food non-energy"

*Drop unnecessary columns included in the download
drop subject measure v6 frequency v8 v10 unitcode unit powercodecode powercode referenceperiodcode referenceperiod flagcodes flags time location

*Reshapes the data to have the values associated with the category under v4 as a column. Useful when working with multiple variables in the download.
reshape wide cpi, i(country qdate) j(v4) string 


*Create a country identifier
encode country, gen(c1)

*Use the country identifier to set data as panel
xtset c1 qdate

*For variables included in the following for loop, create a %YoY rate
local variables cpi_core 
foreach v in `variables' {
	gen `v'_chngYoY = 100*[ln(`v')-ln(L4.`v')]
}


keep qdate country c1 year quarter cpi_core_*

gen expect_cpi_core_YoY = .
levelsof country, local(countries)

*For loop estimates core inflation for each period using the previous 20 years of inflation data (inclusive) and regressing on the 4th lag of inflation. Regression estimates to be interpreted as expectations and are constructed by country.
*Loop through each country
foreach country of local countries {
	summ qdate if country == "`country'"
	local min_date = r(min)
	summ year if country == "`country'" & cpi_core_chngYoY != . 
	local min_year = r(min)
	summ quarter if country == "`country'" & year == `min_year' & cpi_core_chngYoY != . 
	local min_qtr = r(min)
	local min_yr_20 = `min_year' + 20
	levelsof qdate if qdate >= yq(`min_yr_20', `min_qtr') & country=="`country'", local(dates)
	*Loop through each date with rolling regressions including previous 20 years
	foreach date of local dates	{
		qui summ year if qdate == `date'
		local yr = r(mean)
		local yr_minus20 = `yr' - 20
		qui summ quarter if qdate == `date'
		local qtr = r(mean)
		*Regress core inflation on the 4 lag of core inflation for the time period specified and the country specified
		reg cpi_core_chngYoY L4.cpi_core_chngYoY if country == "`country'" & qdate >= yq(`yr_minus20', `qtr') & qdate <= yq(`yr',`qtr')
		predict expect
		*Switch the predicted value for the date and country in question
		replace expect_cpi_core_YoY = expect if country == "`country'" & qdate == `date'
		drop expect
	}
}

keep if qdate >= yq(1975,01)

save data/cpiqoq_final.dta, replace
