Read Me for Replication File
EL by Oscar Jorda, Celeste Liu, Fernanda Nechio, and Fabian Rivera Reyes

The replication file consists of 4 folders:
	1. raw_data
	2. data
	3. final_figs
	4. programs (written as Stata .do files)

This replication file is self contained. All of the data required to produce
the figures on the EL are included in the raw_data folder. Feel free to delete
all elements already in the data and final_figs folders. These elements are
replaced every time the programs are run. Below a quick description of each
program's functionality.

Programs:
	1. replication_EL_FN_OJ_final.do
		-> This program calls all other programs in the appropriate
		order to produce the figures in the EL. In order to run the
		replication folder succesfully change the value of the local 
		"working_dir" to the working directory where the replication
		file is located. This program should run in its entirety
		aftwerwards.
	2. do1_master_data_final.do
		-> This program calls the programs that import raw_data and clean
		it (which output the cleaned data to the folder called data). This
		program also calls in the program to construct the expectations
		measure based on Hamilton et al. (2016). In addition, the gap
		measure and interaction terms are calculated here as well. No more data
		cleaning/ transformation is done after this point.
	3. import_hh_final.do
		-> This program imports the downloaded data from the OECD Household
		Dashboard and saves it as a stata data file.
	4. construct_expectations_qtr_final.do
		-> This program imports the CPI core inflation indexes for the 
		countries specified, creates the rates %YoY, and then constructs
		the expectations using 20 year rolling regressions on the 4th lag
		of core inflation.	
	5. do2_fig1_2_final.do
		-> This program creates figures 1 and 2 included in the EL.
	6. do3_fig3_final.do
		-> This program runs consecutive regressions, advancing the period at
		which the dependent variable is being estimated. In other words,
		the first regression estimates core inflation in the same period
		as its regressors (with the exception of the lagged regressors). The
		second regression then estimates the regressand as the next quarter of
		core inflation while the regressors remain the same. This follows an
		estimation of local projections. Coefficients and error bands are stored
		for the treatment variable. Then, we create figure 3 in the EL.



	


	


