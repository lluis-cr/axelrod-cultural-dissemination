# Method

## Modelling Approach
This repository uses agent-based modelling to study cultural dissemination.
The baseline model is implemented in Python and run through scripted examples
and notebooks.

## Baseline Workflow
1. Initialise a population on a square grid.
2. Assign random cultural vectors to each agent.
3. Run asynchronous Axelrod updates for a fixed number of steps or until no
   active edges remain.
4. Save summary figures showing the initial condition, final cultural domains,
   and active-edge trajectory.

## Planned Experimental Workflow
As the repository expands, experiments should be run in repeated batches across
different parameter settings:

- population size `N`,
- number of cultural features `F`,
- number of trait values `q`,
- random seed,
- topology,
- immigration intensity,
- creator-consumer influence parameters.

## Analysis Targets
Core outputs for comparison across runs include:

- number of cultural domains,
- size of the largest domain,
- pairwise similarity,
- cultural entropy,
- active-edge persistence,
- integration and polarisation metrics for extended models.
