****************************************************
* Mechanism Analysis: Machinery Services as a Buffer
* Tests whether mechanization mitigates age-related
* productivity decline (Age x Machinery interaction)
****************************************************

clear all
set more off

*---------------------------------------------------
* 0) Load data (EDIT PATH as needed)
*---------------------------------------------------
use "./data/main_panel.dta", clear

compress

*---------------------------------------------------
* 1) Panel setup
*---------------------------------------------------
confirm variable hhid year vid
capture confirm numeric variable hhid
if _rc {
    destring hhid, replace force
}
xtset hhid year

*---------------------------------------------------
* 2) Key variables
*---------------------------------------------------
capture drop age_use
gen age_use = round(age_agrilabor)
label var age_use "Age (agricultural labor, rounded)"

drop if missing(sow_food) | sow_food<=0

capture drop mach_mu ln_mach_mu
gen double mach_mu = mach_food_real / sow_food if !missing(mach_food_real)
gen double ln_mach_mu = ln(1 + mach_mu) if !missing(mach_mu)
label var mach_mu "Mechanization service fee per mu"
label var ln_mach_mu "ln(1 + mechanization service fee per mu)"

capture drop labor_mu ln_labor_mu
gen double labor_mu = labor_d_food_real / sow_food if !missing(labor_d_food_real)
gen double ln_labor_mu = ln(1 + labor_mu) if !missing(labor_mu)
label var labor_mu "Family labor days per mu"
label var ln_labor_mu "ln(1 + family labor days per mu)"

*---------------------------------------------------
* 3) Controls and sample
*---------------------------------------------------
confirm variable lntfp

local controls count_famsize edu_agrilabor internet sow_food inc_govern

drop if missing(lntfp, age_use, ln_mach_mu, ln_labor_mu, vid, year)

*---------------------------------------------------
* 4) Old-age threshold dummies (55/60/65/70/75/80)
*---------------------------------------------------
foreach k in 55 60 65 70 75 80 {
    capture drop old`k'
    gen byte old`k' = (age_use >= `k') if !missing(age_use)
    label var old`k' "Age >= `k'"
}

*---------------------------------------------------
* 5) Core mechanism: Age x Machinery interaction
*     FE: village + year; SE: clustered at village
*---------------------------------------------------
estimates clear

reghdfe lntfp ///
    c.age_use##c.ln_mach_mu ///
    `controls', ///
    absorb(vid year) vce(cluster vid) keepsingleton

estimates store M0_AgeXMech_vFE

*---------------------------------------------------
* 6) Multiple old-age thresholds: Old_k x Machinery
*---------------------------------------------------
foreach k in 55 60 65 70 75 80 {

    reghdfe lntfp ///
        i.old`k'##c.ln_mach_mu ///
        `controls', ///
        absorb(vid year) vce(cluster vid) keepsingleton

    estimates store M_old`k'
}

*---------------------------------------------------
* 7) Plot: Age-productivity curves by mechanization level
*---------------------------------------------------
set scheme white_tableau
estimates restore M0_AgeXMech_vFE

quietly sum ln_mach_mu, detail
local p25 = r(p25)
local p50 = r(p50)
local p75 = r(p75)

margins, at(age_use=(45(5)85) ln_mach_mu=(`p25' `p50' `p75')) atmeans level(95)
marginsplot, ///
    recast(line) ///
    recastci(rline) ///
    plotopts(lwidth(thick)) ///
    ciopts(lpattern(dash) lwidth(medthin)) ///
    graphregion(color(white)) ///
    plotregion(color(white)) ///
    ylabel(, nogrid angle(0)) ///
    xlabel(, nogrid angle(45)) ///
    legend(order(1 "Low mech (p25)" 2 "Median mech (p50)" 3 "High mech (p75)") ring(0) pos(11) cols(1)) ///
    title("", size(medsmall)) ///
    xtitle("Age") ///
    ytitle("Predicted ln(TFP)") ///
    name(g_age_mech_buffer, replace)

graph export "./output/Figure5_Buffer.pdf", replace

*---------------------------------------------------
* 8) Export table: Old-age threshold comparison
*---------------------------------------------------
capture which esttab
if _rc {
    di as txt "Note: esttab not found. To export tables, run: ssc install estout, replace"
}
else {
    capture mkdir "./output"

    esttab M_old55 M_old60 M_old65 M_old70 M_old75 M_old80 ///
        using "./output/Table1_mech_old_thresholds.tex", ///
        replace ///
        b(%9.3f) se(%9.3f) ///
        star(* 0.10 ** 0.05 *** 0.01) ///
        stats(N r2, labels("Observations" "R-squared")) ///
        title("Mechanization services and productivity across alternative old-age thresholds") ///
        label
}
