"""
Calculate projection results for SSP1, SSP2, SSP3 scenarios.

Formulas:
- y_{g,t} = y*_{2015} * alpha_g * beta_{g,t}
- Y_t = y*_{2015} * sum_g (alpha_g * beta_{g,t} * N_{g,t})
- Index: Y~_t = 100 * Y_t / Y_{2015}
- Decomposition:
  - Quantity effect: alpha_g * beta_{g,2015} * Delta N_{g,t}
  - Cohort effect: alpha_g * N_{g,2015} * Delta beta_{g,t}
  - Interaction effect: Delta beta_{g,t} * Delta N_{g,t}

Input:
  - stata_apc_coefficients.csv (APC coefficients)
  - rural_aging_indicators.csv (population data by age group)

Output:
  - output/trend_index.csv
  - output/contribution_shares.csv
"""

import pandas as pd
from pathlib import Path

APC_FILE = Path("stata_apc_coefficients.csv")
POP_FILE = Path("rural_aging_indicators.csv")
OUTPUT_DIR = Path("output")

AGE_GROUPS = ['55-59', '60-64', '65-69', '70-74', '75-79', '80+']

AGE_GROUP_COLUMNS = {
    '55-59': 'rural_55_59_million',
    '60-64': 'rural_60_64_million',
    '65-69': 'rural_65_69_million',
    '70-74': 'rural_70_74_million',
    '75-79': 'rural_75_79_million',
    '80+': 'rural_80plus_million',
}
TARGET_YEARS = [2015, 2020, 2025, 2030, 2035, 2040, 2045, 2050]
SCENARIOS = ['SSP1', 'SSP2', 'SSP3']

AGE_LOWER_BOUNDS = {
    '55-59': 55, '60-64': 60, '65-69': 65, '70-74': 70, '75-79': 75, '80+': 80,
}

AGE_MULTIPLIERS = {
    '55-59': 0.9550,
    '60-64': 0.9550,
    '65-69': 0.9507,
    '70-74': 0.9352,
    '75-79': 0.9289,
    '80+': 0.9682,
}

COHORT_MULTIPLIERS = [1.0, 0.9710, 0.9273, 0.9352, 0.9289, 0.9197, 0.9142, 0.9010, 0.9006, 0.8937, 0.8934, 0.8801, 0.8455]


def read_apc_coefficients(filepath: str) -> dict:
    """Read and parse APC coefficients from CSV file."""
    with open(filepath, 'r') as f:
        content = f.read()

    age_lines = [line for line in content.split('\n')[2:8] if line.strip() and not line.startswith('#')]
    age_coeffs = {}
    for line in age_lines:
        parts = line.split(',')
        age_group = parts[0].strip()
        multiplier = float(parts[2].strip())
        age_coeffs[age_group] = multiplier

    cohort_lines = [line for line in content.split('\n')[11:26] if line.strip() and not line.startswith('#')]
    cohort_coeffs = {}
    for line in cohort_lines:
        parts = line.split(',')
        cohort_group = int(parts[0].strip())
        multiplier = float(parts[4].strip())
        cohort_coeffs[cohort_group] = multiplier

    return age_coeffs, cohort_coeffs


def get_cohort_idx(age_group: str, year: int) -> int:
    """Map age group and year to cohort index (c(g,t) = t - L_g)."""
    L_g = AGE_LOWER_BOUNDS[age_group]
    birth_year = year - L_g

    if birth_year <= 1929:
        return 0
    elif birth_year <= 1934:
        return 1
    elif birth_year <= 1939:
        return 2
    elif birth_year <= 1944:
        return 3
    elif birth_year <= 1949:
        return 4
    elif birth_year <= 1954:
        return 5
    elif birth_year <= 1959:
        return 6
    elif birth_year <= 1964:
        return 7
    elif birth_year <= 1969:
        return 8
    elif birth_year <= 1974:
        return 9
    elif birth_year <= 1979:
        return 10
    elif birth_year <= 1984:
        return 11
    else:
        return 12


def calculate_base_sum(df_scenario: pd.DataFrame, age_multipliers: dict, cohort_multipliers: dict) -> float:
    """Calculate base year (2015) sum for a scenario."""
    base_sum = 0.0
    for _, row in df_scenario.iterrows():
        age_group = row['age_group']
        alpha_g = age_multipliers[age_group]
        cohort_idx = get_cohort_idx(age_group, 2015)
        beta_c = cohort_multipliers[cohort_idx]
        N_g = row['population']
        base_sum += alpha_g * beta_c * N_g
    return base_sum


