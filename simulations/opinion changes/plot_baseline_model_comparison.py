# Compare observed T1-T4 endpoint changes with baseline and Axelrod models.

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from survey_preprocessing import (
    ATTITUDE_COLS,
    FEATURE_LABELS,
    get_project_root,
    load_clean_t1_t4_endpoint_changes,
    print_resolved_paths,
)


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = get_project_root(SCRIPT_DIR)

sim_results = SCRIPT_DIR / "survey_model_T1_T4_feature_changes.csv"
feature_results_file = SCRIPT_DIR / "survey_T1_T4_definitive_feature_results.csv"
output_png = SCRIPT_DIR / "baseline_model_feature_comparison.png"
output_pdf = SCRIPT_DIR / "baseline_model_feature_comparison.pdf"

EXPECTED_OBSERVED_COUNTS = np.array([89, 114, 116, 110, 58, 110, 102, 102], dtype=float)
EXPECTED_DYNAMIC_MEAN = np.array(
    [83.00, 113.54, 116.68, 115.12, 67.56, 92.72, 107.96, 104.42],
    dtype=float,
)
EXPECTED_PLOTTING_VALUES = pd.DataFrame(
    {
        "feature_label": FEATURE_LABELS,
        "observed": EXPECTED_OBSERVED_COUNTS,
        "uniform": [100.125] * 8,
        "marginal": [89.18, 108.25, 109.18, 108.41, 78.52, 97.29, 106.04, 104.12],
        "one_step": [79.35, 113.52, 122.22, 119.59, 57.22, 95.17, 114.48, 99.46],
        "dynamic_mean": EXPECTED_DYNAMIC_MEAN,
    }
)

OBSERVED_TOTAL = 801
N_RESPONDENTS = 343
N_RUNS = 50
TOLERANCE = 1e-8


def load_and_validate_data():
    # Load saved results and cleaned T1 responses.
    print_resolved_paths(
        "plot_baseline_model_comparison.py",
        project_root=PROJECT_ROOT,
        script_dir=SCRIPT_DIR,
        sim_results=sim_results,
        output_file=output_png,
    )
    print(f"  feature_results_file: {feature_results_file.resolve()}")
    print(f"  output_pdf: {output_pdf.resolve()}")

    cleaned_survey = load_clean_t1_t4_endpoint_changes(PROJECT_ROOT)
    t1_data = cleaned_survey["t1_data"]
    feature_results = pd.read_csv(feature_results_file)
    sim = pd.read_csv(sim_results)

    if FEATURE_LABELS != [
        "Abortion",
        "Income",
        "Immigration",
        "Welfare",
        "LGBT",
        "Business",
        "Gun",
        "Race",
    ]:
        raise ValueError("Canonical feature labels have changed.")

    if feature_results["feature_label"].tolist() != FEATURE_LABELS:
        raise ValueError("Feature-results file does not use the canonical feature order.")

    observed_counts = feature_results["observed_count"].to_numpy(dtype=float)
    if not np.array_equal(observed_counts, EXPECTED_OBSERVED_COUNTS):
        raise ValueError("Observed counts do not match the locked 801-change values.")
    if not np.isclose(observed_counts.sum(), OBSERVED_TOTAL, atol=TOLERANCE):
        raise ValueError("Observed counts do not sum to 801 endpoint changes.")

    if len(t1_data) != N_RESPONDENTS:
        raise ValueError(f"Expected {N_RESPONDENTS} complete T1 cases, found {len(t1_data)}.")
    if len(ATTITUDE_COLS) != 8:
        raise ValueError("Expected eight attitude features.")

    if len(sim) != N_RUNS:
        raise ValueError(f"Expected {N_RUNS} dynamic simulation runs, found {len(sim)}.")
    if set(sim["seed"].tolist()) != set(range(N_RUNS)):
        raise ValueError("Dynamic simulations must contain seeds 0-49 exactly once.")
    if not sim["target_reached"].all():
        raise ValueError("Not every dynamic run reached the endpoint-change target.")
    if not (sim["endpoint_changes"] == OBSERVED_TOTAL).all():
        raise ValueError("Not every dynamic run stopped at 801 endpoint changes.")

    dynamic_mean = feature_results["simulated_endpoint_count_mean"].to_numpy(dtype=float)
    run_level_mean = sim[[f"feature_{i}_changes" for i in range(8)]].mean().to_numpy()
    if not np.allclose(dynamic_mean, run_level_mean, atol=TOLERANCE):
        raise ValueError("Definitive dynamic means do not match run-level means.")
    if not np.allclose(dynamic_mean, EXPECTED_DYNAMIC_MEAN, atol=TOLERANCE):
        raise ValueError("Dynamic mean vector does not match the locked values.")

    return t1_data, feature_results, sim


