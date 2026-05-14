# Research Roadmap

## Stage 1: Classical Axelrod Baseline
- **Objective:** Establish a clean and reproducible baseline implementation of
  the classical Axelrod cultural dissemination model.
- **Model changes:** None beyond packaging, path handling, and light research
  workflow support.
- **Expected outputs:** Baseline figures, model description, and a stable run
  command.
- **Success criteria:** Baseline model runs reproducibly and produces the
  current standard outputs.
- **Status:** Complete

## Stage 2: Parameter Sensitivity Analysis
- **Objective:** Test how outcomes vary with key baseline parameters such as
  population size, number of features, number of traits, random seed, and run
  length.
- **Model changes:** Add experiment runners and summary metrics without
  changing the baseline interaction rule.
- **Expected outputs:** Parameter sweep tables, repeated-run summaries, and
  plots comparing fragmentation or convergence across settings.
- **Success criteria:** Repeated baseline experiments can be compared
  systematically across parameter settings.
- **Status:** In progress

## Stage 3: Network Topology Extension
- **Objective:** Replace or generalise the lattice neighbourhood structure to
  study how topology changes convergence and fragmentation.
- **Model changes:** Add graph-based interaction structures such as random,
  small-world, or scale-free networks.
- **Expected outputs:** Comparative figures and metrics for lattice versus
  alternative network structures.
- **Success criteria:** The model can run on at least one alternative topology
  while preserving the baseline rule logic.
- **Status:** Planned

## Stage 4: Immigration/Integration Extension
- **Objective:** Study how immigration or replacement dynamics affect cultural
  diversity, assimilation, and fragmentation.
- **Model changes:** Introduce entry or replacement mechanisms for agents and
  define how those agents interact with the existing population.
- **Expected outputs:** Comparative runs showing how inflow timing, scale, or
  placement affect system outcomes.
- **Success criteria:** Immigration scenarios can be simulated and assessed
  with baseline-compatible metrics.
- **Status:** Planned

## Stage 5: Creator-Consumer Influence Extension
- **Objective:** Explore whether asymmetric influence between creators and
  consumers changes the dynamics of convergence and polarisation.
- **Model changes:** Distinguish creator and consumer roles and define a
  non-symmetric exposure or influence mechanism.
- **Expected outputs:** Comparative experiments showing how creator influence
  changes alignment, clustering, or fragmentation.
- **Success criteria:** A creator-consumer model variant runs and can be
  compared against the baseline and network variants.
- **Status:** Planned

## Stage 6: Comparative Analysis and Dissertation Figures
- **Objective:** Bring together results from the baseline and extensions into a
  coherent comparative analysis suitable for dissertation writing.
- **Model changes:** No major rule changes; emphasis shifts to analysis,
  synthesis, and presentation.
- **Expected outputs:** Dissertation-ready tables, figures, and interpretation
  notes.
- **Success criteria:** Results are organised clearly enough to support the MSc
  dissertation and presentation.
- **Status:** Planned