def calculate_projection_trend(pop_df: pd.DataFrame, age_multipliers: dict,
                          cohort_multipliers: dict, scenarios: list, years: list) -> pd.DataFrame:
    """Calculate relative index trends for all scenarios."""
    results = []

    for scenario in scenarios:
        scenario_2015 = pop_df[(pop_df['scenario'] == scenario) & (pop_df['year'] == 2015)].copy()
        base_sum = calculate_base_sum(scenario_2015, age_multipliers, cohort_multipliers)

        for year in years:
            scenario_year = pop_df[(pop_df['scenario'] == scenario) & (pop_df['year'] == year)].copy()
            current_sum = 0.0
            for _, row in scenario_year.iterrows():
                age_group = row['age_group']
                alpha_g = age_multipliers[age_group]
                cohort_idx = get_cohort_idx(age_group, year)
                beta_c = cohort_multipliers[cohort_idx]
                N_g = row['population']
                current_sum += alpha_g * beta_c * N_g
            index_value = current_sum / base_sum * 100.0
            results.append({'scenario': scenario, 'year': year, 'index': index_value})

    return pd.DataFrame(results)


def calculate_contribution_shares(pop_df: pd.DataFrame, age_multipliers: dict,
                               cohort_multipliers: dict, scenarios: list, years: list) -> pd.DataFrame:
    """Calculate contribution shares using absolute values (shares sum to 100%)."""
    results = []

    for scenario in scenarios:
        scenario_2015 = pop_df[(pop_df['scenario'] == scenario) & (pop_df['year'] == 2015)].copy()
        base_sum = calculate_base_sum(scenario_2015, age_multipliers, cohort_multipliers)

        for year in years:
            if year == 2015:
                results.append({
                    'scenario': scenario, 'year': year, 'index': 100.0,
                    'total_change': 0.0, 'quantity_effect': 0.0,
                    'cohort_effect': 0.0, 'interaction_effect': 0.0,
                    'quantity_share_pct': 0.0, 'cohort_share_pct': 0.0,
                    'interaction_share_pct': 0.0,
                })
                continue

            scenario_year = pop_df[(pop_df['scenario'] == scenario) & (pop_df['year'] == year)].copy()

            quantity_total = 0.0
            cohort_total = 0.0
            interaction_total = 0.0

            for _, row_2015 in scenario_2015.iterrows():
                age_group = row_2015['age_group']
                row_curr = scenario_year[scenario_year['age_group'] == age_group]

                if len(row_curr) > 0:
                    alpha_g = age_multipliers[age_group]
                    beta_2015 = cohort_multipliers[get_cohort_idx(age_group, 2015)]
                    beta_year = cohort_multipliers[get_cohort_idx(age_group, year)]

                    N_2015 = row_2015['population'].values[0] if isinstance(row_2015, pd.DataFrame) else row_2015['population']
                    N_year = row_curr['population'].values[0]

                    delta_N = N_year - N_2015
                    delta_beta = beta_year - beta_2015

                    quantity_total += alpha_g * beta_2015 * delta_N
                    cohort_total += alpha_g * N_2015 * delta_beta
                    interaction_total += delta_beta * delta_N

            current_sum = 0.0
            for _, row in scenario_year.iterrows():
                age_group = row['age_group']
                alpha_g = age_multipliers[age_group]
                cohort_idx = get_cohort_idx(age_group, year)
                beta_c = cohort_multipliers[cohort_idx]
                N_g = row['population']
                current_sum += alpha_g * beta_c * N_g

            index_value = (current_sum / base_sum) * 100.0
            total_change = index_value - 100.0

            total_absolute_effects = abs(quantity_total) + abs(cohort_total) + abs(interaction_total)

            if total_absolute_effects != 0:
                quantity_share_pct = abs(quantity_total) / total_absolute_effects * 100.0
                cohort_share_pct = abs(cohort_total) / total_absolute_effects * 100.0
                interaction_share_pct = abs(interaction_total) / total_absolute_effects * 100.0
            else:
                quantity_share_pct = 0.0
                cohort_share_pct = 0.0
                interaction_share_pct = 0.0

            results.append({
                'scenario': scenario, 'year': year, 'index': index_value,
                'total_change': total_change,
                'quantity_effect': quantity_total, 'cohort_effect': cohort_total,
                'interaction_effect': interaction_total,
                'quantity_share_pct': quantity_share_pct,
                'cohort_share_pct': cohort_share_pct,
                'interaction_share_pct': interaction_share_pct,
            })

    return pd.DataFrame(results)