def calculate_uniform_baseline(observed_total, n_features):
    # Equal allocation across features.
    return np.full(n_features, observed_total / n_features, dtype=float)


def calculate_marginal_disagreement_baseline(t1_data):
    # Weight features by T1 marginal disagreement.
    disagreement_weights = []
    for col in ATTITUDE_COLS:
        trait_proportions = t1_data[col].value_counts(normalize=True)
        disagreement = 1 - sum(p**2 for p in trait_proportions)
        disagreement_weights.append(disagreement)

    disagreement_weights = np.array(disagreement_weights, dtype=float)
    return OBSERVED_TOTAL * disagreement_weights / disagreement_weights.sum()


def calculate_static_one_step_axelrod_baseline(t1_data):
    # Weight features by possible one-step Axelrod interactions.
    feature_vectors = t1_data[ATTITUDE_COLS].to_numpy()
    n_features = len(ATTITUDE_COLS)
    feature_weights = np.zeros(n_features, dtype=float)

    for i in range(len(feature_vectors) - 1):
        pairwise_matches = feature_vectors[i + 1 :] == feature_vectors[i]
        overlaps = pairwise_matches.mean(axis=1)
        valid_pairs = (overlaps > 0) & (overlaps < 1)

        if not valid_pairs.any():
            continue

        differing_features = ~pairwise_matches[valid_pairs]
        n_differing = differing_features.sum(axis=1)
        pair_contributions = (
            overlaps[valid_pairs] / n_differing
        )[:, np.newaxis] * differing_features
        feature_weights += pair_contributions.sum(axis=0)

    return OBSERVED_TOTAL * feature_weights / feature_weights.sum()


def calculate_performance_metrics(observed, predictions):
    # Pearson correlation and mean absolute error.
    rows = []
    for model_name, predicted in predictions.items():
        if np.isclose(np.std(predicted), 0):
            pearson_r = np.nan
        else:
            pearson_r = float(np.corrcoef(observed, predicted)[0, 1])

        rows.append(
            {
                "model": model_name,
                "pearson_r": pearson_r,
                "mae": float(np.mean(np.abs(observed - predicted))),
            }
        )

    return pd.DataFrame(rows)


def validate_predictions(observed, predictions):
    # Check totals and rounded plotting values.
    plotting_values = pd.DataFrame(
        {
            "feature_label": FEATURE_LABELS,
            "observed": observed,
            "uniform": predictions["Uniform allocation"],
            "marginal": predictions["T1 marginal disagreement"],
            "one_step": predictions["Static one-step Axelrod"],
            "dynamic_mean": predictions["Dynamic Axelrod mean"],
        }
    )

    for col in ["observed", "uniform", "marginal", "one_step", "dynamic_mean"]:
        if not np.isclose(plotting_values[col].sum(), OBSERVED_TOTAL, atol=TOLERANCE):
            raise ValueError(f"{col} does not sum to 801 endpoint changes.")

    numeric_cols = ["observed", "uniform", "marginal", "one_step", "dynamic_mean"]
    if not np.allclose(
        plotting_values[numeric_cols].to_numpy(),
        EXPECTED_PLOTTING_VALUES[numeric_cols].to_numpy(),
        atol=0.01,
    ):
        print("\nCalculated plotting values:")
        print(plotting_values.to_string(index=False))
        print("\nExpected plotting values:")
        print(EXPECTED_PLOTTING_VALUES.to_string(index=False))
        raise ValueError("Calculated baseline values differ from validation targets.")

    return plotting_values


