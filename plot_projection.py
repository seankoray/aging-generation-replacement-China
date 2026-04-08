"""
Plot projection results: relative trend and contribution decomposition.

Input:
  - trend_index.csv
  - contribution_shares.csv
  - age_group_output_shares.csv

Output:
  - output/projection_trend.pdf
  - output/contribution_decomposition.pdf
  - output/effect_comparison.pdf
  - output/age_group_output_shares.pdf
  - output/projection_combined.pdf
"""

import pandas as pd
import numpy as np
from pathlib import Path

from plot_style import Figure, COLORS

TREND_FILE = Path("trend_index.csv")
CONTRIBUTION_FILE = Path("contribution_shares.csv")
AGE_SHARES_FILE = Path("age_group_output_shares.csv")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SCENARIOS = ['SSP1', 'SSP2', 'SSP3']
SCENARIO_COLORS = {
    'SSP1': '#4e79a7',
    'SSP2': '#2ca02c',
    'SSP3': '#ff7f0e',
}


def plot_relative_trend(trend_df: pd.DataFrame) -> None:
    """Plot relative trend index for all SSP scenarios (grouped bar chart)."""
    fig = Figure(figsize=(10, 6))
    ax = fig.get_ax()

    trend_df_filtered = trend_df[trend_df['year'] != 2015].copy()
    years = sorted(trend_df_filtered['year'].unique())
    n_years = len(years)
    n_scenarios = len(SCENARIOS)
    width = 0.6 / n_scenarios

    x = np.arange(n_years)

    legend_bars_trend = []

    for i, scenario in enumerate(SCENARIOS):
        df = trend_df_filtered[trend_df_filtered['scenario'] == scenario].copy()
        df = df.sort_values('year')
        values = df['index'].values
        bars = ax.bar(x + i * width, values, width=width,
                        color=SCENARIO_COLORS[scenario],
                        edgecolor='white', linewidth=0.3)
        legend_bars_trend.append(bars[0])

        for j, (bar, val) in enumerate(zip(bars, values)):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                      f'{val:.1f}', ha='center', va='bottom', fontsize=7)

    ax.axhline(y=100, color=COLORS['gray'], linestyle='--', linewidth=0.8, alpha=0.5)
    ax.set_xlabel('Year')
    ax.set_ylabel('Index (2015 = 100)')
    ax.set_xticks(x + width * (n_scenarios - 1) / 2)
    ax.set_xticklabels(years)
    ax.set_ylim(bottom=80)

    fig.legend_handles = legend_bars_trend
    fig.legend_labels = SCENARIOS
    fig.add_legend(position='bottom', ncol=3)

    output_file = OUTPUT_DIR / 'projection_trend.pdf'
    fig.save(output_file, formats=['png'])
    print(f"Saved: {output_file}")