def calculate_age_group_output_shares(pop_df: pd.DataFrame, age_multipliers: dict,
                                   cohort_multipliers: dict, scenarios: list, years: list) -> pd.DataFrame:
    """Calculate the percentage contribution of each age group to total elderly farmer output."""
    results = []

    for scenario in scenarios:
        for year in years:
            scenario_year = pop_df[(pop_df['scenario'] == scenario) & (pop_df['year'] == year)].copy()

            outputs = []
            total_output = 0.0

            for _, row in scenario_year.iterrows():
                age_group = row['age_group']
                alpha_g = age_multipliers[age_group]
                cohort_idx = get_cohort_idx(age_group, year)
                beta_c = cohort_multipliers[cohort_idx]
                N_g = row['population']

                output = alpha_g * beta_c * N_g
                outputs.append((age_group, output))
                total_output += output

            for age_group, output in outputs:
                share_pct = (output / total_output) * 100.0 if total_output != 0 else 0.0
                results.append({
                    'scenario': scenario, 'year': year,
                    'age_group': age_group, 'share_pct': share_pct,
                })

    return pd.DataFrame(results)


def main():
    print("=" * 80)
    print("Projection: Relative Trend Index and Contribution Decomposition")
    print("=" * 80)

    print("\n1. Reading APC coefficients...")
    age_coeffs, cohort_coeffs = read_apc_coefficients(APC_FILE)
    print(f"   Age coefficients: {len(age_coeffs)} groups")
    print(f"   Cohort coefficients: {len(cohort_coeffs)} groups")

    print("\n2. Reading SSP population data...")
    pop_wide = pd.read_csv(POP_FILE)
    pop_wide = pop_wide[pop_wide['scenario'].isin(SCENARIOS)].copy()
    print(f"   Loaded: {len(pop_wide)} rows (wide format)")

    pop_rows = []
    for _, row in pop_wide.iterrows():
        scenario = row['scenario']
        year = row['year']
        for age_group, col_name in AGE_GROUP_COLUMNS.items():
            population = row[col_name]
            pop_rows.append({
                'scenario': scenario, 'year': year,
                'age_group': age_group, 'population': population,
            })

    pop_df = pd.DataFrame(pop_rows)
    print(f"   Transformed: {len(pop_df)} rows (long format)")

    print("\n3. Calculating relative trend index...")
    trend_df = calculate_projection_trend(pop_df, AGE_MULTIPLIERS,
                                              COHORT_MULTIPLIERS,
                                              SCENARIOS, TARGET_YEARS)
    print(f"   Output: {len(trend_df)} rows")

    print("\n4. Calculating contribution decomposition...")
    share_df = calculate_contribution_shares(pop_df, AGE_MULTIPLIERS,
                                                 COHORT_MULTIPLIERS,
                                                 SCENARIOS, TARGET_YEARS)
    print(f"   Output: {len(share_df)} rows")

    print("\n5. Saving results...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    trend_file = OUTPUT_DIR / "trend_index.csv"
    trend_df.to_csv(trend_file, index=False, float_format='%.4f')
    print(f"   Saved: {trend_file}")

    share_file = OUTPUT_DIR / "contribution_shares.csv"
    share_df.to_csv(share_file, index=False, float_format='%.4f')
    print(f"   Saved: {share_file}")

    print("\n6. Calculating age group output shares...")
    age_shares_df = calculate_age_group_output_shares(pop_df, AGE_MULTIPLIERS,
                                                     COHORT_MULTIPLIERS,
                                                     SCENARIOS, TARGET_YEARS)
    print(f"   Output: {len(age_shares_df)} rows")

    age_shares_file = OUTPUT_DIR / "age_group_output_shares.csv"
    age_shares_df.to_csv(age_shares_file, index=False, float_format='%.4f')
    print(f"   Saved: {age_shares_file}")

    # Summary tables
    print("\n" + "=" * 80)
    print("Relative Trend Index (2015=100)")
    print("=" * 80)
    pivot_trend = trend_df.pivot(index='year', columns='scenario', values='index')
    print(pivot_trend.to_string())

    print("\n" + "=" * 80)
    print("Contribution Decomposition (SSP2, 2015-2050)")
    print("=" * 80)
    ssp2_share = share_df[share_df['scenario'] == 'SSP2'].copy()
    print(f"{'Year':<8} {'Index':>8} {'Change':>8} {'Qty%':>8} {'Coh%':>8} {'Int%':>8}")
    print("-" * 50)
    for _, row in ssp2_share.iterrows():
        print(f"{row['year']:>8} {row['index']:>7.1f} {row['total_change']:>7.1f}% "
              f"{row['quantity_share_pct']:>7.1f}% {row['cohort_share_pct']:>7.1f}% "
              f"{row['interaction_share_pct']:>7.1f}%")

    print("\nDone!")


if __name__ == '__main__':
    main()
