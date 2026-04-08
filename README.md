# Aging, Generation Replacement and Grain Productivity in China

**Authors:** Shouying Liu, Xue Qiao, Kerui Shen

Replication code for the manuscript "Aging, Generation Replacement and Grain Productivity in China."

## Repository Structure

```
.
├── README.md
├── calculate_projection.py      # APC projection: trend index and contribution decomposition
├── plot_projection.py           # Plot projection figures (SSP1/SSP2/SSP3 scenarios)
├── plot_style.py                # Publication-quality plotting module
│
├── Figure1_AB_demo_trend.do     # Fig 1A: Population share by age group (inline data)
├── Figure1_C_input_comparision.do  # Fig 1C: Input scale and intensity comparison
├── Figure1_D_tfp_comparision.do    # Fig 1D: TFP gaps over time
├── Figure2_APC_baseline.do      # Fig 2: APC decomposition of TFP
├── Figure3_Nongrain_income.do   # Fig 3: Non-grain income share (mechanism 1)
├── Figure4_Exit.do              # Fig 4: Exit probability from grain production (mechanism 2)
├── Figure5_Table1_Buffer.do     # Fig 5 & Table 1: Machinery buffer effect (mechanism 3)
├── SI_HAPC.do                   # SI: HAPC model estimates
│
├── stata_apc_coefficients.csv   # APC coefficients from Stata regression
├── rural_aging_indicators.csv   # Rural population by age group (SSP scenarios)
├── trend_index.csv              # Projected trend index (2015=100)
├── contribution_shares.csv      # Contribution decomposition results
├── age_group_output_shares.csv  # Age group output share projections
├── ssp_raw.xlsx                 # Raw SSP scenario population data
└── Figure6_projection.pdf       # Pre-generated projection figure
```

## Script-to-Figure Mapping

| Script | Output |
|--------|--------|
| `Figure1_AB_demo_trend.do` | Fig 1A: Population age structure trend (2003-2017) |
| `Figure1_C_input_comparision.do` | Fig 1C: Input scale/intensity comparison across age groups |
| `Figure1_D_tfp_comparision.do` | Fig 1D: TFP gaps over time |
| `Figure2_APC_baseline.do` | Fig 2: Age-Period-Cohort decomposition of TFP |
| `Figure3_Nongrain_income.do` | Fig 3: Non-grain income share APC decomposition |
| `Figure4_Exit.do` | Fig 4: Discrete-time exit model |
| `Figure5_Table1_Buffer.do` | Fig 5 + Table 1: Age x Machinery interaction |
| `SI_HAPC.do` | SI Table: HAPC (mixed-effects) model estimates |
| `calculate_projection.py` | Intermediate CSV files for projection |
| `plot_projection.py` | Fig 6: Projection under SSP scenarios |

## Data Availability

- **Stata scripts** require confidential household survey microdata that cannot be publicly shared due to data use agreements. Researchers interested in accessing the data should contact the authors.
- **Python scripts** for projection analysis are fully reproducible using the included CSV files and `ssp_raw.xlsx`.
- The Stata scripts reference placeholder filenames (`main_panel.dta`, `exit_supplement.dta`) that should be replaced with actual data paths.

## Software Requirements

- **Stata 18** (with `reghdfe`, `estout` packages)
- **Python 3.8+** with:
  - `pandas`
  - `numpy`
  - `matplotlib`

## How to Run

### Stata Scripts
1. Install required packages: `ssc install reghdfe, replace` and `ssc install estout, replace`
2. Update the `use` command at the top of each script to point to your data files
3. Run scripts in order (Figure1 -> Figure5, SI_HAPC)

### Python Scripts
1. Ensure CSV files are in the same directory as the scripts
2. Run `python calculate_projection.py` to generate intermediate files
3. Run `python plot_projection.py` to produce figures in `output/`

## License

This code is provided for research replication purposes. Please cite the paper if you use this code.
