
/*
Replication file for the Economic Letter written by Fernanda Nechio, Oscar Jorda, Celeste Liu, Fabian Rivera Reyes


Steps to use the replication folder:
	1. Download the folder
	2. Open the replication_EL_FN_OJ_final.do do file located in the programs folder
	3. Change the local below to the working directory (point towards the replication folder in your drive)
	4. Run the file
*/



* Set Up
clear all
set more off
cap log close
*Specify the working directory below
local working_dir

cd "`working_dir'"

*Builds master dataset. Saves the master dataset as data/master_EL.dta, replace
do programs/do1_master_data_final.do

*Creates figures 1 and 2
do programs/do2_fig1_2_final.do

*Creates figure 3
do programs/do3_fig_3_final.do