# Model Description

## Baseline Agents
Each agent is represented by a vector of `F` cultural features. Each feature
takes one of `q` discrete trait values.

## Interaction Rule
At each asynchronous update:

1. Select one focal agent at random.
2. Select one neighbour at random.
3. Compute similarity as the fraction of matching features.
4. If similarity is strictly between 0 and 1, allow interaction with
   probability equal to similarity.
5. When interaction occurs, copy one differing trait from the neighbour into
   the focal agent.

## Spatial Structure
The current baseline uses a two-dimensional square grid with a Von Neumann
neighbourhood and open boundaries.

## Outputs
The baseline implementation currently exposes:

- feature-grid visualisation,
- cultural-domain labels,
- active-edge counts over time,
- saved figures for the initial state, final domains, and activity history.

## Planned Extensions
- network-based interaction beyond fixed lattice neighbours,
- immigration and integration dynamics,
- creator-consumer influence with asymmetric exposure.
