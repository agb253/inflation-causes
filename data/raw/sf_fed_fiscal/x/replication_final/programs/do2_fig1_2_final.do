/*
This .do file creates both figures 2 and 3

*/

*Ensure that Stata understands the data as a panel data set where c1 is the country id and qdate is the quarterly date variable
xtset c1 qdate, quarterly


preserve
*Generate a variable that is 0 for the US and 1 otherwise (this includes all other countries)
gen division = 0 
replace division = 1 if country != "United States"
label def div_label 0 "United States" 1 "OECD peers"
label val division div_label
*Collapse the data based on the new variable we have created. Generate the following variables for the distributions: median (or percentile 50), 75th percentile, and 25th percentile. Notice that these values will only be different when division == 1.
collapse (p50) cpi_core_chngYoY (p75) cpi_core_chngYoY_p75=cpi_core_chngYoY (p25) cpi_core_chngYoY_p25=cpi_core_chngYoY, by(division qdate)

*Core inflation - Graph the IQR with the median for the OECD and the US values
twoway (line cpi_core_chngYoY qdate if division == 0 & qdate >= yq(2019,01), sort) (line cpi_core_chngYoY qdate if division == 1 & qdate >= yq(2019,01), sort) (rarea cpi_core_chngYoY_p75 cpi_core_chngYoY_p25 qdate if division == 1 & qdate >= yq(2019,01), color(grey%30) sort), title("Core inflation (%yoy)") xtitle("") legend(order(1 "United States" 2 "OECD")) name(fig1, replace)
*Export the graph to the final_figs folder
gr export final_figs/fig1.pdf, as(pdf) replace

restore


*Repeat the steps above for the real disposable income variable
preserve
gen division = 0 
replace division = 1 if country != "United States"
label def div_label 0 "United States" 1 "OECD peers"
label val division div_label
collapse (p50) RDIPC (p75) RDIPC_p75=RDIPC (p25) RDIPC_p25=RDIPC, by(division qdate)

twoway (line RDIPC qdate if division == 0 & qdate >= yq(2019,01), sort) (line RDIPC qdate if division == 1 & qdate >= yq(2019,01), sort) (rarea RDIPC_p75 RDIPC_p25 qdate if division == 1 & qdate >= yq(2019,01),color(grey%30) sort), title("Real disposible income per capita (2019Q4=100)") legend(order(1 "United States" 2 "OECD")) name(fig2, replace)
gr export final_figs/fig2.pdf, as(pdf) replace

restore

