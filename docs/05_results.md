# Results

## Baseline Results Interpretation

The baseline run uses a two-dimensional Axelrod model where each grid cell is
an agent, each agent has several cultural features, and interaction is more
likely between agents that already share some cultural traits.

The initial feature plot shows one cultural feature before interaction. It is
mostly random because each agent is initialised independently. This is the
starting condition before social influence has had time to create spatial
structure.

The final cultural-domain plot shows the full cultural vector of each agent
after many update steps. Instead of random noise, the grid now contains larger
patches. These patches are cultural domains: neighbouring agents that have
become culturally identical or very similar through repeated interaction.

The activity plot counts active edges: neighbouring pairs that are neither
completely different nor completely identical. These are the pairs that can
still interact under Axelrod's rules. In a fully frozen run, this count should
fall to zero. The current run does not reach zero by the end of the plotted
simulation; activity initially falls, then rises again. This means the model
has not yet reached an absorbing frozen state within the current run length.

## How to Read This Substantively

The baseline already shows the core Axelrod mechanism:

- Local social influence creates visible cultural domains from random initial
  conditions.
- The system does not necessarily converge to one global culture.
- Cultural fragmentation can persist even without explicit hostility,
  immigration, media, or network polarisation.
- The final state depends on parameters such as grid size, number of cultural
  features, number of possible traits, random seed, and run length.

The non-zero and rising active-edge curve should be treated as a prompt for
more systematic experimentation. It may indicate that the run was stopped too
early, that the chosen parameter regime has long transient dynamics, or that
single-run plots are too noisy to interpret without repeated runs.

## Baseline Concepts to Understand First

- Absorbing state: a state where no further cultural updates can occur.
- Active edge: a neighbour pair with partial similarity, meaning they can still
  interact.
- Cultural domain: a group of agents sharing the same full cultural vector.
- Monoculture: all agents converge to one shared culture.
- Fragmentation: multiple distinct cultural domains remain.
- Homophily: similarity increases the probability of interaction.
- Social influence: interaction makes agents more similar.
- Parameter sensitivity: outcomes depend on `N`, `F`, `q`, random seed, and
  stopping rules.
- Phase transition: Axelrod models often show a shift between convergence and
  fragmentation as cultural diversity increases.

## Useful Foundational Exercises

1. Run the same parameters across many random seeds and compare average
   outcomes.
2. Sweep `q`, the number of possible traits, and measure when the system shifts
   from convergence to fragmentation.
3. Sweep `F`, the number of cultural features, and measure how dimensionality
   affects interaction.
4. Compare open boundaries with periodic boundaries.
5. Track the number of cultural domains over time.
6. Track the largest cultural domain share over time.
7. Compare final-state diversity using entropy or pairwise similarity.
8. Run until active edges reach zero, then compare frozen states.

## Pivot Toward Networks

The right pivot point is after the baseline has reusable metrics and repeated
runs. The model can then move from a fixed grid-neighbourhood assumption to a
general graph where nodes are agents and edges are possible interactions.

A practical sequence is:

1. Refactor the baseline model so plotting is separate from model logic.
2. Add metrics for domains, diversity, largest-domain share, and active edges.
3. Reproduce baseline grid results using those metrics.
4. Implement graph-based neighbours in `src/axelrod/network.py`.
5. Compare grid, random, small-world, and scale-free networks.
6. Visualise networks with node colours representing cultural states.
7. Use those network tools as the base for creator-consumer influence and
   immigration/integration experiments.

The network pivot should happen before the full immigration and creator-consumer
extensions, because both extensions depend on the ability to represent non-grid
social structures.
