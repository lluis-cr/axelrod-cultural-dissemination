# Modelling Opinion Dynamics Using Longitudinal Data

Minimal reproducibility archive for Lluis Cobos Roca's MSc dissertation, University of Limerick, 2026.

This repository contains the Appendix C source scripts, saved public-safe outputs, and final figures. Raw survey data are not included.

## Contents

- `simulations/topologies/`: lattice and topology comparison scripts plus baseline logs.
- `simulations/q sweep/`: trait-space sweep script, 3,200-run log and summary.
- `simulations/F sweep/`: feature-number sweep script, 3,200-run log and summary.
- `simulations/opinion changes/`: survey preprocessing, empirical simulations and empirical plotting scripts.
- `outputs/`: small empirical and baseline comparison CSVs.
- `figures/`: final dissertation figures as PNG files.
- `environment_versions.txt`: submitted environment record.

## Environment

Python 3.13.0. Main package versions:

```text
numpy==2.1.3
pandas==2.2.3
matplotlib==3.9.2
networkx==3.4.2
scipy==1.15.1
pillow==11.0.0
```

## Restricted Data

To rerun the empirical scripts, place the restricted survey files here:

```text
survey data/Election 2020 T1.csv
survey data/Election 2020 T4.csv
```

These files are not distributed and must not be committed.

## Quick Check

```bash
python validate_outputs.py
```

Expected anchors: q-sweep 3,200 absorbed runs; F-sweep 3,189 absorbed and 11 non-absorbed runs; empirical observed vector `(89, 114, 116, 110, 58, 110, 102, 102)`; simulated mean vector `(83.00, 113.54, 116.68, 115.12, 67.56, 92.72, 107.96, 104.42)`.

## Regeneration

The full sweeps are computationally expensive.

```bash
python "simulations/q sweep/axelrod_q_sweep.py"
python "simulations/F sweep/axelrod_f_sweep.py"
python "simulations/plot_final_dissertation_sweep_figures.py"
python "simulations/opinion changes/axelrod_simulations_opinion_changes.py"
python "simulations/opinion changes/plot_survey_feature_boxplots.py"
python "simulations/opinion changes/plot_baseline_model_comparison.py"
```
