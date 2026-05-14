# Axelrod Cultural Dissemination Model

Simulation of how societies converge, fragment, or polarise using an
agent-based implementation of the Axelrod cultural dissemination model.

## What This Project Does
This project implements the classical Axelrod model on a two-dimensional
lattice:

- agents sit on a 2D lattice,
- each agent has multiple cultural features and discrete traits,
- agents interact more often when they are already culturally similar,
- local interaction can produce consensus, fragmentation, or long-lived frozen
  dynamics.

The current implementation focuses on the baseline model and its reproducible
outputs.

## Example Outputs
The baseline implementation currently saves three standard outputs:

- initial cultural distribution:
  [`results/figures/initial_feature_0.png`](results/figures/initial_feature_0.png)
- final cultural domains:
  [`results/figures/final_cultural_domains.png`](results/figures/final_cultural_domains.png)
- activity decay over time:
  [`results/figures/activity_decay.png`](results/figures/activity_decay.png)

## Current Implementation
- Baseline Axelrod model
- 2D lattice
- Von Neumann neighbourhood
- Open boundaries
- Asynchronous similarity-based interaction
- Active-edge tracking
- Cultural-domain labelling
- Baseline notebook:
  [`notebooks/exp01_baseline.ipynb`](notebooks/exp01_baseline.ipynb)
- Baseline run command:
  `PYTHONPATH=src python -m axelrod.model`

## Installation
```bash
pip install -r requirements.txt
```

## Run the Baseline Model
From the repository root:

```bash
PYTHONPATH=src python -m axelrod.model
```

## Repository Layout
```text
src/axelrod/        # Core model implementation
notebooks/          # Baseline experiment
results/figures/    # Output visualisations
docs/               # Supporting documentation
config/             # Parameters
data/               # Placeholder for datasets
```

## Research Context
This model is being developed as part of broader MSc research into cultural
convergence, fragmentation, and polarisation. The public repository focuses on
the implemented model code and reproducible baseline experiments.

## Research Questions
- When does the Axelrod model converge to a shared culture?
- When does it remain fragmented into multiple cultural domains?
- How sensitive are outcomes to parameter choices and stopping rules?
- How might topology or influence asymmetry change those dynamics?

## Extensions Planned
- Parameter sensitivity analysis
- Alternative network structures
- Immigration and integration dynamics
- Influence asymmetry, such as hubs or media nodes

These extensions are planned or only partially scaffolded in the codebase; they
are not presented here as completed experimental results.

## Documentation
- [`docs/01_problem_definition.md`](docs/01_problem_definition.md)
- [`docs/02_model_description.md`](docs/02_model_description.md)
- [`docs/03_assumptions.md`](docs/03_assumptions.md)
- [`docs/04_method.md`](docs/04_method.md)
- [`docs/05_results.md`](docs/05_results.md)
- [`docs/06_limitations.md`](docs/06_limitations.md)
