****************************************************
* Mechanism 1: Non-Grain Income Share (APC Decomposition)
****************************************************

clear all
set more off

*---------------------------------------------------
* 0) Load data (EDIT PATH as needed)
*---------------------------------------------------
use "./data/main_panel.dta", clear

*---------------------------------------------------
* 1) Income deflation and share construction
*---------------------------------------------------
local inc_vars inc_total inc_mana inc_food inc_cash inc_wage_l inc_wage_o inc_govern

foreach v of local inc_vars {
    replace `v' = (`v' / price) * 100 if !missing(`v') & !missing(price)
}

drop if missing(inc_total) | inc_total == 0
drop if missing(inc_food)  | inc_food > inc_total

gen double inc_food_share    = inc_food / inc_total
gen double inc_nonfood_share = 1 - inc_food_share

label var inc_food_share    "Food income share"
label var inc_nonfood_share "Non-food income share"

*---------------------------------------------------
* 2) Non-agricultural labor share
*---------------------------------------------------
drop if missing(count_labor) | count_labor == 0
drop if missing(count_agrilabor) | count_agrilabor > count_labor

gen double share_nonagrilabor = 1 - (count_agrilabor / count_labor)
label var share_nonagrilabor "Share of non-agricultural labor"

*---------------------------------------------------
* 3) Age and cohort definitions
*---------------------------------------------------
replace age = age_agrilabor
replace age = round(age)

gen cohort = year - age
label var cohort "Birth cohort (year - age)"

* Age groups
gen byte age_group1 = .
replace age_group1 = 0  if inrange(age,16,25)
replace age_group1 = 1  if inrange(age,26,30)
replace age_group1 = 2  if inrange(age,31,35)
replace age_group1 = 3  if inrange(age,36,40)
replace age_group1 = 4  if inrange(age,41,45)
replace age_group1 = 5  if inrange(age,46,50)
replace age_group1 = 6  if inrange(age,51,55)
replace age_group1 = 7  if inrange(age,56,60)
replace age_group1 = 8  if inrange(age,61,65)
replace age_group1 = 9  if inrange(age,66,70)
replace age_group1 = 10 if inrange(age,71,75)
replace age_group1 = 11 if inrange(age,76,80)
replace age_group1 = 12 if inrange(age,81,90)

label define age_group1_lbl ///
    0 "16-25" 1 "26-30" 2 "31-35" 3 "36-40" 4 "41-45" ///
    5 "46-50" 6 "51-55" 7 "56-60" 8 "61-65" 9 "66-70" ///
    10 "71-75" 11 "76-80" 12 "81-90"
label values age_group1 age_group1_lbl

* Cohort groups
gen byte cohort_group = .
replace cohort_group = 0  if inrange(cohort,1920,1929)
replace cohort_group = 1  if inrange(cohort,1930,1934)
replace cohort_group = 2  if inrange(cohort,1935,1939)
replace cohort_group = 3  if inrange(cohort,1940,1944)
replace cohort_group = 4  if inrange(cohort,1945,1949)
replace cohort_group = 5  if inrange(cohort,1950,1954)
replace cohort_group = 6  if inrange(cohort,1955,1959)
replace cohort_group = 7  if inrange(cohort,1960,1964)
replace cohort_group = 8  if inrange(cohort,1965,1969)
replace cohort_group = 9  if inrange(cohort,1970,1974)
replace cohort_group = 10 if inrange(cohort,1975,1979)
replace cohort_group = 11 if inrange(cohort,1980,1984)
replace cohort_group = 12 if inrange(cohort,1985,1999)

label define cohort_group_lbl ///
    0 "1920-1929" 1 "1930-1934" 2 "1935-1939" 3 "1940-1944" ///
    4 "1945-1949" 5 "1950-1954" 6 "1955-1959" 7 "1960-1964" ///
    8 "1965-1969" 9 "1970-1974" 10 "1975-1979" 11 "1980-1984" ///
    12 "1985-1999"
label values cohort_group cohort_group_lbl

*---------------------------------------------------
* 4) APC regression
*     Base groups: age 16-25, cohort 1920-1929, year 2003
*---------------------------------------------------
reghdfe inc_nonfood_share ///
    ib0.age_group1 ib0.cohort_group ib2003.year ///
    count_famsize edu_agrilabor internet sow_food inc_govern, ///
    absorb(vid) vce(cluster vid) keepsingletons

predict double xb, xb

*---------------------------------------------------
* 5) Margins plots
*---------------------------------------------------

* Age effect
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
    ytitle("Non-grain Income(%)") ///
    name(g_age, replace)

* Cohort effect
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
    ytitle("Non-grain Income(%)") ///
    name(g_cohort, replace)

* Period effect
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
    ytitle("Non-grain Income(%)") ///
    name(g_year, replace)

*---------------------------------------------------
* 6) Combine and export
*---------------------------------------------------
graph combine g_age g_cohort g_year, ///
    col(1) ///
    ysize(20) xsize(12) ///
    imargin(small) ///
    ycommon ///
    graphregion(color(white)) ///
    name(g_non_grain_income, replace)

graph export "./output/Figure3_NonGrain_Income.pdf", replace
