# Axelrod Model Q-Sweep Simulations
# Fixed F = 5, sweep q/n_traits = [3, 5, 10, 20]
# Topologies: lattice, ER, scale-free, complete
# Outputs:
#   axelrod_q_sweep_full_log.csv
#   axelrod_q_sweep_quantile_summary.csv

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import random as rd
import copy
from collections import Counter
import csv
import pandas as pd


def run_simulation(
        topology, n_traits, n_features, grid_x, grid_y, N,
        avg_k_target, t_max, seed, experiment):

    # Seed RNG
    rd.seed(seed)

    # Graph creation
    G, pos, is_lattice = create_graph(
        topology=topology,
        N=N,
        avg_k=avg_k_target,
        grid_x=grid_x,
        grid_y=grid_y,
        seed=seed
    )

    N_actual = G.number_of_nodes()

    # Random Axelrod initialisation
    trait_min = 0
    trait_max = n_traits - 1

    features = {
        u: [rd.randint(trait_min, trait_max) for _ in range(n_features)]
        for u in G.nodes
    }

    initial_features = copy.deepcopy(features)

    # Non-isolated nodes only, to avoid selecting a node with no neighbours
    non_isolated_nodes = [node for node in G.nodes() if G.degree(node) > 0]

    if len(non_isolated_nodes) == 0:
        raise ValueError("Graph has no non-isolated nodes.")

    # Run model loop
    for interaction in range(1, t_max + 1):
        # Pick a node and one of its neighbours at random
        u = rd.choice(non_isolated_nodes)
        v = rd.choice(list(nx.neighbors(G, u)))

        # Compute common features and index of non-common ones
        f_u, f_v = features[u], features[v]

        if f_u != f_v:
            non_common_index = [
                i for i, pair in enumerate(zip(f_u, f_v))
                if pair[0] != pair[1]
            ]

            common = (n_features - len(non_common_index)) / n_features

            # With probability common, copy one differing feature from v to u
            if rd.random() <= common:
                feature_to_change = rd.choice(non_common_index)
                features[u][feature_to_change] = f_v[feature_to_change]

        # Check frozen state every N_actual interactions
        if interaction % N_actual == 0 and is_frozen(G, features, n_features):
            break

    frozen_step = interaction

    # Output values of interest
    final_unique_cultures = count_unique_cultures(features)
    initial_unique_cultures = count_unique_cultures(initial_features)
    avg_degree = sum(dict(G.degree()).values()) / G.number_of_nodes()
    isolates = list(nx.isolates(G))

    results = {
        "experiment": experiment,
        "script": "axelrod_q_sweep",
        "seed": seed,
        "topology": topology,
        "grid_x": grid_x,
        "grid_y": grid_y,
        "N": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "avg_degree": avg_degree,
        "avg_k_target": avg_k_target,
        "n_features": n_features,
        "n_traits": n_traits,
        "t_max": t_max,
        "isolated_nodes": len(isolates),
        "initial_unique_cultures": initial_unique_cultures,
        "final_unique_cultures": final_unique_cultures,
        "frozen_step": frozen_step,
        "frozen": is_frozen(G, features, n_features)
    }

    return results


def create_graph(topology, N=100, avg_k=4, grid_x=10, grid_y=10, seed=None):
    match topology:
        case "lattice":
            G = nx.grid_2d_graph(grid_x, grid_y)
            pos = {node: node for node in G.nodes()}
            is_lattice = True

        case "er":
            p = avg_k / (N - 1)
            G = nx.erdos_renyi_graph(N, p, seed=seed)
            pos = nx.spring_layout(G, seed=seed)
            is_lattice = False

        case "complete":
            G = nx.complete_graph(N)
            pos = nx.spring_layout(G, seed=seed)
            is_lattice = False

        case "scale_free":
            m = avg_k // 2
            G = nx.barabasi_albert_graph(N, m, seed=seed)
            pos = nx.spring_layout(G, seed=seed)
            is_lattice = False

        case _:
            raise ValueError(f"Unknown topology: {topology}")

    return G, pos, is_lattice


