*========================================================
* Fig 1A: Population Share by Age Group (Inline Data)
*========================================================
clear
set more off

* 1) Data (2003-2017 household survey)
input year young mid old
2003 12.11 66.82 21.07
2004 9.65  65.96 24.39
2005 7.95  63.88 28.18
2006 6.63  63.62 29.75
2007 5.91  61.63 32.46
2008 4.50  58.53 36.97
2009 7.98  60.53 31.49
2010 6.93  58.76 34.31
2011 6.58  56.66 36.76
2012 5.65  56.07 38.28
2013 5.47  54.02 40.50
2014 4.75  52.91 43.34
2015 4.03  51.97 44.00
2016 4.17  50.26 45.57
2017 3.07  48.92 48.01
end

* 2) Cumulative boundaries for stacked area
gen cum_y = young
gen cum_m = young + mid
gen cum_o = young + mid + old
gen zero  = 0

* 3) Plot
twoway ///
    (rarea zero  cum_y year,  color("166 189 219%85") lcolor(none)) ///
    (rarea cum_y cum_m year,  color("150 150 150%60") lcolor(none)) ///
    (rarea cum_m cum_o year,  color("240 128 128%85") lcolor(none)) ///
    , ///
    yscale(range(0 100) noline) ///
    ylabel(0(20)100, labsize(3.5) nogrid angle(0) format(%2.0f)) ///
    xscale(range(2003 2017) lcolor(black)) ///
    xlabel(2003(2)2017, labsize(3.5) nogrid) ///
    xtitle("Year", size(3.5) margin(t=2)) ///
    ytitle("Share of households (%)", size(3.5) margin(r=2)) ///
    legend(order(3 "Old (>=55)" 2 "Middle-aged (36-55)" 1 "Young (<=35)") ///
           pos(6) ring(1) cols(3) region(lstyle(none)) size(3)) ///
    graphregion(color(white)) ///
    plotregion(color(white) lcolor(black) lwidth(thin)) ///
    xsize(7) ysize(5)

graph export "./output/Figure1A.png", replace
