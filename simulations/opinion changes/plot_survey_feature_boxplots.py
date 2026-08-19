# Plot Figure-2-style boxplots for survey-initialised Axelrod runs.
# Bars = locked observed feature-change proportions from the results ledger.
# Boxplots = simulated relative endpoint changes across saved random seeds.

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from survey_preprocessing import (
    ATTITUDE_COLS,
    FEATURE_LABELS,
    get_project_root,
    print_resolved_paths,
)


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = get_project_root(SCRIPT_DIR)

sim_results = SCRIPT_DIR / "survey_model_T1_T4_feature_changes.csv"
feature_results_file = SCRIPT_DIR / "survey_T1_T4_definitive_feature_results.csv"
output_png = SCRIPT_DIR / "final_empirical_feature_change_figure.png"
output_pdf = SCRIPT_DIR / "final_empirical_feature_change_figure.pdf"

attitude_cols = ATTITUDE_COLS
feature_labels = FEATURE_LABELS

print_resolved_paths(
    "plot_survey_feature_boxplots.py",
    project_root=PROJECT_ROOT,
    script_dir=SCRIPT_DIR,
    sim_results=sim_results,
    output_file=output_png,
)
print(f"  feature_results_file: {feature_results_file.resolve()}")
print(f"  output_pdf: {output_pdf.resolve()}")

# Load locked feature-level results and saved model output. Simulations are not rerun.
feature_results = pd.read_csv(feature_results_file)
sim = pd.read_csv(sim_results)

# Observed proportions are taken from the authoritative feature-results file.
expected_counts = [89, 114, 116, 110, 58, 110, 102, 102]
expected_relative = np.array(expected_counts, dtype=float) / 801
observed_relative = feature_results["observed_relative"].to_numpy(dtype=float)
if not np.allclose(observed_relative, expected_relative, atol=1e-12):
    raise ValueError("Observed proportions do not match the locked 801-change values.")
if feature_results["feature_label"].tolist() != feature_labels:
    raise ValueError("Feature order does not match the locked dissertation order.")

# Simulated relative endpoint-change distributions from the saved definitive runs.
relative_cols = [f"feature_{i}_relative_changes" for i in range(len(attitude_cols))]
boxplot_data = [sim[col].dropna() for col in relative_cols]

# Basic checks against the locked empirical analysis.
print("Observed total changes:", int(feature_results["observed_count"].sum()))
print("Simulation target changes:", sim["target_changes"].unique())
print("Simulation successful changes:", sim["successful_changes"].unique())
print("All targets reached:", sim["target_reached"].all())
print("Seeds:", int(sim["seed"].min()), "to", int(sim["seed"].max()))

# Plot
x = np.arange(len(attitude_cols))

plt.figure(figsize=(10, 6))

# Boxplots for simulation distribution
plt.boxplot(
    boxplot_data,
    positions=x,
    widths=0.45,
    showfliers=True,
)

# Bars for observed data
plt.bar(
    x,
    observed_relative,
    width=0.5,
    alpha=0.75,
    label="Observed proportion",
)

plt.xticks(x, feature_labels, rotation=45, ha="right")
plt.ylabel("Proportion of feature changes")
plt.title("Observed vs simulated relative feature changes, T1 to T4")
plt.legend()
plt.tight_layout()
plt.savefig(output_png, dpi=300)
plt.savefig(output_pdf)
plt.close()

print(f"Saved PNG to {output_png}")
print(f"Saved PDF to {output_pdf}")
