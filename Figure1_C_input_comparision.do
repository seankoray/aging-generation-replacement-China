****************************************************
* Fig 1C: Input Scale and Intensity Comparison
****************************************************

*---------------------------------------------------
* 0) Load data (EDIT PATH as needed)
*---------------------------------------------------
use "./data/main_panel.dta", clear

*---------------------------------------------------
* 1) Sample selection
*---------------------------------------------------
keep if inlist(age_group,1,2,3)
keep if sow_food > 0
drop if missing(year, age_group, sow_food)

local CLUSTER hhid

*---------------------------------------------------
* 2) Convert land: mu -> hectare
*---------------------------------------------------
gen land_ha = sow_food/15

gen labor_ha = labor_d_food_real / land_ha
gen mach_ha  = mach_food_real     / land_ha
gen inter_ha = total_food_real    / land_ha

*---------------------------------------------------
* 3) Log transforms
*---------------------------------------------------
replace ln_land     = ln(land_ha)
gen ln_labor_ha = ln(1 + labor_ha)
gen ln_mach_ha  = ln(1 + mach_ha)
gen ln_inter_ha = ln(1 + inter_ha)

*---------------------------------------------------
* 4) Regressions
*---------------------------------------------------
tempfile fig1c
postfile P str60 outcome byte grp double b se using `fig1c', replace

foreach y in ln_land ln_labor_ha ln_mach_ha ln_inter_ha {

    regress `y' ib2.age_group i.year, vce(cluster `CLUSTER')

    lincom 1.age_group
    local b1  = r(estimate)
    local se1 = r(se)

    lincom 3.age_group
    local b3  = r(estimate)
    local se3 = r(se)

    if "`y'"=="ln_land" {
        post P ("Land (hectares)") (1) (`b1') (`se1')
        post P ("Land (hectares)") (3) (`b3') (`se3')
    }

    if "`y'"=="ln_labor_ha" {
        post P ("Labor per hectare") (1) (`b1') (`se1')
        post P ("Labor per hectare") (3) (`b3') (`se3')
    }

    if "`y'"=="ln_mach_ha" {
        post P ("Machine services per hectare") (1) (`b1') (`se1')
        post P ("Machine services per hectare") (3) (`b3') (`se3')
    }

    if "`y'"=="ln_inter_ha" {
        post P ("Intermediate inputs per hectare") (1) (`b1') (`se1')
        post P ("Intermediate inputs per hectare") (3) (`b3') (`se3')
    }
}

postclose P
use `fig1c', clear

*---------------------------------------------------
* 5) Confidence intervals
*---------------------------------------------------
gen lo = b - 1.96*se
gen hi = b + 1.96*se

gen y = .
replace y = 4 if outcome=="Land (hectares)"
replace y = 3 if outcome=="Labor per hectare"
replace y = 2 if outcome=="Machine services per hectare"
replace y = 1 if outcome=="Intermediate inputs per hectare"

gen y_plot = y
replace y_plot = y_plot - 0.12 if grp==1
replace y_plot = y_plot + 0.12 if grp==3

label define grplab 1 "Young vs. middle-aged" 3 "Old vs. middle-aged"
label values grp grplab

*---------------------------------------------------
* 6) Plot
*---------------------------------------------------
twoway ///
    (rcap lo hi y_plot if grp==1, horizontal lcolor(navy%60) lwidth(medthin)) ///
    (scatter y_plot b if grp==1, msymbol(O) msize(medium) mcolor(navy)) ///
    (rcap lo hi y_plot if grp==3, horizontal lcolor(orange_red%60) lwidth(medthin)) ///
    (scatter y_plot b if grp==3, msymbol(D) msize(medium) mcolor(orange_red)) ///
    , ///
    xline(0, lcolor(gs10) lwidth(thin)) ///
    xscale(range(-.45 .22)) ///
    xlabel(-.4 -.2 0 .2, nogrid labsize(medium)) ///
    ylab( ///
        1 "Intermediate" ///
        2 "Machine" ///
        3 "Labor" ///
        4 "Land" ///
        , angle(0) nogrid labsize(medium)) ///
    xtitle("") ///
    ytitle("") ///
    legend( ///
        order(2 "Young vs. Middle-aged" ///
              4 "Old vs. Middle-aged") ///
        pos(6) ring(1) ///
        cols(1) ///
        region(lstyle(none)) ///
        size(medium)) ///
    graphregion(color(white) margin(l=14 r=6 t=4 b=6)) ///
    plotregion(color(white) margin(l=4 r=4 t=2 b=2)) ///
    xsize(7.2) ysize(4.8) ///
    scheme(s1color)

graph export "./output/Figure1C.png", replace