def plot_contribution_decomposition(contribution_df: pd.DataFrame) -> None:
    """Plot contribution decomposition for all SSP scenarios (stacked bars)."""
    fig = Figure(figsize=(14, 4), nrows=1, ncols=3, sharey=False)
    axes = fig.get_axes()

    effect_colors = {
        'quantity': '#4e79a7',
        'cohort': '#d62728',
        'interaction': '#ff7f0e',
    }

    legend_bars = []

    for idx, (scenario, ax) in enumerate(zip(SCENARIOS, axes)):
        df = contribution_df[contribution_df['scenario'] == scenario].copy()
        df = df.sort_values('year')
        df = df[df['year'] != 2015].copy()

        x = np.arange(len(df))
        width = 0.6

        bottom = np.zeros(len(df))

        for i, effect in enumerate(['quantity_share_pct', 'cohort_share_pct', 'interaction_share_pct']):
            effect_type = effect.split('_')[0]
            values = df[effect].values
            bars = ax.bar(x, values, bottom=bottom, color=effect_colors[effect_type],
                         width=width, edgecolor='white', linewidth=0.3)
            bottom += values

            if idx == 0:
                legend_bars.append(bars[0])

        ax.axhline(y=0, color=COLORS['dark_gray'], linestyle='-', linewidth=0.8)

        ax.set_xticks(x)
        ax.set_xticklabels(df['year'])
        ax.set_xlabel('Year')

        if idx == 0:
            ax.set_ylabel('Relative Importance (%)')
        ax.set_title(scenario, pad=10)

        total_change = df['total_change'].values
        for i, (x_pos, total) in enumerate(zip(x, total_change)):
            ax.text(x_pos, 100 + 1, f'{total:+.1f}%',
                    ha='center', va='bottom', fontsize=7)

        quantity_vals = df['quantity_share_pct'].values
        cohort_vals = df['cohort_share_pct'].values

        for i, x_pos in enumerate(x):
            q_val = quantity_vals[i]
            ax.text(x_pos, q_val / 2, f'{int(q_val)}',
                    ha='center', va='center', fontsize=8, color='white', weight='bold')
            c_val = cohort_vals[i]
            q_bottom = quantity_vals[i]
            ax.text(x_pos, q_bottom + c_val / 2, f'{int(c_val)}',
                    ha='center', va='center', fontsize=8, color='white', weight='bold')

    fig.legend_handles = legend_bars
    fig.legend_labels = ['Quantity Effect', 'Cohort Effect', 'Interaction Effect']
    fig.add_legend(position='bottom', ncol=3)

    output_file = OUTPUT_DIR / 'contribution_decomposition.pdf'
    fig.save(output_file, formats=['png'])
    print(f"Saved: {output_file}")


def plot_effect_comparison(contribution_df: pd.DataFrame) -> None:
    """Plot comparison of each effect across scenarios (three panels)."""
    fig = Figure(figsize=(14, 4), nrows=1, ncols=3, sharex=True)
    axes = fig.get_axes()

    effect_labels = {
        'quantity_share_pct': 'Quantity Effect',
        'cohort_share_pct': 'Cohort Effect',
        'interaction_share_pct': 'Interaction Effect',
    }

    for idx, (effect_col, ax) in enumerate(zip(
            ['quantity_share_pct', 'cohort_share_pct', 'interaction_share_pct'], axes)):
        for scenario in SCENARIOS:
            df = contribution_df[contribution_df['scenario'] == scenario].copy()
            df = df.sort_values('year')
            ax.plot(df['year'], df[effect_col],
                    color=SCENARIO_COLORS[scenario],
                    marker='o', linewidth=1.5, markersize=4, label=scenario)

        ax.axhline(y=0, color=COLORS['dark_gray'], linestyle='-', linewidth=0.8)

        ax.set_xlabel('Year')

        if idx == 0:
            ax.set_ylabel('Relative Importance (%)')
        ax.set_title(effect_labels[effect_col], pad=10)

    fig.legend_handles = [axes[0].lines[i] for i in range(len(SCENARIOS))]
    fig.legend_labels = SCENARIOS
    fig.add_legend(position='bottom', ncol=3)

    output_file = OUTPUT_DIR / 'effect_comparison.pdf'
    fig.save(output_file, formats=['png'])
    print(f"Saved: {output_file}")