def create_and_save_figure(plotting_values):
    # Create the feature-level comparison figure.
    x = np.arange(len(FEATURE_LABELS))

    plt.figure(figsize=(10, 6))
    ax = plt.gca()

    # Plot model predictions behind the observed counts.
    model_styles = {
        "uniform": {
            "label": "Uniform allocation",
            "color": "#7F7F7F",
            "marker": "s",
            "linestyle": "--",
        },
        "marginal": {
            "label": "T1 marginal disagreement",
            "color": "#0072B2",
            "marker": "^",
            "linestyle": "-",
        },
        "one_step": {
            "label": "Static one-step Axelrod",
            "color": "#D55E00",
            "marker": "D",
            "linestyle": "-",
        },
        "dynamic_mean": {
            "label": "Dynamic Axelrod mean",
            "color": "#009E73",
            "marker": "v",
            "linestyle": "-",
        },
    }

    for col, style in model_styles.items():
        ax.plot(
            x,
            plotting_values[col],
            label=style["label"],
            color=style["color"],
            marker=style["marker"],
            linestyle=style["linestyle"],
            linewidth=1.4,
            markersize=5.5,
            alpha=0.9,
            zorder=2,
        )

    ax.scatter(
        x,
        plotting_values["observed"],
        label="Observed",
        color="black",
        marker="o",
        s=54,
        zorder=4,
    )

    ax.set_xticks(x)
    ax.set_xticklabels(FEATURE_LABELS, rotation=45, ha="right")
    ax.set_ylabel("Number of endpoint changes")
    ax.grid(True, axis="y", color="#D8D8D8", linewidth=0.7)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(
        ncol=5,
        frameon=False,
        loc="lower center",
        bbox_to_anchor=(0.5, 1.02),
        fontsize=9,
        handlelength=1.8,
        columnspacing=1.0,
    )

    plt.tight_layout()
    plt.savefig(output_png, dpi=300, bbox_inches="tight")
    plt.savefig(output_pdf, bbox_inches="tight")
    plt.close()

    print(f"Saved PNG to {output_png}")
    print(f"Saved PDF to {output_pdf}")


def main():
    # Run validation, baseline calculations and plotting.
    t1_data, feature_results, sim = load_and_validate_data()

    observed = feature_results["observed_count"].to_numpy(dtype=float)
    predictions = {
        "Uniform allocation": calculate_uniform_baseline(OBSERVED_TOTAL, len(ATTITUDE_COLS)),
        "T1 marginal disagreement": calculate_marginal_disagreement_baseline(t1_data),
        "Static one-step Axelrod": calculate_static_one_step_axelrod_baseline(t1_data),
        "Dynamic Axelrod mean": feature_results[
            "simulated_endpoint_count_mean"
        ].to_numpy(dtype=float),
    }

    plotting_values = validate_predictions(observed, predictions)
    metrics = calculate_performance_metrics(observed, predictions)

    print("\nFeature-level comparison values:")
    print(plotting_values.to_string(index=False))
    print("\nPerformance metrics:")
    print(metrics.to_string(index=False, na_rep="Undefined"))
    print("\nDynamic run checks:")
    print(f"  runs: {len(sim)}")
    print(f"  seeds: {int(sim['seed'].min())}-{int(sim['seed'].max())}")
    print(f"  all target reached: {bool(sim['target_reached'].all())}")
    print(f"  endpoint changes: {sorted(sim['endpoint_changes'].unique().tolist())}")

    create_and_save_figure(plotting_values)


if __name__ == "__main__":
    main()
