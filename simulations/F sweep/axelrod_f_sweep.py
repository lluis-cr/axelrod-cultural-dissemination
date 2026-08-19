# Axelrod Model F-sweep Simulations
# Separate clean copy for the F-sweep experiment.
# Fixed q = n_traits = 5, sweep F = n_features across topologies.

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import random as rd
import copy
from collections import Counter
import csv
import pandas as pd


def run_simulation(topology, n_traits, n_features, grid_x, grid_y, N,
                   avg_k_target, t_max, seed, experiment):
    rd.seed(seed)

    G, pos, is_lattice = create_graph(
        topology=topology,
        N=N,
        avg_k=avg_k_target,
        grid_x=grid_x,
        grid_y=grid_y,
        seed=seed
    )

    N_actual = G.number_of_nodes()

    trait_min = 0
    trait_max = n_traits - 1

    features = {
        u: [rd.randint(trait_min, trait_max) for _ in range(n_features)]
        for u in G.nodes
    }

    initial_features = copy.deepcopy(features)

    non_isolated_nodes = [node for node in G.nodes() if G.degree(node) > 0]

    if len(non_isolated_nodes) == 0:
        raise ValueError("Graph has no non-isolated nodes.")

    for interaction in range(1, t_max + 1):
        u = rd.choice(non_isolated_nodes)
        v = rd.choice(list(nx.neighbors(G, u)))

        f_u, f_v = features[u], features[v]

        if f_u != f_v:
            non_common_index = [
                i for i, pair in enumerate(zip(f_u, f_v))
                if pair[0] != pair[1]
            ]

            common = (n_features - len(non_common_index)) / n_features

            if rd.random() <= common:
                feature_to_change = rd.choice(non_common_index)
                features[u][feature_to_change] = f_v[feature_to_change]

        if interaction % N_actual == 0 and is_frozen(G, features, n_features):
            break

    frozen_step = interaction

    final_unique_cultures = count_unique_cultures(features)
    initial_unique_cultures = count_unique_cultures(initial_features)
    avg_degree = sum(dict(G.degree()).values()) / G.number_of_nodes()
    isolates = list(nx.isolates(G))

    results = {
        "experiment": experiment,
        "script": "axelrod_f_sweep",
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
        "frozen": is_frozen(G, features, n_features),
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


def main():
    grid_x = 10
    grid_y = 10
    N = 100
    n_traits = 5
    t_max = 200000
    avg_k_target = 4
    experiment = "f_sweep"

    topologies = ["lattice", "er", "scale_free", "complete"]
    f_values = [3, 5, 10, 20]
    seeds = range(200)

    filename = "axelrod_f_sweep_full_log.csv"
    total_runs = len(topologies) * len(f_values) * len(seeds)
    run_number = 0

    with open(filename, "w", newline="") as csvfile:
        writer = None

        for topology in topologies:
            for F in f_values:
                for seed in seeds:
                    run_number += 1

                    results = run_simulation(
                        topology=topology,
                        n_traits=n_traits,
                        n_features=F,
                        grid_x=grid_x,
                        grid_y=grid_y,
                        N=N,
                        avg_k_target=avg_k_target,
                        t_max=t_max,
                        seed=seed,
                        experiment=experiment
                    )

                    if writer is None:
                        writer = csv.DictWriter(csvfile, fieldnames=results.keys())
                        writer.writeheader()

                    writer.writerow(results)

                    print(
                        f"Run {run_number}/{total_runs} complete | "
                        f"topology={topology}, F={F}, seed={seed}, "
                        f"final cultures={results['final_unique_cultures']}, "
                        f"frozen step={results['frozen_step']}, "
                        f"frozen={results['frozen']}"
                    )

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
          )
          .reset_index()
    )

    summary.to_csv("axelrod_f_sweep_quantile_summary.csv", index=False)

    print("\nSaved full log to axelrod_f_sweep_full_log.csv")
    print("Saved plot-ready quantile summary to axelrod_f_sweep_quantile_summary.csv")
    print(summary)


if __name__ == "__main__":
    main()
