# Axelrod Cultural Dissemination

MSc research project investigating cultural convergence, fragmentation, and
polarisation using agent-based modelling based on Axelrod's classical cultural
dissemination model.

## Research Motivation
This project investigates how simple local interaction rules can generate
large-scale social patterns such as consensus, stable diversity, and
fragmentation. The starting point is the classical Axelrod model, which offers
a compact way to study how homophily and social influence interact over time.

The broader MSc research goal is to use that baseline model as a foundation for
later extensions, including network topology changes, immigration or
integration dynamics, and creator-consumer influence dynamics.

## Current Stage
**Current stage: baseline Axelrod implementation**

This repository is an active research codebase. At present, only the classical
baseline Axelrod model is implemented. Future extensions are planned, but they
are not yet implemented unless explicitly stated.

## What Is Implemented Now
- A maintained baseline Axelrod model in
  [`src/axelrod/model.py`](src/axelrod/model.py)
- A two-dimensional lattice with Von Neumann neighbourhoods and open
  boundaries
- Asynchronous interaction based on cultural similarity
- Active-edge tracking over time
- Cultural-domain labelling
- A baseline run command that saves current output figures
- A baseline notebook in
  [`notebooks/exp01_baseline.ipynb`](notebooks/exp01_baseline.ipynb)

## What Is Planned Next
- Parameter sensitivity analysis across `N`, `F`, `q`, and random seeds
- Alternative network structures
- Immigration and integration dynamics
- Creator-consumer influence dynamics
- Comparative analysis across model variants

## Research Questions
- Under what conditions does the baseline Axelrod model converge to a shared
  culture?
- Under what conditions does it remain fragmented into multiple cultural
  domains?
- How sensitive are outcomes to parameter choices and stopping rules?
- How do alternative network structures change convergence and fragmentation?
- How might immigration or creator-consumer influence alter those dynamics?

## Repository Layout
```text
axelrod-cultural-dissemination/
├── config/                  # Parameters and configuration
├── data/                    # Raw and processed inputs (currently minimal)
├── docs/                    # Research notes, roadmap, and experiment templates
├── notebooks/               # Baseline notebook plus planning notebooks
├── results/                 # Saved figures and future result tables
└── src/axelrod/             # Maintained Python package
```

## Installation
From the repository root:

```bash
pip install -r requirements.txt
```

## How To Run the Current Baseline
From the repository root:

```bash
PYTHONPATH=src python -m axelrod.model
```

This command runs the current baseline model and writes figures into
[`results/figures`](results/figures).

## Current Outputs
The current baseline implementation provides:

- [`results/figures/initial_feature_0.png`](results/figures/initial_feature_0.png)
- [`results/figures/final_cultural_domains.png`](results/figures/final_cultural_domains.png)
- [`results/figures/activity_decay.png`](results/figures/activity_decay.png)

These outputs reflect the present baseline model only. Future stages will test
additional dynamics and produce comparative results.

## Roadmap
| Stage | Description | Status |
|---|---|---|
| Stage 1 | Classical Axelrod baseline implementation | Complete |
| Stage 2 | Parameter sensitivity analysis | In progress |
| Stage 3 | Network topology extension | Planned |
| Stage 4 | Immigration/integration extension | Planned |
| Stage 5 | Creator-consumer influence extension | Planned |
| Stage 6 | Comparative analysis and dissertation figures | Planned |

See [`docs/research_roadmap.md`](docs/research_roadmap.md) for the fuller
research plan.

## Documentation
- [`docs/01_problem_definition.md`](docs/01_problem_definition.md)
- [`docs/02_model_description.md`](docs/02_model_description.md)
- [`docs/03_assumptions.md`](docs/03_assumptions.md)
- [`docs/04_method.md`](docs/04_method.md)
- [`docs/05_results.md`](docs/05_results.md)
- [`docs/06_limitations.md`](docs/06_limitations.md)
- [`docs/research_roadmap.md`](docs/research_roadmap.md)
- [`docs/experiment_template.md`](docs/experiment_template.md)
- [`docs/work_log.md`](docs/work_log.md)

## Academic Integrity / Research Status
This repository is evolving during an MSc research project. The code,
notebooks, and documentation reflect work in progress rather than a final
research product. Planned extensions should not be interpreted as implemented
results unless they are documented as such in code, notebooks, or the results
files.
