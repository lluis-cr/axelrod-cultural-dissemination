from pathlib import Path

import pandas as pd


ATTITUDE_COLS = [
    "Att_Abort",
    "Att_Inc",
    "Att_Imm",
    "Att_Welf",
    "Att_LGBT",
    "Att_Busn",
    "Att_Gun",
    "Att_Race",
]

CHANGED_COLS = [f"{col}_changed" for col in ATTITUDE_COLS]

FEATURE_LABELS = [
    "Abortion",
    "Income",
    "Immigration",
    "Welfare",
    "LGBT",
    "Business",
    "Gun",
    "Race",
]


def get_project_root(script_dir):
    return Path(script_dir).resolve().parents[1]


def get_survey_paths(project_root):
    project_root = Path(project_root).resolve()
    return {
        "t1": project_root / "survey data" / "Election 2020 T1.csv",
        "t4": project_root / "survey data" / "Election 2020 T4.csv",
        "opinion_changes_t1_t4": project_root
        / "survey data"
        / "opinion changes per timepoint"
        / "opinion_changes_T1_T4.csv",
    }


def print_resolved_paths(label, project_root, script_dir=None, sim_results=None, output_file=None):
    print(f"Resolved paths for {label}:")
    if script_dir is not None:
        print(f"  script_dir: {Path(script_dir).resolve()}")
    print(f"  project_root: {Path(project_root).resolve()}")

    for name, path in get_survey_paths(project_root).items():
        print(f"  {name}: {path.resolve()}")

    if sim_results is not None:
        print(f"  sim_results: {Path(sim_results).resolve()}")
    if output_file is not None:
        print(f"  output_file: {Path(output_file).resolve()}")


def load_clean_t1_t4_endpoint_changes(project_root):
    paths = get_survey_paths(project_root)

    t1_raw = pd.read_csv(paths["t1"])
    t4_raw = pd.read_csv(paths["t4"])

    t1 = t1_raw.drop_duplicates(subset="ID", keep="first")[["ID"] + ATTITUDE_COLS]
    t4 = t4_raw.drop_duplicates(subset="ID", keep="first")[["ID"] + ATTITUDE_COLS]

    merged = t1.merge(t4, on="ID", how="inner", suffixes=("_T1", "_T4"))

    required_cols = [f"{col}_T1" for col in ATTITUDE_COLS] + [
        f"{col}_T4" for col in ATTITUDE_COLS
    ]
    merged = merged.dropna(subset=required_cols).copy()

    t1_data_with_id = merged[["ID"] + [f"{col}_T1" for col in ATTITUDE_COLS]].copy()
    t1_data_with_id.columns = ["ID"] + ATTITUDE_COLS

    observed_changes = merged[["ID"]].copy()
    for col in ATTITUDE_COLS:
        observed_changes[f"{col}_changed"] = (
            merged[f"{col}_T1"] != merged[f"{col}_T4"]
        ).astype(int)

    observed_total = int(observed_changes[CHANGED_COLS].sum().sum())

    return {
        "t1_data_with_id": t1_data_with_id.reset_index(drop=True),
        "t1_data": t1_data_with_id[ATTITUDE_COLS].reset_index(drop=True),
        "observed_changes": observed_changes.reset_index(drop=True),
        "observed_total": observed_total,
        "paths": paths,
    }