def is_frozen(G, features, n_features):
    for u, v in G.edges():
        overlap = sum(1 for i in range(n_features) if features[u][i] == features[v][i])
        if 0 < overlap < n_features:
            return False
    return True


def count_unique_cultures(features):
    culture_counts = Counter(tuple(v) for v in features.values())
    return len(culture_counts)


def plot_state(G, features, pos, is_lattice, title, grid_x=10, grid_y=10):
    unique_cultures = list(set(tuple(f) for f in features.values()))
    culture_index = {c: i for i, c in enumerate(unique_cultures)}

    if is_lattice:
        grid_labels = np.zeros((grid_x, grid_y))

        for node in G.nodes():
            x, y = node
            grid_labels[x, y] = culture_index[tuple(features[node])]

        plt.figure(figsize=(8, 8))
        plt.imshow(grid_labels.T, cmap=plt.cm.tab20, interpolation="nearest")
        plt.title(title)
        plt.axis("off")
        plt.show()

    else:
        node_colours = [culture_index[tuple(features[node])] for node in G.nodes()]

        plt.figure(figsize=(8, 8))
        nx.draw_networkx_nodes(G, pos, node_color=node_colours, cmap=plt.cm.tab20, node_size=80)
        nx.draw_networkx_edges(G, pos, edge_color="lightgray", width=0.5)
        plt.title(title)
        plt.axis("off")
        plt.show()


# Experiment block: Q-sweep

grid_x = 10
grid_y = 10
N = 100
n_features = 5          # fixed F
q_values = [3, 5, 10, 20]
t_max = 200000
avg_k_target = 4
experiment = "q_sweep"

topologies = ["lattice", "er", "scale_free", "complete"]
seeds = range(200)

filename = "axelrod_q_sweep_full_log.csv"

total_runs = len(topologies) * len(q_values) * len(seeds)
run_number = 0

with open(filename, "w", newline="") as f:
    writer = None

    for topology in topologies:
        for q in q_values:
            for seed in seeds:
                run_number += 1

                results = run_simulation(
                    topology=topology,
                    n_traits=q,
                    n_features=n_features,
                    grid_x=grid_x,
                    grid_y=grid_y,
                    N=N,
                    avg_k_target=avg_k_target,
                    t_max=t_max,
                    seed=seed,
                    experiment=experiment
                )

                if writer is None:
                    writer = csv.DictWriter(f, fieldnames=results.keys())
                    writer.writeheader()

                writer.writerow(results)

                print(
                    f"Run {run_number}/{total_runs} complete | "
                    f"topology={topology}, q={q}, seed={seed}, "
                    f"final cultures={results['final_unique_cultures']}, "
                    f"frozen step={results['frozen_step']}"
                )


# Create plot-ready quantile summary

df = pd.read_csv(filename)

summary = (
    df.groupby(["topology", "n_features", "n_traits"])
      .agg(
          final_unique_cultures_median=("final_unique_cultures", "median"),
          final_unique_cultures_q025=("final_unique_cultures", lambda x: x.quantile(0.025)),
          final_unique_cultures_q975=("final_unique_cultures", lambda x: x.quantile(0.975)),

          frozen_step_median=("frozen_step", "median"),
          frozen_step_q025=("frozen_step", lambda x: x.quantile(0.025)),
          frozen_step_q975=("frozen_step", lambda x: x.quantile(0.975)),

          initial_unique_cultures_median=("initial_unique_cultures", "median"),
          initial_unique_cultures_q025=("initial_unique_cultures", lambda x: x.quantile(0.025)),
          initial_unique_cultures_q975=("initial_unique_cultures", lambda x: x.quantile(0.975)),

          frozen_rate=("frozen", "mean"),
          isolated_nodes_mean=("isolated_nodes", "mean"),
      )
      .reset_index()
)

summary.to_csv("axelrod_q_sweep_quantile_summary.csv", index=False)

print("\nSaved full log to axelrod_q_sweep_full_log.csv")
print("Saved plot-ready quantile summary to axelrod_q_sweep_quantile_summary.csv")
print(summary)