def plot_age_group_output_shares(age_shares_df: pd.DataFrame) -> None:
    """Plot age group output shares for all SSP scenarios (stacked bars)."""
    AGE_GROUPS = ['55-59', '60-64', '65-69', '70-74', '75-79', '80+']
    AGE_COLORS = {
        '55-59': '#4e79a7',
        '60-64': '#2ca02c',
        '65-69': '#ff7f0e',
        '70-74': '#9467bd',
        '75-79': '#8c564b',
        '80+': '#7f7f7f',
    }

    fig = Figure(figsize=(14, 4), nrows=1, ncols=3, sharey=False)
    axes = fig.get_axes()

    legend_bars = []

    for idx, (scenario, ax) in enumerate(zip(SCENARIOS, axes)):
        df = age_shares_df[age_shares_df['scenario'] == scenario].copy()
        df = df.sort_values('year')

        pivot_df = df.pivot(index='year', columns='age_group', values='share_pct')
        years = pivot_df.index.tolist()

        x = np.arange(len(years))
        width = 0.6

        bottom = np.zeros(len(years))

        for age_group in AGE_GROUPS:
            values = pivot_df[age_group].values
            bars = ax.bar(x, values, bottom=bottom, color=AGE_COLORS[age_group],
                         width=width, edgecolor='white', linewidth=0.3)
            bottom += values

            if idx == 0:
                legend_bars.append(bars[0])

        ax.axhline(y=0, color=COLORS['dark_gray'], linestyle='-', linewidth=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(years)
        ax.set_xlabel('Year')

        if idx == 0:
            ax.set_ylabel('Output Share (%)')
        ax.set_title(scenario, pad=10)

        bottom_label = np.zeros(len(df))
        for age_group in AGE_GROUPS:
            values = pivot_df[age_group].values
            for i, (x_pos, val) in enumerate(zip(x, values)):
                if val > 3:
                    ax.text(x_pos, bottom_label[i] + val / 2, f'{int(val)}',
                            ha='center', va='center', fontsize=7, color='white')
                bottom_label[i] += val

    fig.legend_handles = legend_bars
    fig.legend_labels = AGE_GROUPS
    fig.add_legend(position='bottom', ncol=6)

    output_file = OUTPUT_DIR / 'age_group_output_shares.pdf'
    fig.save(output_file, formats=['png'])
    print(f"Saved: {output_file}")


def plot_combined_figure(trend_df: pd.DataFrame, contribution_df: pd.DataFrame, age_shares_df: pd.DataFrame = None) -> None:
    """Plot combined figure with projection trend (A) and contribution decomposition (B)."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    fig = plt.figure(figsize=(14, 5))

    axes = fig.subplots(1, 2, squeeze=False).flatten()

    EFFECT_COLORS = {
        'quantity': '#4e79a7',
        'cohort': '#d62728',
        'interaction': '#ff7f0e',
    }

    # Panel A: Projection Trend
    ax_a = axes[0]

    trend_df_filtered = trend_df[trend_df['year'] != 2015].copy()
    years = sorted(trend_df_filtered['year'].unique())
    n_years = len(years)
    n_scenarios = len(SCENARIOS)
    width = 0.6 / n_scenarios

    x = np.arange(n_years)

    for i, scenario in enumerate(SCENARIOS):
        df = trend_df_filtered[trend_df_filtered['scenario'] == scenario].copy()
        df = df.sort_values('year')
        values = df['index'].values
        bars = ax_a.bar(x + i * width, values, width=width,
                        color=SCENARIO_COLORS[scenario],
                        edgecolor='white', linewidth=0.3)

        for j, (bar, val) in enumerate(zip(bars, values)):
            ax_a.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                      f'{val:.1f}', ha='center', va='bottom', fontsize=7)

    ax_a.axhline(y=100, color=COLORS['gray'], linestyle='--', linewidth=0.8, alpha=0.5)
    ax_a.set_xlabel('Year')
    ax_a.set_ylabel('Index (2015 = 100)')
    ax_a.set_xticks(x + width * (n_scenarios - 1) / 2)
    ax_a.set_xticklabels(years)
    ax_a.set_ylim(bottom=80)
    ax_a.text(-0.12, 1.05, 'A', transform=ax_a.transAxes,
              fontsize=14, weight='bold', va='top')

    # Panel B: Contribution Decomposition (SSP2)
    ax_b = axes[1]

    scenario = 'SSP2'
    df = contribution_df[contribution_df['scenario'] == scenario].copy()
    df = df.sort_values('year')
    df = df[df['year'] != 2015].copy()

    x_b = np.arange(len(df))
    width_b = 0.6

    bottom = np.zeros(len(df))

    for i, effect in enumerate(['quantity_share_pct', 'cohort_share_pct', 'interaction_share_pct']):
        effect_type = effect.split('_')[0]
        values = df[effect].values
        bars = ax_b.bar(x_b, values, bottom=bottom, color=EFFECT_COLORS[effect_type],
                        width=width_b, edgecolor='white', linewidth=0.3)
        bottom += values

    ax_b.axhline(y=0, color=COLORS['dark_gray'], linestyle='-', linewidth=0.8)
    ax_b.set_xticks(x_b)
    ax_b.set_xticklabels(df['year'])
    ax_b.set_xlabel('Year')
    ax_b.set_ylabel('Relative Importance (%)')
    ax_b.set_ylim(bottom=-5, top=110)
    ax_b.text(-0.12, 1.05, 'B', transform=ax_b.transAxes,
              fontsize=14, weight='bold', va='top')

    total_change = df['total_change'].values
    for i, (x_pos, total) in enumerate(zip(x_b, total_change)):
        ax_b.text(x_pos, 100 + 1, f'{total:+.1f}%',
                  ha='center', va='bottom', fontsize=7)

    quantity_vals = df['quantity_share_pct'].values
    cohort_vals = df['cohort_share_pct'].values

    for i, x_pos in enumerate(x_b):
        q_val = quantity_vals[i]
        ax_b.text(x_pos, q_val / 2, f'{int(q_val)}',
                  ha='center', va='center', fontsize=8, color='white', weight='bold')
        c_val = cohort_vals[i]
        q_bottom = quantity_vals[i]
        ax_b.text(x_pos, q_bottom + c_val / 2, f'{int(c_val)}',
                  ha='center', va='center', fontsize=8, color='white', weight='bold')

    legend_a_patches = [Patch(facecolor=SCENARIO_COLORS[s], edgecolor='white', linewidth=0.5) for s in SCENARIOS]
    ax_a.legend(legend_a_patches, SCENARIOS, loc='upper center',
                bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)

    effect_keys = ['quantity', 'cohort', 'interaction']
    effect_labels = ['Quantity Effect', 'Cohort Effect', 'Interaction Effect']
    legend_b_patches = [Patch(facecolor=EFFECT_COLORS[effect], edgecolor='white', linewidth=0.5) for effect in effect_keys]
    ax_b.legend(legend_b_patches, effect_labels, loc='upper center',
                bbox_to_anchor=(0.5, -0.15), ncol=3, frameon=False)

    plt.tight_layout()
    output_file = OUTPUT_DIR / 'projection_combined.pdf'
    fig.savefig(output_file, format='pdf', bbox_inches='tight')
    fig.savefig(str(output_file).replace('.pdf', '.png'), format='png', dpi=150, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close(fig)


def main():
    print("=" * 80)
    print("Plotting Projection Results")
    print("=" * 80)

    print("\n1. Loading data...")
    trend_df = pd.read_csv(TREND_FILE)
    contribution_df = pd.read_csv(CONTRIBUTION_FILE)
    age_shares_df = pd.read_csv(AGE_SHARES_FILE)
    print(f"   Trend data: {len(trend_df)} rows")
    print(f"   Contribution data: {len(contribution_df)} rows")
    print(f"   Age group shares: {len(age_shares_df)} rows")

    print("\n2. Plotting relative trend...")
    plot_relative_trend(trend_df)

    print("\n3. Plotting contribution decomposition...")
    plot_contribution_decomposition(contribution_df)

    print("\n4. Plotting effect comparison...")
    plot_effect_comparison(contribution_df)

    print("\n5. Plotting age group output shares...")
    plot_age_group_output_shares(age_shares_df)

    print("\n6. Plotting combined figure...")
    plot_combined_figure(trend_df, contribution_df, age_shares_df)

    print(f"\nDone! Figures saved in {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
