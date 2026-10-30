*This file is runs the panel regression using a DiD approach towards RDI expansion and creates fig 3 in the EL.


preserve
gen b=0
gen u=0
gen d=0
gen h = .

*Estimates and stores the associated effect captured by the coefficient for the variable: treat_pandemic_roll_rdi_1_1
forval h = 0/3 {
	xtreg f`h'.cpi_core_chngYoY i.qdate expect_cpi_core_YoY rolling_avg_rdi L1.cpi_core_chngYoY treat_pandemic_infYoY_lag_1_1 treat_pandemic_roll_exp_1_1_YoY treat_pandemic_roll_rdi_1_1, fe vce(cluster country)
	local c`h'=_b[treat_pandemic_roll_rdi_1_1]
	local u_`h' = 1.645* _se[treat_pandemic_roll_rdi_1_1]
	local l_`h' = -1* 1.645* _se[treat_pandemic_roll_rdi_1_1]
}

*Print the coefficients with standard errors
forval h = 0/3 {
	di "`c`h''; `se_`h''"
}
restore

keep if country == "United States"
keep if qdate >  yq(2017,4)

*Let the associated effect with real disposable income be zero if the value is missing
replace rolling_avg_rdi = 0 if rolling_avg_rdi == .

*Set the date as quarterly in Stata (notice there is no longer a panel data set because we only kept US data)
tsset qdate, quarterly

*Calculate the associated cumulative effect below
gen sum_effect = 0
gen error_upper = 0
gen error_lower = 0
replace sum_effect = `c0'*rolling_avg_rdi + `c1'*L1.rolling_avg_rdi + `c2'*L2.rolling_avg_rdi  + `c3'*L3.rolling_avg_rdi   
replace error_upper = `u_0'*rolling_avg_rdi + `u_1'*L1.rolling_avg_rdi + `u_2'*L2.rolling_avg_rdi + `u_3'*L3.rolling_avg_rdi
replace error_lower = `l_0'*rolling_avg_rdi + `l_1'*L1.rolling_avg_rdi + `l_2'*L2.rolling_avg_rdi + `l_3'*L3.rolling_avg_rdi

*Ensure that we only graph the effects in the appropriate time period
replace sum_effect = . if qdate < yq(2020,1)

*Calculate the counterfactural by subtracting the effect associated with RDI from the observed core inflation in the US
gen difference = cpi_core_chngYoY-sum_effect

*Include the error bands
gen upper_bound_counter = difference-error_upper
gen lower_bound_counter = difference-error_lower

*Graph the counterfactual with the error bands
twoway (line cpi_core_chngYoY qdate, sort) (line difference qdate, sort lpattern(dash)) (rarea upper_bound_counter lower_bound_counter qdate, sort lpattern(dash) acolor(red%30)), xline(240, lcolor(grey) lpattern(dot)) graphregion(color(white)) plotregion(color(white))  name(fig3, replace) 

gr export final_figs/fig3.pdf, as(pdf) replace







