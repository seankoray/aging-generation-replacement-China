****************************************************
* APC Decomposition: Age-Period-Cohort Effects on TFP
****************************************************

clear all
set more off

*---------------------------------------------------
* 0) Load data (EDIT PATH as needed)
*---------------------------------------------------
use "./data/main_panel.dta", clear
keep if sow == 1

* Use agricultural labor age
replace age = age_agrilabor
replace age = round(age)

* Birth cohort = year - age
gen cohort = year - age

*---------------------------------------------------
* 1) Age groups
*---------------------------------------------------
gen age_group1 = .
replace age_group1 = 0  if age >= 16 & age <= 25
replace age_group1 = 1  if age >= 26 & age <= 30
replace age_group1 = 2  if age >= 31 & age <= 35
replace age_group1 = 3  if age >= 36 & age <= 40
replace age_group1 = 4  if age >= 41 & age <= 45
replace age_group1 = 5  if age >= 46 & age <= 50
replace age_group1 = 6  if age >= 51 & age <= 55
replace age_group1 = 7  if age >= 56 & age <= 60
replace age_group1 = 8  if age >= 61 & age <= 65
replace age_group1 = 9  if age >= 66 & age <= 70
replace age_group1 = 10 if age >= 71 & age <= 75
replace age_group1 = 11 if age >= 76 & age <= 80
replace age_group1 = 12 if age >= 81 & age <= 90

label define age_group1_lbl ///
    0 "16-25" 1 "26-30" 2 "31-35" 3 "36-40" 4 "41-45" ///
    5 "46-50" 6 "51-55" 7 "56-60" 8 "61-65" 9 "66-70" ///
    10 "71-75" 11 "76-80" 12 "81-90"
label values age_group1 age_group1_lbl

*---------------------------------------------------
* 2) Cohort groups
*---------------------------------------------------
gen cohort_group = .
replace cohort_group = 0  if cohort >= 1920 & cohort <= 1929
replace cohort_group = 1  if cohort >= 1930 & cohort <= 1934
replace cohort_group = 2  if cohort >= 1935 & cohort <= 1939
replace cohort_group = 3  if cohort >= 1940 & cohort <= 1944
replace cohort_group = 4  if cohort >= 1945 & cohort <= 1949
replace cohort_group = 5  if cohort >= 1950 & cohort <= 1954
replace cohort_group = 6  if cohort >= 1955 & cohort <= 1959
replace cohort_group = 7  if cohort >= 1960 & cohort <= 1964
replace cohort_group = 8  if cohort >= 1965 & cohort <= 1969
replace cohort_group = 9  if cohort >= 1970 & cohort <= 1974
replace cohort_group = 10 if cohort >= 1975 & cohort <= 1979
replace cohort_group = 11 if cohort >= 1980 & cohort <= 1984
replace cohort_group = 12 if cohort >= 1985 & cohort <= 1999

label define cohort_group_lbl ///
    0 "1920-1929" 1 "1930-1934" 2 "1935-1939" 3 "1940-1944" ///
    4 "1945-1949" 5 "1950-1954" 6 "1955-1959" 7 "1960-1964" ///
    8 "1965-1969" 9 "1970-1974" 10 "1975-1979" 11 "1980-1984" ///
    12 "1985-1999"
label values cohort_group cohort_group_lbl

*---------------------------------------------------
* 3) APC regression with village FE
*     Base groups: age 16-25, cohort 1920-1929, year 2003
*---------------------------------------------------
reghdfe lntfp ///
    ib0.age_group1 ib0.cohort_group ib2003.year ///
    count_famsize edu_agrilabor internet sow_food inc_govern, ///
    absorb(vid) vce(cluster vid) keepsingletons

predict double xb, xb

*---------------------------------------------------
* 4) Margins plots
*---------------------------------------------------

* Age curve
margins age_group1, atmeans predict(xb) level(95)

marginsplot, ///
    recast(line) ///
    recastci(rline) ///
    plotopts(lwidth(thick)) ///
    ciopts(lcolor(navy) lpattern(dash) lwidth(medthin)) ///
    graphregion(color(white)) ///
    plotregion(color(white)) ///
    ylabel(, nogrid angle(0)) ///
    xlabel(, valuelabel angle(45) nogrid) ///
    legend(off) ///
    title("", size(medsmall)) ///
    xtitle("Age group") ///
    ytitle("ln(TFP)") ///
    name(g_age, replace)

* Cohort curve
margins cohort_group, atmeans predict(xb) level(95)

marginsplot, ///
    recast(line) ///
    recastci(rline) ///
    plotopts(lwidth(thick)) ///
    ciopts(lcolor(navy) lpattern(dash) lwidth(medthin)) ///
    graphregion(color(white)) ///
    plotregion(color(white)) ///
    ylabel(, nogrid angle(0)) ///
    xlabel(, valuelabel angle(45) nogrid) ///
    legend(off) ///
    title("", size(medsmall)) ///
    xtitle("Cohort group") ///
    ytitle("ln(TFP)") ///
    name(g_cohort, replace)

* Year/period curve
margins year, atmeans predict(xb) level(95)

marginsplot, ///
    recast(line) ///
    recastci(rline) ///
    plotopts(lwidth(thick)) ///
    ciopts(lcolor(navy) lpattern(dash) lwidth(medthin)) ///
    graphregion(color(white)) ///
    plotregion(color(white)) ///
    ylabel(, nogrid angle(0)) ///
    xlabel(, valuelabel angle(45) nogrid) ///
    legend(off) ///
    title("", size(medsmall)) ///
    xtitle("Year") ///
    ytitle("ln(TFP)") ///
    name(g_year, replace)

*---------------------------------------------------
* 5) Combine and export
*---------------------------------------------------
graph combine g_age g_cohort g_year, ///
    col(1) ///
    ysize(20) xsize(12) ///
    imargin(small) ///
    ycommon ///
    graphregion(color(white)) ///
    name(g_apc_baseline, replace)

graph export "./output/Figure2_APC_TFP_decomposition.pdf", as(pdf) replace
graph export "./output/Figure2_APC_TFP_decomposition.png", width(2400) replace
