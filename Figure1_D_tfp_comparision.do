****************************************************
* Fig 1D: TFP Gaps Over Time
****************************************************

use "./data/main_panel.dta", clear

local CLUSTER hhid

keep if inlist(age_group,1,2,3)
drop if missing(lntfp, age_group, year)

quietly levelsof year, local(yrs)

tempfile tfp_gaps
postfile P int year byte grp double b se using `tfp_gaps', replace

tokenize "`yrs'"
while "`1'" != "" {

    local t = `1'

    quietly regress lntfp ib2.age_group if year==`t', vce(cluster `CLUSTER')

    quietly lincom 1.age_group
    post P (`t') (1) (r(estimate)) (r(se))

    quietly lincom 3.age_group
    post P (`t') (3) (r(estimate)) (r(se))

    mac shift
}

postclose P
use `tfp_gaps', clear

* Confidence intervals
gen lo = b - 1.96*se
gen hi = b + 1.96*se

label define grplab 1 "Young vs. middle-aged" 3 "Old vs. middle-aged"
label values grp grplab

quietly summarize year, meanonly
local ymin = r(min)
local ymax = r(max)

local xticks
forvalues yy = `ymin'(2)`ymax' {
    local xticks "`xticks' `yy'"
}

* Plot
twoway ///
    (rcap lo hi year if grp==1, lcolor(navy%60) lwidth(medthin)) ///
    (connected b year if grp==1, lcolor(navy) lwidth(medthin) ///
        msymbol(O) msize(medsmall) mcolor(navy)) ///
    (rcap lo hi year if grp==3, lcolor(orange_red%60) lwidth(medthin)) ///
    (connected b year if grp==3, lcolor(orange_red) lwidth(medthin) ///
        msymbol(D) msize(medsmall) mcolor(orange_red)) ///
    , ///
    yline(0, lcolor(gs10) lwidth(thin)) ///
    xscale(range(`ymin' `ymax')) ///
    xlabel(`xticks', labsize(medium) nogrid) ///
    ylabel(, labsize(medium) nogrid) ///
    xtitle("") ytitle("") ///
    legend(order(2 "Young vs. Middle-aged" 4 "Old vs. Middle-aged") ///
           pos(6) ring(1) cols(1) region(lstyle(none)) size(medium)) ///
    graphregion(color(white) margin(l=14 r=6 t=4 b=6)) ///
    plotregion(color(white) margin(l=4 r=4 t=2 b=2)) ///
    xsize(7.2) ysize(4.8) ///
    scheme(s1color)

graph export "./output/Figure1D.png", replace
