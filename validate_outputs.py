from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent


def read_csv(path):
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def as_bool(series):
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().map({"true": True, "false": False})


q = read_csv(ROOT / "simulations/q sweep/axelrod_q_sweep_full_log200.csv")
f = read_csv(ROOT / "simulations/F sweep/axelrod_f_sweep_full_log200.csv")
emp = read_csv(ROOT / "outputs/survey_model_T1_T4_feature_changes.csv")
features = read_csv(ROOT / "outputs/survey_T1_T4_definitive_feature_results.csv")
metrics = read_csv(ROOT / "outputs/final_null_model_metrics.csv")

if len(q) != 3200 or not as_bool(q["frozen"]).all():
    raise SystemExit("q-sweep validation failed")

f_absorbed = as_bool(f["frozen"])
non_absorbed = f.loc[~f_absorbed]
if len(f) != 3200 or int(f_absorbed.sum()) != 3189 or len(non_absorbed) != 11:
    raise SystemExit("F-sweep absorption counts failed")
if not ((non_absorbed["topology"] == "complete") & (non_absorbed["n_features"] == 20) & (non_absorbed["frozen_step"] == 200000)).all():
    raise SystemExit("F-sweep non-absorbed condition failed")

if len(emp) != 50 or set(emp["seed"]) != set(range(50)):
    raise SystemExit("empirical seed validation failed")
if set(emp["topology"]) != {"complete"} or set(emp["N"]) != {343} or set(emp["n_features"]) != {8}:
    raise SystemExit("empirical design validation failed")
if not as_bool(emp["target_reached"]).all() or set(emp["stop_reason"]) != {"target_reached"} or set(emp["endpoint_changes"]) != {801}:
    raise SystemExit("empirical stopping validation failed")

observed = features["observed_count"].to_numpy(dtype=float)
simulated = features["simulated_endpoint_count_mean"].to_numpy(dtype=float)
if not np.array_equal(observed, np.array([89, 114, 116, 110, 58, 110, 102, 102], dtype=float)):
    raise SystemExit("observed feature vector failed")
if not np.allclose(simulated, np.array([83.00, 113.54, 116.68, 115.12, 67.56, 92.72, 107.96, 104.42])):
    raise SystemExit("simulated mean vector failed")

dynamic = metrics.loc[metrics["model"] == "Dynamic Axelrod mean"].iloc[0]
if not np.isclose(dynamic["pearson_r"], 0.897998) or not np.isclose(dynamic["mae_endpoint_changes"], 5.935):
    raise SystemExit("metric validation failed")

print("Validation passed.")
