****************************************************
* Mechanism 2: Discrete-Time Exit Model
* Models the probability of exiting grain production
****************************************************

clear all
set more off

*---------------------------------------------------
* 0) Load main data and append exit supplement
*---------------------------------------------------
use "./data/main_panel.dta", clear
append using "./data/exit_supplement.dta"

capture confirm numeric variable hhid
if _rc {
    destring hhid, replace force
}

*---------------------------------------------------
* 1) Panel setup
*---------------------------------------------------
isid hhid year
xtset hhid year

*---------------------------------------------------
* 2) Construct "has next wave" indicator
*---------------------------------------------------
gen byte has_next = !missing(F.sow)
label var has_next "Has observation in next wave (t+1)"

*---------------------------------------------------
* 3) Construct exit event
*---------------------------------------------------
gen byte exit = .
replace exit = 0 if sow==1 & has_next==1
replace exit = 1 if sow==1 & has_next==1 & F.sow==0
label var exit "Exit grain production next wave"

*---------------------------------------------------
* 4) First-exit only: drop observations after first exit
*---------------------------------------------------
by hhid (year): egen first_exit_year = min(cond(exit==1, year, .))
label var first_exit_year "First exit year (if any)"
drop if !missing(first_exit_year) & year > first_exit_year

*---------------------------------------------------
* 5) Keep risk set only
*---------------------------------------------------
keep if sow==1 & has_next==1
assert inlist(exit,0,1)

order year hhid vid sow has_next exit first_exit_year

*---------------------------------------------------
* 6) Age variable (agricultural labor)
*---------------------------------------------------
capture drop age_use
gen age_use = round(age_agrilabor)
label var age_use "Age (agricultural labor, rounded)"

capture drop age_group1
gen byte age_group1 = .
replace age_group1 = 0  if inrange(age_use,16,25)
replace age_group1 = 1  if inrange(age_use,26,30)
replace age_group1 = 2  if inrange(age_use,31,35)
replace age_group1 = 3  if inrange(age_use,36,40)
replace age_group1 = 4  if inrange(age_use,41,45)
replace age_group1 = 5  if inrange(age_use,46,50)
replace age_group1 = 6  if inrange(age_use,51,55)
replace age_group1 = 7  if inrange(age_use,56,60)
replace age_group1 = 8  if inrange(age_use,61,65)
replace age_group1 = 9  if inrange(age_use,66,70)
replace age_group1 = 10 if inrange(age_use,71,75)
replace age_group1 = 11 if inrange(age_use,76,80)
replace age_group1 = 12 if inrange(age_use,81,90)

label define age_group1_lbl ///
    0 "16-25" 1 "26-30" 2 "31-35" 3 "36-40" 4 "41-45" ///
    5 "46-50" 6 "51-55" 7 "56-60" 8 "61-65" 9 "66-70" ///
    10 "71-75" 11 "76-80" 12 "81-90"
label values age_group1 age_group1_lbl
label var age_group1 "Age group"

assert !missing(age_group1) if !missing(age_use)

*---------------------------------------------------
* 7) Controls
*---------------------------------------------------
local controls count_famsize edu_agrilabor internet sow_food inc_govern

*---------------------------------------------------
* 8) Pooled logit regressions
*---------------------------------------------------
set scheme white_tableau
compress

capture drop vid_id
egen vid_id = group(vid)
label var vid_id "Village ID (compact)"

* (A1) By age group
logit exit ///
    i.age_group1 ///
    `controls' ///
    i.year, ///
    vce(cluster vid_id)

margins age_group1, atmeans
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
    ytitle("Pr(Exit next wave)") ///
    name(g_exit_age1, replace)

* (A2) Continuous age
logit exit ///
    i.age_use ///
    `controls' ///
    i.year, ///
    vce(cluster vid)

margins, at(age_use=(16(5)81)) atmeans
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
    xtitle("Age") ///
    ytitle("Pr(Exit next wave)") ///
    name(g_exit_age2, replace)

*---------------------------------------------------
* 9) Combine and export
*---------------------------------------------------
graph combine g_exit_age1 g_exit_age2, ///
    col(1) ///
    ysize(15) xsize(12) ///
    imargin(small) ///
    graphregion(color(white)) ///
    name(g_exit_age, replace)

graph export "./output/Figure4_Exit.pdf", replace
